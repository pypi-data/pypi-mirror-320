from click.testing import CliRunner
#from summarizer.cli import main
from summarizer.cli import main

def test_cli_with_file(sample_text_file, sample_text, mocker):
    # If using: from .summarizer import process_text in cli.py
    mock_process = mocker.patch('summarizer.cli.process_text')
    mock_process.return_value = "Summarized text"
    
    runner = CliRunner()
    result = runner.invoke(main, ['--file', sample_text_file])

    #print("CLI Output:\n", result.output)  # Print the output for debugging
    #print("sample text:\n", sample_text)

    assert result.exit_code == 0
    assert "Summarized text" in result.output
    mock_process.assert_called_once_with(sample_text.strip(), model="t5-base", max_length=180 )

def test_cli_with_url(mocker):
    #mock_extract = mocker.patch('summarizer.utils.extract_from_url')
    #mock_process = mocker.patch('summarizer.summarizer.process_text')
    mock_extract = mocker.patch('summarizer.cli.extract_from_url')
    mock_process = mocker.patch('summarizer.cli.process_text')

    mock_extract.return_value ="""
    This domain is for use in illustrative examples in documents. You may use this
    domain in literature without prior coordination or asking for permission. More information...
    """
    mock_process.return_value = "Summarized text"
    
    runner = CliRunner()
    result = runner.invoke(main, ['--url', 'http://example.com'])
    #result = runner.invoke(main, ['--url', 'https://en.wikipedia.org/wiki/Seoul'])

    #print("CLI Output:\n", result.output)  # Print the output for debugging
    #result.output = """
    #Fetching text from URL: http://example.com 
    #Starting summarization process...
    # 
    #Summary:
    #================================================================================
    #Summarized text
    #================================================================================
    #""" 
    
    assert result.exit_code == 0
    assert "Summarized text" in result.output

    mock_extract.assert_called_once_with('http://example.com')
    #mock_extract.assert_called_once_with('https://en.wikipedia.org/wiki/Seoul')
    #mock_process.assert_called_once_with("Extracted text", model='t5-base', max_length=180)
    mock_process.assert_called_once_with(mock_extract.return_value, model='t5-base', max_length=180)

def test_cli_no_input():
    runner = CliRunner()
    result = runner.invoke(main, [])
    
    assert result.exit_code != 0
    assert "Please provide either --url or --file" in result.output

def test_cli_invalid_file():
    runner = CliRunner()
    result = runner.invoke(main, ['--file', 'nonexistent.txt'])
    
    assert result.exit_code != 0
    assert "Error" in result.output