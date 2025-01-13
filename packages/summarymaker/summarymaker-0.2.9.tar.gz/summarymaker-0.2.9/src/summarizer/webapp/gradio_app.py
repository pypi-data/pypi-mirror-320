# Set environment variables before any other imports
import os
import tempfile

# Create app-specific temp directories
temp_base = tempfile.gettempdir()
os.environ['HF_HOME'] = os.path.join(temp_base, 'huggingface_home')
os.environ['GRADIO_TEMP_DIR'] = os.path.join(temp_base, 'gradio_tmp')

# Create directories with appropriate permissions
for dir_path in [os.environ['HF_HOME'], 
                 os.environ['GRADIO_TEMP_DIR']]:
    try:
        os.makedirs(dir_path, mode=0o777, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create directory {dir_path}: {e}")

# Now import the rest of the dependencies
import gradio as gr
from typing import Optional, Tuple, Union
from pathlib import Path

# Import summarizer components
from summarizer.summarizer import process_text
from summarizer.utils import extract_from_url

class SummaryMaker:
    def __init__(self):
        """Initialize the SummaryMaker application."""
        pass  # Environment setup is now handled at module level

    def summarize_text(
        self,
        choice: str,
        url: str,
        file_path: Optional[str],
        text: str,
        model_name: str,
        max_length: int
    ) -> str:
        """
        Summarize text based on the input type chosen (URL, File, or direct Text).
        
        Args:
            choice: Input type ("URL", "File", or "Text")
            url: URL to extract text from
            file_path: Path to uploaded file
            text: Direct input text
            model_name: Name of the summarization model to use
            max_length: Maximum length of the summary
            
        Returns:
            str: Generated summary or error message
        """
        try:
            input_text = self._get_input_text(choice, url, file_path, text)
            
            if not input_text or len(input_text.strip()) < 50:
                return "Error: Not enough text content to summarize (minimum 50 characters)"
                
            summary = process_text(
                input_text,
                model=model_name,
                max_length=max_length
            )
            return summary
            
        except Exception as e:
            return f"Summarization failed: {str(e)}"

    def _get_input_text(
        self,
        choice: str,
        url: str,
        file_path: Optional[str],
        text: str
    ) -> str:
        """
        Extract text content based on the chosen input method.
        
        Args:
            choice: Input type ("URL", "File", or "Text")
            url: URL to extract text from
            file_path: Path to uploaded file
            text: Direct input text
            
        Returns:
            str: Extracted text content
            
        Raises:
            ValueError: If text extraction fails
        """
        if choice == "URL":
            if not url:
                raise ValueError("No URL provided")
            return extract_from_url(url)
            
        elif choice == "File":
            if not file_path:
                raise ValueError("No file uploaded")
            return Path(file_path.name).read_text(encoding='utf-8')
            
        elif choice == "Text":
            return text
            
        raise ValueError(f"Invalid choice: {choice}")

    def update_visibility(
        self,
        choice: str
    ) -> Tuple[gr.update, gr.update, gr.update, gr.update]:
        """
        Update the visibility of input components based on the selected choice
        and clear the summary output.
        
        Args:
            choice: Selected input type
            
        Returns:
            Tuple of Gradio updates for URL, File, Text, and Summary components
        """
        return (
            gr.update(visible=(choice == "URL"), value=""),  # URL input
            gr.update(visible=(choice == "File"), value=None),  # File input
            gr.update(visible=(choice == "Text"), value=""),  # Text input
            gr.update(value="")  # Summary output
        )

    def create_interface(self):
        """Create and configure the Gradio interface."""
        with gr.Blocks(title="SummaryMaker") as demo:
            gr.Markdown("# SummaryMaker")
            gr.Markdown(
                """A simple tool to generate summaries from text, URLs, or files.
                Choose your input method and adjust the settings below."""
            )
            
            # Input method selection
            choice = gr.Dropdown(
                choices=["Text", "URL", "File"],
                label="Choose input type",
                value="Text"
            )
            
            # Input components
            url = gr.Textbox(
                label="URL to Summarize",
                placeholder="Enter URL here...",
                visible=False
            )
            file = gr.File(
                label="Upload File",
                file_types=[".txt", ".md", ".doc", ".docx"],
                visible=False
            )
            text = gr.Textbox(
                label="Text to Summarize",
                placeholder="Enter or paste your text here...",
                lines=10,
                visible=True
            )
            
            # Model settings
            with gr.Row():
                model = gr.Textbox(
                    label="Model Name",
                    value="t5-base",
                    placeholder="Enter model name..."
                )
                max_length = gr.Slider(
                    label="Maximum Summary Length",
                    minimum=50,
                    maximum=500,
                    value=180,
                    step=10
                )
            
            # Output
            summary = gr.Textbox(
                label="Generated Summary",
                lines=5
            )
            
            # Event handlers
            choice.change(
                fn=self.update_visibility,
                inputs=choice,
                outputs=[url, file, text, summary]  # Added summary to outputs
            )
            
            gr.Button("Generate Summary").click(
                fn=self.summarize_text,
                inputs=[choice, url, file, text, model, max_length],
                outputs=summary
            )
            
        return demo

def main():
    """Initialize and launch the application."""
    app = SummaryMaker()
    demo = app.create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # Set to True to create a public URL
    )

if __name__ == "__main__":
    main()
