import google.generativeai as client
from google.generativeai.types import GenerationConfig
import os
from dotenv import load_dotenv

from utils import get_file_path

load_dotenv()

client.configure(api_key=os.getenv("GOOGLE_API_KEY"))
SYSTEM_INSTRUCTION = "You are a helpful assistant that generates README file for github projects."

MODEL = client.GenerativeModel(
    model_name="gemini-1.5-flash", 
    system_instruction=SYSTEM_INSTRUCTION
)

GENERATION_CONFIG = GenerationConfig(
    temperature=0.7,
    max_output_tokens=8192
)



def generate_readme(project_description:str, code_content:dict)->str:
    """
    Generates a README file based on the given project description and code content.

    Args:
        project_description (str): A brief description of the project.
        code_content (dict): A dictionary mapping filenames to their contents.

    Returns:
        str: The generated README content.
    """

    prompt = f"""
    You are an expert at generating comprehensive and informative README files for GitHub projects.

    Project Description:
    {project_description}

    Here is the code from the project (filenames are included):
    """

    for filename, content in code_content.items():
        prompt += f"\n--- {filename} ---\n{content}\n"

    prompt += """

    Based on the project description and the provided code, generate a detailed README.md file.
    The README should include the following sections (if applicable):

    - Project Title
    - Overview/Introduction
    - Features
    - Getting Started (Installation, Prerequisites, Usage)
    - Examples (if relevant)
    - API Reference (if it's a library or has an API)
    - Contributing
    - License
    - Acknowledgements (if applicable)

    Be clear, concise, and informative. Use markdown formatting.
    """

    try:
        response = MODEL.generate_content(prompt, generation_config=GENERATION_CONFIG)
        return response.text
    except Exception as e:
        return f"Error generating README: {e}"

def generate_readme_V2(
        user_name:str,
        repo_name:str,
        project_description:str, 
        code_content:dict
    )->str:
    """
    Generates a README file based on the given project description and code content.

    Args:
        project_description (str): A brief description of the project.
        code_content (dict): A dictionary mapping filenames to their contents.

    Returns:
        str: The generated README content.
    """

    template_path = get_file_path("README_TEMPLATE.md")
    with open(template_path, "r", encoding="utf-8") as f:
            readme_template = f.read()
    
    
    prompt = f"""
    You are an expert at generating comprehensive and informative README files for GitHub projects, and you strictly follow a provided template.

    **README Template:**
    ```markdown
    {readme_template}
    ```

    **Instructions:**
    - Carefully follow the structure and sections defined in the provided README template.
    - Replace the placeholder content in the template with information specific to the project.
    - Ensure all sections from the template are present in the generated README.
    - Pay attention to markdown formatting within the template and maintain it.
    - Populate the sections with details derived from the project description and the provided code.

    **Project Description:**
    {project_description}

    Here is the code from the project (filenames are included):
    """

    for filename, content in code_content.items():
        prompt += f"\n--- {filename} ---\n{content}\n"

    prompt += f"""
      update the links in the readme file with the following info:
      YOUR_USERNAME={user_name}
      YOUR_REPO_NAME={repo_name}  
      provide only the markdown and nothing else.
    """
    try:
        response = MODEL.generate_content(prompt, generation_config=GENERATION_CONFIG)
        print(response.text)
        return response.text.strip('```markdown\n').strip('```')
    except Exception as e:
        return f"Error generating README: {e}"