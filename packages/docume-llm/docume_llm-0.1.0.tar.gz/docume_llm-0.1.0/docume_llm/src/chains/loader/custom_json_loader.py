from langchain_community.document_loaders.base import BaseLoader
from langchain.schema import Document
import json

class CustomJSONLoader(BaseLoader):
    def __init__(self, json_data,  metadata, jq_schema="."):
        self.json_data = json_data
        self.jq_schema = jq_schema
        self.metadata = metadata

    def load(self):
        # Process the JSON data according to the jq_schema
        # For simplicity, we'll just return the JSON data as a Document
        
        return [Document(page_content=json.dumps(self.json_data), metadata=self.metadata)]
    
def load_into_documents(json_data, app_type, grouping_func):
    print('Running loader')
    grouped_jsons, metadatas = grouping_func(json_data)
    documents = []
    for js, metadata in zip(grouped_jsons, metadatas):
        loader = CustomJSONLoader(js, jq_schema=".", metadata=metadata)
        documents.extend(loader.load())
    return documents