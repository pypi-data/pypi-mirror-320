# SummaryMaker

A Python command-line tool for text summarization that can process both text files and web articles.

## Features
- Summarize text from local files
- Extract and summarize content from web URLs
- Configurable summarization model selection
- Adjustable summary length
- Support for multiple text encodings

## Installation

### From PyPI
```bash
pip install summarymaker
```

### Development Installation
```bash
git clone https://github.com/hwang2006/summarymaker
cd summarymaker
pip install -e .[dev]
```

## Dependencies
- Python >= 3.7
- click>=8.0.0
- transformers>=4.0.0
- torch==2.4.0
- numpy<2.0 
- beautifulsoup4>=4.9.0
- requests>=2.25.0
- flask>=2.0.0 

## Usage
```bash
# Summarize a text file
summarymaker --file examples/test.txt

# Summarize content from a URL
summarymaker --url https://example.com

# Customize the model and summary length
summarymaker --file examples/test_article.txt --model facebook/bart-large-cnn --max-length 200
```

## Flask Web Application
To run the Flask web application, use the following command:
1. Navigate to the src/summarizer/webapp directory.
2. Run the Flask application: 
```bach
python app.py
```
3. Open your web browser and go to http://127.0.0.1:5000/.
4. Choose the input type (URL, File, or Text), provide the input, and click "Summarize".
![Flask GUI](/assets/flask_gui.png)

## Gradio Web Application
### Local Deployment
To run the Gradio web application, use the following command:
1. Navigate to the src/summarizer/webapp directory.
2. Run the Gradio application: 
```bach
python gradio_app.py
```
3. Open your web browser and go to http://127.0.0.1:7860/.
4. This will start a Gradio web server, and you can interact with the summarization application through a web browser.
![Gradio GUI](/assets/gradio_gui_2.png)

### Online Deployment on Koyeb
The Gradio web application is deployed on Koyeb, a serverless platform that simplifies hosting and managing applications, allowing quick and scalable deployments. You can try out the SummaryMaker Web application using the following steps:

1. Open your web browser and go to [SummaryMaker on Koyeb](https://distinctive-alida-kisti-defa9b51.koyeb.app/)
2. Choose the input type (URL, File, or Text).
3. Provide the input (URL, upload a file, or enter text directly).
4. Select a text summarization model (e.g., google/flan-t5-small ) on Hugging Face.
5. Optionally adjust the maximum summary length.
6. Click "Summarize" to generate the summary.

## Command-Line Options
- `--file`: Path to a text file to summarize
- `--url`: URL of web content to summarize
- `--model`: Name of the transformer model to use (default: t5-small)
- `--max-length`: Maximum length of the summary in tokens (default: 180)

## Examples
```bash
# Basic file summarization
summarymaker --file examples/test.txt

# Web article summarization
summarymaker --url https://en.wikipedia.org/wiki/Seoul

# Custom model and length. 
# Unlike the t5-base model, the facebook/bart-large-cnn model can handle inputs only up to 512 tokens.
summarymaker --file examples/test_article.md --model facebook/bart-large-cnn --max-length 250

# allenai/led-base-16384 is a Longformer Encoder-Decoder (LED) model designed to handle long sequences.
summarymaker --file examples/test_article.md --model allenai/led-base-16384 --max-length 1024
```

## Development
The project follows a standard Python package structure:
- Source code is located in `src/summarizer/`
- Tests are in the `tests/` directory
- Example files can be found in `examples/`
- Configuration files include `pyproject.toml` and `setup.py`

## Project Structure
```
summarymaker/
├── CHANGELOG.md
├── LICENSE
├── MANIFEST.in
├── README.md
├── assets/
│   ├── flask_gui.png
│   └── gradio_gui.png
├── examples/
│   ├── test.txt
│   ├── test_article.md
│   └── test_article.txt
├── myvenv/
├── pyproject.toml
├── setup.py
├── src/
│   └── summarizer/
│       ├── __init__.py
│       ├── cli.py
│       ├── summarizer.py
│       ├── utils.py
│       └── webapp/
│           ├── app.py
│           ├── gradio_app.py
│           └── templates/
│               └── index.html
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_cli.py
    ├── test_summarizer.py
    └── test_utils.py
```
## Contributing

We welcome contributions from the community! Here's how you can help:

### Getting Started
1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines for Python code
- Write tests for new features using pytest
- Update documentation to reflect any changes
- Add new examples if introducing new functionality
- Update the CHANGELOG.md file with your changes

### Running Tests
```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Run tests with coverage
coverage run -m pytest tests/
coverage report
```

### Documentation
- Update docstrings for any new functions or classes
- Keep the README.md updated with new features or changes
- Add inline comments for complex logic

### Code Review Process
1. Maintainers will review your Pull Request
2. Address any comments or requested changes
3. Once approved, your code will be merged
4. Your contribution will be added to the CHANGELOG.md

For major changes, please open an issue first to discuss what you would like to change. This ensures your time is well spent and your contribution aligns with the project's direction.

## License
Copyright (c) 2024 [Soonwook Hwang]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
