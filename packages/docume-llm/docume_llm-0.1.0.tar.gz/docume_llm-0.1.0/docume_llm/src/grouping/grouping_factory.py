from docume_llm.src.utils.config import ApplicationType
from docume_llm.src.jira.grouping import group_documents

def get_grouping_func(app_type):
    
    if app_type==ApplicationType.JIRA.value:
        return group_documents
    