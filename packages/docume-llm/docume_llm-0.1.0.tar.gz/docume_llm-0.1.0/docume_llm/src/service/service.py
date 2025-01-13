from docume_llm.src.preprocess.preprocess_factory import get_preprocess_func
from docume_llm.src.chains.loader.custom_json_loader import load_into_documents
from docume_llm.src.grouping.grouping_factory import get_grouping_func
from docume_llm.src.utils.llm_model import setup_llm_model
from dotenv import load_dotenv
from docume_llm.src.chains.chain import chain_documents
from docume_llm.src.utils.config import Query
from docume_llm.src.validators.doc_validator import validate_doc_input
import os

def generate_doc(json_data, **kwargs):
    validate_doc_input(**kwargs)
    
    app_type = kwargs.get('app_type')
    
    json_data = preprocess(json_data, app_type)
    documents = load_documents(json_data, app_type)
    llm_model, embedding_object = llm_configuration(model_type = kwargs.get('llm_type'), api_key = kwargs.get('api_key'))
    queries = get_queries()
    answers = chain_documents(documents, queries, llm_model, embedding_object)
    return queries, answers
    
    
    
def preprocess(json_data, app_type):
    preprocess_func = get_preprocess_func(app_type)
    return preprocess_func(json_data)



def load_documents(json_data, app_type):
    grouping_func = get_grouping_func(app_type)
    documents = load_into_documents(json_data, app_type, grouping_func)
    return documents

def llm_configuration(model_type, api_key):
    llm, embeddings = setup_llm_model(model_type, api_key=api_key)
    return llm, embeddings
    
def get_queries():
    return zip(Query.metadata_for_query, Query.queries)
    


    