from docume_llm.src.utils.config import ApplicationType, LLMModelType
def validate_doc_input(**kwargs):
    
    app_type = kwargs.get('app_type')
    application_types = [app.value for app in ApplicationType]
    if not app_type or app_type not in application_types:
        raise ValueError(f"Invalid application type. Supported types are {application_types}")
    
    
    llm_type = kwargs.get('llm_type')
    if not llm_type:
        raise ValueError("LLM model type is required")
    
    
    model_types = [model.value for model in LLMModelType]
    if llm_type not in model_types:
        raise ValueError(f"Invalid LLM model type. Supported types are {model_types}")
    
    
    if llm_type == LLMModelType.OPENAI.value:
        api_key = kwargs.get('api_key')
        if not api_key:
            raise ValueError("API key is required for OpenAI model")    
    return