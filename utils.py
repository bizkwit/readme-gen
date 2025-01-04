import os
import shutil
import subprocess
import tempfile
from typing import Optional

TITLE_HTML = """
    <style>
    .row{
        display: flex;
    }
    .flex-grow{
        flex-grow: 1;
    }
    .title-container{
        display: flex;
        border-radius: .5em;
    }
    .logo-img{
        align-items: center;
        display: flex;
        padding: 1em 0;
        width: 70px;
        height:70px;
    }
    .text-data{
        display: flex;
        flex-direction: column;
        justify-content: center;
        font-weight: bold;
        font-size: 18px;
    }
    </style>
    <div class="title-container">
        <div class="logo-img">
            <svg xmlns="http://www.w3.org/2000/svg"  fill="currentColor" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M14 4.5V14a2 2 0 0 1-2 2H9v-1h3a1 1 0 0 0 1-1V4.5h-2A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v9H2V2a2 2 0 0 1 2-2h5.5zM.706 13.189v2.66H0V11.85h.806l1.14 2.596h.026l1.14-2.596h.8v3.999h-.716v-2.66h-.038l-.946 2.159h-.516l-.952-2.16H.706Zm3.919 2.66V11.85h1.459q.609 0 1.005.234t.589.68q.195.445.196 1.075 0 .634-.196 1.084-.197.451-.595.689-.396.237-1 .237H4.626Zm1.353-3.354h-.562v2.707h.562q.279 0 .484-.082a.8.8 0 0 0 .334-.252 1.1 1.1 0 0 0 .196-.422q.067-.252.067-.592a2.1 2.1 0 0 0-.117-.753.9.9 0 0 0-.354-.454q-.238-.152-.61-.152"/>
            </svg>
        </div>
        <div class="text-data">
            <h1>README Generator</h1>
        </div>
    </div>
"""
INIT_CSS = """
    footer{
        visibility: hidden;
    }
    .clear-button{
        color:#fff;
        font-wheight: bold;
        background-color: rgba(228,119,109,1);
    }
    .clear-button:hover{
        background-color: #eb675e;
    }
    .right-container{
        align-content: end;
    }
    .api-button{
        font-size: 13px;
        color:#505739;
        width: 100px;
        font-weight: bold;
        border: 2px 15px #333029;
        box-shadow: 0px 1px 0px 0px #1c1b18;
        text-shadow: 0px 1px 0px #ffffff;
        background: linear-gradient(#eae0c2,#ccc2a6);
    }
    .api-button:hover{
        background: linear-gradient(#ccc2a6, #eae0c2);
    }
"""

def get_file_path(file_name:str) -> str:
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        file_name
    )

def clone_repo_with_tempfile(
    repo_url:str,
    access_token:Optional[str]=None
)-> tempfile.TemporaryDirectory:
    """Clone a GitHub repository to a temporary directory, handling private repos.

    Args:
        repo_url (str): URL of the GitHub repository to clone.
        access_token (Optional[str]): GitHub access token for private repositories.

    Returns:
        tempfile.TemporaryDirectory: Temporary directory containing the cloned repository.
    """
    try:
        temp_dir = tempfile.TemporaryDirectory()
        clone_command = ["git", "clone"]
        if access_token:
            # Modify the URL to include the access token for HTTPS authentication
            parts = repo_url.split("//")
            authenticated_url = f"{parts[0]}//{access_token}@{parts[1]}"
            clone_command.append(authenticated_url)
        else:
            clone_command.append(repo_url)
        clone_command.append(temp_dir.name)

        subprocess.run(clone_command, check=True, capture_output=True)
        return temp_dir
    
    except subprocess.CalledProcessError as e:
        error_message = f"Error cloning repository: {e}\n{e.stderr.decode()}"
        return error_message
    
    except Exception as e:
        return f"An unexpected error occurred during cloning: {e}"

def read_code_files(
    repo_dir:str, 
    allowed_extensions:tuple=('.py', '.js', '.java', '.c', '.cpp', '.go', '.sh')
) -> dict:
    """Read all code files in the given repository directory, filtering by extension.

    Args:
        repo_dir (str): Path to the local repository directory.
        allowed_extensions (tuple, optional): Extensions to include. Defaults to ('.py', '.js', '.java', '.c', '.cpp', '.go', '.sh').

    Returns:
        dict: Mapping of file names to their contents.
    """
    code_content = {}
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith(allowed_extensions):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        code_content[file] = f.read()
                except UnicodeDecodeError:
                    print(f"Skipping file {file}: Could not decode content.")
                except Exception as e:
                    print(f"Error reading file {file}: {e}")
    return code_content


def cleanup(local_dir):
    """Deletes the locally cloned repository."""
    print(f"Cleaning up: {local_dir}")
    try:
        shutil.rmtree(local_dir)
        print(f"Cleaned up: Removed {local_dir}")
        return f"Cleaned up: Removed {local_dir}"
    except Exception as e:
        return f"Error cleaning up: {e}"