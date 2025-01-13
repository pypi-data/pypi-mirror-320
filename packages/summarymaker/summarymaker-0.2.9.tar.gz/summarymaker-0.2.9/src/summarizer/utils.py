import requests
from bs4 import BeautifulSoup
import time

def read_file(file_path):
    """
    Read text content from a file.
    
    Args:
        file_path (str): Path to the text file
        
    Returns:
        str: File content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                raise Exception("File is empty")
            return content
    except UnicodeDecodeError:
        # Try with different encodings if utf-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read().strip()
                if not content:
                    raise Exception("File is empty")
                return content
        except Exception as e:
            raise Exception(f"Failed to read file with alternative encoding: {str(e)}")
    except Exception as e:
        raise Exception(f"File reading failed: {str(e)}")

def extract_from_url(url):
    """
    Extract text content from a URL.
    
    Args:
        url (str): URL to extract text from
        
    Returns:
        str: Extracted text content
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Add retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                break
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Try to get text from articles first
        article_text = ""
        articles = soup.find_all(['article', 'main'])
        if articles:
            for article in articles:
                paragraphs = article.find_all("p")
                article_text += " ".join(p.text.strip() for p in paragraphs if p.text.strip())
        
        # If no article text found, fall back to all paragraphs
        if not article_text:
            paragraphs = soup.find_all("p")
            article_text = " ".join(p.text.strip() for p in paragraphs if p.text.strip())
        
        if not article_text:
            raise Exception("No text content found on the page")
            
        return article_text
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise Exception(f"URL extraction failed: {str(e)}")