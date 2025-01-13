from docume_llm.src.utils.config import LLMModelType
from langchain_openai import OpenAI
from langchain_openai import OpenAIEmbeddings

def setup_llm_model(llm_model_type, **kwargs):
    
    if llm_model_type == LLMModelType.OPENAI.value:
        api_key = kwargs.get('api_key')
        llm = build_openai_model(api_key)
        embeddings = build_openai_embeddings(api_key)
        return llm, embeddings
    
    
    
def build_openai_model(api_key):
    llm = OpenAI(temperature=0.1, max_tokens=2048, openai_api_key=api_key)
    return llm


def build_openai_embeddings(api_key):
    return OpenAIEmbeddings(openai_api_key=api_key)