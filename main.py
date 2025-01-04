import tempfile
from typing import Optional
import gradio as gr
from gradio_modal import Modal
from utils import (
    INIT_CSS,
    TITLE_HTML, 
    clone_repo_with_tempfile, 
    get_file_path, 
    read_code_files, 
    cleanup
)
from llm import generate_readme


def generate_readme_from_repo(
    llm_dropdown:str,
    api_key:str,
    repo_url:str, 
    project_description:str, 
    access_token:Optional[str]=None
) -> str:
    """Main function to orchestrate the README generation process."""
    
    print("LLM SELECTED: "  + llm_dropdown)
    print("API KEY: "  + api_key)

    repo_name = repo_url.split('/')[-1].replace('.git', '')
    user_name = repo_url.split('/')[-2]
    local_repo_dir = get_file_path(f"temp_{repo_name}")

    temp_dir = clone_repo_with_tempfile(repo_url, access_token)
    code_content = read_code_files(temp_dir.name)
    if not code_content:
        cleanup(local_repo_dir)
        return "No code files found in the repository.", ""

    readme_content = generate_readme(
        llm_dropdown,
        api_key,
        user_name,
        repo_name,
        project_description, 
        code_content
    )

    temp_dir.cleanup()
    if readme_content:
        # Save the readme content to a temporary file
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".md", delete=False) as tmp_file:
            tmp_file.write(readme_content)
            readme_file_path = tmp_file.name
        return "README Generation Complete!", readme_content, readme_file_path
    else:
        return "Failed to generate README.", "Failed to generate README.", None

with gr.Blocks(
    title="GitHub README Generator",
    # theme="bethecloud/storj_theme",
    css=INIT_CSS
) as demo:
    with Modal(visible=False) as modal:
        gr.Markdown("## LLM Config")

        llm_choices = ["google-gemini"] #TODO: add more llm options
        llm_dropdown = gr.Dropdown(
            label="LLM", 
            choices=llm_choices, 
            value=llm_choices[0]
        )

        llm_dropdown.change(fn=lambda x: x,inputs=llm_dropdown,outputs=llm_dropdown)
        api_key = gr.Textbox(label="API Key", type="password")
    with gr.Row():
        with gr.Column(scale=12):
            title = gr.HTML(TITLE_HTML)
            gr.Markdown("Enter the GitHub repository URL and a brief description of your project to generate a README file using an LLM.")
        with gr.Column(scale=1, elem_classes="right-container"):
            api_btn = gr.Button("LLM Config", elem_classes="api-button", size="sm")
            api_btn.click(
                fn=lambda: gr.update(visible=True),
                outputs=[modal]
            )
    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=500):
            with gr.Group():
                repo_url_input = gr.Textbox(label="GitHub Repository URL")
                project_description_input = gr.Textbox(label="Project Description (optional)")
                with gr.Accordion("Advanced Settings", open=True):
                    gr.Markdown("# Personal Access Token (for private repos)")
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
        with gr.Column(scale=4):
            with gr.Row():
                generate_button = gr.Button("Generate README")
                clear_button = gr.Button("Clear", variant="secondary", elem_classes="clear-button")
            status_output = gr.Label(label="Status")
            readme_output = gr.Markdown(
                label="Generated README",
                min_height=500,
                max_height=500
            )
            readme_file_output = gr.File(label="Download README", visible=False)



    clear_button.click(
        fn=lambda: [None] * 5 + [gr.File(visible=False)],
        inputs=[],
        outputs=[
            repo_url_input,
            project_description_input,
            access_token_input,
            status_output,
            readme_output,
            readme_file_output
        ]
    )
    def update_outputs(status, readme, file_path):
        return status, readme, gr.File(value=file_path, visible=bool(file_path))
    
    generate_button.click(
        fn=generate_readme_from_repo,
        inputs=[
            llm_dropdown,
            api_key,
            repo_url_input,
            project_description_input,
            access_token_input
        ],
        outputs=[
            status_output,
            readme_output,
            readme_file_output
        ]
    ).then(
        fn=update_outputs,
        inputs=[
            status_output,
            readme_output,
            readme_file_output
        ],
        outputs=[
            status_output,
            readme_output,
            readme_file_output
        ]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )