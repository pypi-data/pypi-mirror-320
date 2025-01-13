import os, re
from docume_llm.src.utils.data import read_json_data
from docume_llm.src.service.service import generate_doc


def generate_documentation(json_data, **kwargs):
    return generate_doc(json_data, **kwargs)
    

def give_all_files_from_directory(directory):
    return os.listdir(directory)
    
def give_next_filename(files):
    # Regex pattern to match files with the base name and extension
    pattern = re.compile(rf"zero_shot_(\d+)\.txt")
    # Find all matching files and extract their numbers
    numbers = []
    for file in files:
        match = pattern.match(file)
        if match:
            numbers.append(int(match.group(1)))
    
    # Determine the next number
    if numbers:
        next_number = max(numbers) + 1
    else:
        next_number = 1
    return f"zero_shot_{next_number}.txt"
    
if __name__ == '__main__':
    file_path = '/home/b/bipinp/projects/docume_llm/docume_llm/kan72.json'
    json_data = read_json_data(file_path)
    app_type = 'jira'
    
    args = {
        'app_type': app_type,
        'llm_type': 'openai',
        'api_key': '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'
    }
    
    queries, answers = generate_documentation(json_data, **args)
    files = give_all_files_from_directory('.')
    filename = give_next_filename(files)
    
    with open(filename, "w") as file:
        for q,a in zip(queries, answers):
            file.write(q + "\n" + a + "\n\n")
            file.write("*"*100)
    