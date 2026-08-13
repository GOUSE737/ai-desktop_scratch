import pytest
from core.assistant import AssistantCore

def test_full_pipeline_text_commands():
    assistant = AssistantCore()
    
    # Test single-step screenshot command
    resp1 = assistant.process_command_text("Take a screenshot")
    assert "Task completed" in resp1 or "Screenshot" in resp1

    # Test multi-step command (Create folder and search files)
    resp2 = assistant.process_command_text("Create a folder called TestFolder, and search for pdf files")
    assert "Task completed" in resp2
