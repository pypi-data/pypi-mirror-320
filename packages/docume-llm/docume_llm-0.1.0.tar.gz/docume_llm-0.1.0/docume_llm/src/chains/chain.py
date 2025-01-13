from langchain.text_splitter import RecursiveCharacterTextSplitter
import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from typing_extensions import TypedDict, Annotated, List
import operator


def chain_documents(documents, queries, llm, embeddings, filterType = "comment"):
    print('Running chain')
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separators=["}","\n\n", "\n", " ", ""]
    )
    
    docs = text_splitter.split_documents(documents)
    # Pass the documents and embeddings inorder to create FAISS vector index
    vectorindex_openai = FAISS.from_documents(docs, embeddings)
    retriever = vectorindex_openai.as_retriever()
    
    # IMP---- There might be an issue with the async call. 
    output = []
    for metadata, query in queries:
        docs = retriever.invoke(query, filter={'type': {"$in":metadata}})
        final = asyncio.run(run_query(llm, query, docs))
        output.append(final)
    return output

async def run_query(llm, query, docs):
    app = build_graph_chain(llm)
    async for step in app.astream(
        {"contents": [doc.page_content for doc in docs], "question": query},
        {"recursion_limit": 10},
    ):
        continue

    final = step.get("generate_final_summary").get("final_summary")
    return final


def build_graph_chain(llm):
    
    reduce_template = """
    The following is a set of summaries:
    {docs}
    Take these and distill it into a final, consolidated summary
    of the main themes.
    """

    map_template = "Write a concise summary of the following: {context} for the following {question}"


    map_prompt = ChatPromptTemplate([("human", map_template)])
    reduce_prompt = ChatPromptTemplate([("human", reduce_template)])

    map_chain = map_prompt | llm | StrOutputParser()
    reduce_chain = reduce_prompt | llm | StrOutputParser()

    # Graph components: define the components that will make up the graph


    # This will be the overall state of the main graph.
    # It will contain the input document contents, corresponding
    # summaries, and a final summary.
    class OverallState(TypedDict):
        # Notice here we use the operator.add
        # This is because we want combine all the summaries we generate
        # from individual nodes back into one list - this is essentially
        # the "reduce" part
        question: str
        contents: List[str]
        summaries: Annotated[list, operator.add]
        final_summary: str


    # This will be the state of the node that we will "map" all
    # documents to in order to generate summaries
    class SummaryState(TypedDict):
        content: str
        ques: str


    # Here we generate a summary, given a document
    async def generate_summary(state: SummaryState):
        print(state)
        response = await map_chain.ainvoke({"context": state["content"], "question": state["ques"]})
        return {"summaries": [response]}


    # Here we define the logic to map out over the documents
    # We will use this an edge in the graph
    def map_summaries(state: OverallState):
        # We will return a list of `Send` objects
        # Each `Send` object consists of the name of a node in the graph
        # as well as the state to send to that node
        return [
            Send("generate_summary", {"content": content, "ques": state["question"]}) for content in state["contents"]
        ]


    # Here we will generate the final summary
    async def generate_final_summary(state: OverallState):
        response = await reduce_chain.ainvoke(state["summaries"])
        return {"final_summary": response}


    # Construct the graph: here we put everything together to construct our graph
    graph = StateGraph(OverallState)
    graph.add_node("generate_summary", generate_summary)
    graph.add_node("generate_final_summary", generate_final_summary)
    graph.add_conditional_edges(START, map_summaries, ["generate_summary"])
    graph.add_edge("generate_summary", "generate_final_summary")
    graph.add_edge("generate_final_summary", END)
    app = graph.compile()
    
    return app