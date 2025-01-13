def test_example(sample_text_file):
    with open(sample_text_file, 'r') as f:
        content = f.read()
    assert "Artificial intelligence" in content