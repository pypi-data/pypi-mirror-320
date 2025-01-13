import os
import tempfile
import pytest
from summarizer.utils import read_file, extract_from_url
import requests

def test_read_file_success(sample_text_file, sample_text):
    content = read_file(sample_text_file)
    assert content.strip() == sample_text.strip()

def test_read_file_nonexistent():
    with pytest.raises(Exception) as exc_info:
        read_file("nonexistent_file.txt")
    assert "File reading failed" in str(exc_info.value)

def test_read_file_empty():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        pass
    try:
        with pytest.raises(Exception) as exc_info:
            read_file(f.name)
        assert "File is empty" in str(exc_info.value)
    finally:
        os.unlink(f.name)

def test_extract_from_url(requests_mock):
    url = "http://example.com"
    mock_html = """
    <html>
        <body>
            <article>
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
            </article>
        </body>
    </html>
    """
    requests_mock.get(url, text=mock_html)
    content = extract_from_url(url)
    assert "First paragraph. Second paragraph." in content

def test_extract_from_url_no_content(requests_mock):
    url = "http://example.com"
    mock_html = "<html><body></body></html>"
    requests_mock.get(url, text=mock_html)
    with pytest.raises(Exception) as exc_info:
        extract_from_url(url)
    assert "No text content found" in str(exc_info.value)

def test_extract_from_url_connection_error(requests_mock):
    url = "http://example.com"
    requests_mock.get(url, exc=requests.exceptions.ConnectionError)
    with pytest.raises(Exception) as exc_info:
        extract_from_url(url)
    assert "Failed to fetch URL" in str(exc_info.value)
