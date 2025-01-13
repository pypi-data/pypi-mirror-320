import pytest
#from'summarizer.summarizer import process_text
from summarizer.summarizer import process_text


def test_process_text_success(mocker, sample_text):
    """
    When you create a pipeline, it's a two-step process:

    # Step 1: Create the pipeline
    summarizer = pipeline("summarization", model="t5-base")
    # Step 2: Use the pipeline
    summary = summarizer(text)

    # This works because it matches Step 1 - creating the pipeline
    mock_pipeline.assert_called_once_with("summarization", model="t5-base")

    # This doesn't work because it's trying to assert Step 2
    mock_pipeline.assert_called_once_with(sample_text, model="t5-base")

    """
    # If using: from transformers import pipeline in summarizer.py
    # This works because it matches Step 1 - creating the pipeline
    mock_pipeline = mocker.patch('summarizer.summarizer.pipeline')

    # If using: import transformers
    #mock_pipeline = mocker.patch('summarizer.summarizer.transformers.pipeline')
    

    mock_summarizer = mock_pipeline.return_value
    mock_summarizer.return_value = [{'summary_text': 'Test summary'}]
    #mock_pipeline.return_value.return_value = [{'summary_text': 'Test summary'}]
 
    result = process_text(sample_text.strip())

    #print("result: ", result) #for debugging purpose
    assert result == 'Test summary'
    mock_pipeline.assert_called_once_with("summarization", model="t5-base")
    mock_summarizer.assert_called_once_with(sample_text.strip(), max_length=180)
    #mock_pipeline.assert_called_once_with(sample_text, model="t5-base")

def test_process_text_with_custom_model(mocker, sample_text):
    mock_pipeline = mocker.patch('summarizer.summarizer.pipeline')
    mock_summarizer = mock_pipeline.return_value
    mock_summarizer.return_value = [{'summary_text': 'Test summary'}]
    
    custom_model = "t5-small"
    result = process_text(sample_text.strip(), model=custom_model)
    
    print(result) # print out result for debugging purpose
    
    assert result == 'Test summary'
    #mock_pipeline.assert_called_once_with("summarization", model=custom_model)
    mock_summarizer.assert_called_once_with(sample_text.strip(), max_length=180)

def test_process_text_failure(mocker, sample_text):
    mock_pipeline = mocker.patch('summarizer.summarizer.pipeline')
    mock_summarizer = mock_pipeline.return_value
    mock_summarizer.return_value = [{'summary_text': 'Test summary'}]
    mock_pipeline.side_effect = Exception("Model error")

    with pytest.raises(Exception) as exc_info:
        process_text(sample_text.strip())
         
    print("Exception String: ", str(exc_info.value)) # for debugging purpose
    assert "Summarization failed" in str(exc_info.value)
