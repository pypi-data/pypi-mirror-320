from docume_llm.src.utils.config import ApplicationType
from docume_llm.src.jira.preprocess_jira import preprocess_json_data

def get_preprocess_func(app_type):
    
    if app_type==ApplicationType.JIRA.value:
        return preprocess_json_data
    