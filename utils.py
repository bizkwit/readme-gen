import os
import shutil
import subprocess
import tempfile
from typing import Optional

def get_file_path(file_name:str) -> str:
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        file_name
    )

def clone_repo(repo_url, local_dir, access_token=None):
    """Clones a GitHub repository to a local directory, handling private repos."""
    try:
        clone_command = ["git", "clone"]
        if access_token:
            # Modify the URL to include the access token for HTTPS authentication
            parts = repo_url.split("//")
            authenticated_url = f"{parts[0]}//{access_token}@{parts[1]}"
            clone_command.append(authenticated_url)
        else:
            clone_command.append(repo_url)
        clone_command.append(local_dir)

        subprocess.run(clone_command, check=True, capture_output=True)
        return f"Repository cloned to {local_dir}"
    except subprocess.CalledProcessError as e:
        error_message = f"Error cloning repository: {e}\n{e.stderr.decode()}"
        return error_message
    except Exception as e:
        return f"An unexpected error occurred during cloning: {e}"

def clone_repo_with_tempfile(
    repo_url:str,
    access_token:Optional[str]=None
)-> tempfile.TemporaryDirectory:
    """Clones a GitHub repository to a local directory, handling private repos."""
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
        clone_command.append(temp_dir)

        subprocess.run(clone_command, check=True, capture_output=True)
        return temp_dir
    
    except subprocess.CalledProcessError as e:
        error_message = f"Error cloning repository: {e}\n{e.stderr.decode()}"
        return error_message
    
    except Exception as e:
        return f"An unexpected error occurred during cloning: {e}"

def read_code_files(repo_dir, allowed_extensions=('.py', '.js', '.java', '.c', '.cpp', '.go', '.sh')):
    """Reads the content of code files within the repository."""
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