from transformers import pipeline
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = "3"

def process_text(text, model="t5-base", max_length=180):
    """
    Process and summarize the input text.
    
    Args:
        text (str): Input text to summarize
        model (str): Name of the transformer model to use
        max_length (int): Maximum length of the summary
        
    Returns:
        str: Summarized text
    """
    try:
        summarizer = pipeline("summarization", model=model)
        result = summarizer(text, max_length=max_length)
        return result[0]["summary_text"]
    except Exception as e:
        raise Exception(f"Summarization failed: {str(e)}")