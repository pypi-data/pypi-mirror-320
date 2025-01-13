from flask import Flask, request, render_template
from summarizer.summarizer import process_text  # Adjust import path
from summarizer.utils import extract_from_url, read_file  # Adjust import path
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Limit file upload size to 1 MB
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

@app.route('/')
def index():
    # Render the template with an empty summary by default
    return render_template('index.html', summary="")

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        choice = request.form.get('choice')
        url = request.form.get('url')
        file = request.files.get('file')
        text = request.form.get('text')
        model = request.form.get('model') or 't5-base'
        max_length = request.form.get('max_length')

        # Validate max_length
        try:
            max_length = int(max_length) if max_length else 180
            if max_length <= 0:
                raise ValueError("Max length must be positive.")
        except ValueError:
            return render_template('index.html', error="Invalid maximum length", summary="")

        # Ensure only one input is provided
        if (choice == 'url' and not url) or (choice == 'file' and not file) or (choice == 'text' and not text):
            return render_template('index.html', error="Please provide the selected input type.", summary="")

        input_text = ""
        if choice == 'url':
            if not url.startswith(('http://', 'https://')):
                return render_template('index.html', error="Invalid URL format.", summary="")
            try:
                input_text = extract_from_url(url)
            except Exception as e:
                logging.error(f"URL extraction failed: {str(e)}")
                return render_template('index.html', error="URL extraction failed.", summary="")
        elif choice == 'file':
            if not file.filename.endswith('.txt'):
                return render_template('index.html', error="Only .txt files are supported.", summary="")
            try:
                input_text = file.read().decode('utf-8')
            except Exception as e:
                logging.error(f"File reading failed: {str(e)}")
                return render_template('index.html', error="File reading failed.", summary="")
        elif choice == 'text':
            input_text = text

        if not input_text or len(input_text.strip()) < 50:
            return render_template('index.html', error="Not enough text content to summarize", summary="")

        try:
            summary = process_text(input_text, model=model, max_length=max_length)
        except Exception as e:
            logging.error(f"Summarization failed: {str(e)}")
            return render_template('index.html', error="Summarization failed.", summary="")

        return render_template('index.html', summary=summary, url=url, model=model, max_length=max_length, text=text)

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return render_template('index.html', error="An unexpected error occurred.", summary="")

if __name__ == '__main__':
    # Use a secure production-ready WSGI server for deployment, e.g., Gunicorn
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)
