from typing import Optional
import gradio as gr
from utils import clone_repo_with_tempfile, get_file_path, read_code_files, cleanup
from llm import generate_readme, generate_readme_V2


def generate_readme_from_repo(
    repo_url:str, 
    project_description:str, 
    access_token:Optional[str]=None
) -> str:
    """Main function to orchestrate the README generation process."""
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    user_name = repo_url.split('/')[-2]
    local_repo_dir = get_file_path(f"temp_{repo_name}")

    temp_dir = clone_repo_with_tempfile(repo_url, access_token)
    code_content = read_code_files(temp_dir.name)
    if not code_content:
        cleanup(local_repo_dir)
        return "No code files found in the repository.", ""


    readme_content = generate_readme_V2(
        user_name,
        repo_name, 
        project_description, 
        code_content
    )

    temp_dir.cleanup()
    return "README Generation Complete!", readme_content if readme_content else "Failed to generate README."

with gr.Blocks() as demo:
    gr.Markdown("# GitHub README Generator")
    gr.Markdown("Enter the GitHub repository URL and a brief description of your project to generate a README file using an LLM.")

    with gr.Column():
        repo_url_input = gr.Textbox(label="GitHub Repository URL")
        project_description_input = gr.Textbox(label="Project Description")
        with gr.Accordion("Personal Access Token (for private repos)", open=False):
            gr.Markdown(
                """
                To generate a README for a private repository, you need to provide a Personal Access Token (PAT) from GitHub.

                **How to create a Personal Access Token:**

                1. Go to your GitHub profile settings: [https://github.com/settings/profile](https://github.com/settings/profile)
                2. Click on "Developer settings" in the sidebar.
                3. Click on "Personal access tokens" -> "Tokens (classic)".
                4. Click on "Generate new token" -> "Generate new token (classic)".
                5. Give your token a descriptive name (e.g., "README Generator").
                6. **Select the `repo` scope** (this is necessary to clone private repositories).
                7. Click "Generate token" at the bottom.
                8. **Copy the generated token.** This is the value you need to paste below.

                **Important Security Note:** Treat your PAT like a password. Do not share it publicly or commit it to your repository.
                """
            )
            access_token_input = gr.Textbox(label="Personal Access Token", type="password")
        with gr.Row():
            generate_button = gr.Button("Generate README")
            clear_button = gr.Button("Clear", variant="secondary")

    status_output = gr.Label(label="Status")
    readme_output = gr.Markdown(label="Generated README")

    clear_button.click(
        fn=lambda: [None]*5,
        inputs=[],
        outputs=[
            repo_url_input, 
            project_description_input, 
            access_token_input, 
            status_output, 
            readme_output
        ]
    )

    generate_button.click(
        fn=generate_readme_from_repo,
        inputs=[
            repo_url_input, 
            project_description_input, 
            access_token_input
        ],
        outputs=[
            status_output, 
            readme_output
        ]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )