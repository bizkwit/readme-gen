from typing import Literal
import google.generativeai as client
from google.generativeai.types import GenerationConfig
import os
from dotenv import load_dotenv

from utils import get_file_path

load_dotenv()

SYSTEM_INSTRUCTION = "You are a helpful assistant that generates README file for github projects."


def init_model(llm_type:Literal['google-gemini'], api_key:str):
    if llm_type == 'google-gemini':
        client.configure(api_key=api_key)
        MODEL = client.GenerativeModel(
            model_name="gemini-1.5-flash", 
            system_instruction=SYSTEM_INSTRUCTION
        )
        GENERATION_CONFIG = GenerationConfig(
            temperature=0.7,
            max_output_tokens=8192
        )
    return MODEL, GENERATION_CONFIG

def generate_readme(
    llm_dropdown:str,
    api_key:str,
    user_name:str,
    repo_name:str,
    project_description:str,
    code_content:dict
)->str:
    """
    Generates a README file based on the given project description and code content.

    Args:
        user_name (str): The username of the github user.
        repo_name (str): The name of the github repository.
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

    prompt += f"""

    Based on the project description and the provided code, generate a detailed README.md file.
    The README should include the following sections (if applicable):

    - Project shields
    - Project Title
    - Overview/Introduction
    - Table of Contents
    - Features
    - Technologies (include icons is possible)
    - Getting Started (Installation, Prerequisites, Usage)
    - Examples (if relevant)
    - Roadmap (with checkboxes for completed tasks)
    - API Reference (if it's a library or has an API)
    - Contributing
    - License
    - Acknowledgements (if applicable)

    here is the repo name: {repo_name}
    here is the user name: {user_name}
    Be clear, concise, and informative. Use markdown formatting.
    """

    try:
        MODEL, GENERATION_CONFIG = init_model(llm_dropdown, api_key)
        response = MODEL.generate_content(prompt, generation_config=GENERATION_CONFIG)
        print(response.text)
        return response.text.strip('```markdown\n').strip('```')
    except Exception as e:
        return f"Error generating README: {e}"
