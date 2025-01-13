
# Project Name

## Setup Instructions

### Step 1: Create a `.env` File

```python
from docume_llm.main import generate_documentation
import json, os, re

file_path = "kan72.json"

with open(file_path, 'r') as file:
    json_data = json.load(file)
    
app_type = 'jira'
    
args = {
    'app_type': app_type,
    'llm_type': 'openai',
    'api_key': 'your-api-key-here'
}
    
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

queries, answers = generate_documentation(json_data, **args)

files = give_all_files_from_directory('.')
filename = give_next_filename(files)

with open(filename, "w") as file:
    for q,a in zip(queries, answers):
        file.write(q + "\n" + a + "\n\n")
        file.write("*" * 100)