def group_documents(json_data):
    print('Running grouping')
    jsons = []
    metadatas = []
    
    comment = json_data['fields']['comment']
    if comment:
        jsons.append(comment)
        metadatas.append({'type': 'comment'})
        del json_data['fields']['comment']
    
    description = json_data['fields']['description']
    if description:
        jsons.append(description)
        metadatas.append({'type': 'description'})
        del json_data['fields']['description']
        
    acceptance_criteria = json_data['fields'].get('acceptance_criteria', None)
    if acceptance_criteria:
        jsons.append(acceptance_criteria)
        metadatas.append({'type': 'acceptance_criteria'})
        del json_data['fields']['acceptance_criteria']
    
    jsons.append(json_data)
    metadatas.append({"type": "story_info"})
    
    return jsons, metadatas