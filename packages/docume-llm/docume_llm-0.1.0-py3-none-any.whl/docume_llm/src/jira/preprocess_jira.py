
def preprocess_json_data(json_data):
    print("Preprocessing JSON data in jira format")
    json_data = preprocess_comments(json_data)
    json_data = preprocess_descriptions(json_data)
    json_data = preprocess_acceptance_criteria(json_data)
    return json_data
    
    
def preprocess_comments(json_data):
    comment_section = json_data.get('fields').get('comment', None)
    if not comment_section: return json_data
    raw_comments = comment_section.get('comments', None)
    if raw_comments is None: return json_data
    formatted_comments = []
    for comment in raw_comments:
        formatted_comments.append(generate_content_for_comment(comment))
    json_data['fields']['comment']['comments'] = formatted_comments     
    return json_data


def preprocess_descriptions(json_data):
    description_section = json_data.get('fields').get('description', None)
    if description_section is None: return json_data
    descriptions = description_section.get('content', None)
    if descriptions is None: return json_data
    formatted_descriptions = []
    for description in descriptions:
        formatted_descriptions.append(generate_content_for_description(description))
    json_data['fields']['description'] = '\n'.join(formatted_descriptions)
    return json_data

def preprocess_acceptance_criteria(json_data):
    acceptance_criteria_section = json_data.get('fields').get('acceptance_criteria', None)
    if acceptance_criteria_section is None: return json_data
    acceptance_criteria = acceptance_criteria_section['content']
    if acceptance_criteria is None: return json_data
    formatted_acceptance_criteria = []
    for criterion in acceptance_criteria:
        formatted_acceptance_criteria.append(generate_content_for_description(criterion))
    json_data['fields']['acceptance_criteria'] = '\n'.join(formatted_acceptance_criteria)
    return json_data


def generate_content_for_comment(comment):
    author_name = comment['author']['displayName']
    text_elements = extract_text_elements(comment['body']['content'])
    return {
        'author_name': author_name,
        'text':'\n'.join(text_elements)
    }  
    
def generate_content_for_description(description):
    return get_extracted_texts_as_string(description['content'])


def generate_content_for_acceptance_criteria(acceptance_criteria):
    return get_extracted_texts_as_string(acceptance_criteria['content'])
    
def get_extracted_texts_as_string(content):
    text_elements = extract_text_elements(content)
    return '\n'.join(text_elements)    

def extract_text_elements(content):
    text_elements = []
    for item in content:
        if item['type'] == 'text':
            text_elements.append(item['text'])
        if 'content' in item:
            text_elements.extend(extract_text_elements(item['content']))
    return text_elements
    