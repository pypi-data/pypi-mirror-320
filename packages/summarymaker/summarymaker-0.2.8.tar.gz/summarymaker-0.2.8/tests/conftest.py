import pytest
import tempfile
import os

@pytest.fixture
def sample_text():
    return """
    Artificial intelligence has emerged as a transformative force in modern healthcare, 
    revolutionizing everything from diagnostic procedures to patient care management. 
    In recent years, healthcare providers and institutions worldwide have increasingly 
    adopted AI-powered solutions to enhance their services and improve patient outcomes.
    """

@pytest.fixture
def sample_text_file(sample_text):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(sample_text)
    yield f.name
    os.unlink(f.name)