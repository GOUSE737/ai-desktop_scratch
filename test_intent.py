import pytest
from core.intent_engine import IntentEngine

@pytest.fixture
def intent_engine():
    return IntentEngine()

def test_open_app_variations(intent_engine):
    phrases = [
        "Open Chrome",
        "Launch Chrome",
        "Start Google Chrome",
        "Can you open the browser?",
        "I want to browse something"
    ]
    for phrase in phrases:
        res = intent_engine.parse_intent(phrase)
        assert res["intent"] == "OPEN_APP", f"Failed for phrase: '{phrase}'"
        assert res["entities"]["app_name"] == "chrome"

def test_youtube_search_variations(intent_engine):
    res1 = intent_engine.parse_intent("Search YouTube for Python tutorials")
    assert res1["intent"] == "YOUTUBE_SEARCH"
    assert res1["entities"]["query"] == "python tutorials"

    res2 = intent_engine.parse_intent("Open YouTube and search machine learning")
    assert res2["intent"] == "YOUTUBE_SEARCH"
    assert "machine learning" in res2["entities"]["query"]

def test_file_and_folder_intents(intent_engine):
    res1 = intent_engine.parse_intent("Create a folder called Major Project")
    assert res1["intent"] == "CREATE_FOLDER"
    assert res1["entities"]["folder_name"] == "major project"

    res2 = intent_engine.parse_intent("Find my PDF files")
    assert res2["intent"] == "FILE_SEARCH"

    res3 = intent_engine.parse_intent("Rename report.pdf to final_report.pdf")
    assert res3["intent"] == "RENAME_FILE"
    assert res3["entities"]["old_name"] == "report.pdf"
    assert res3["entities"]["new_name"] == "final_report.pdf"

    res4 = intent_engine.parse_intent("Delete draft.txt")
    assert res4["intent"] == "DELETE_FILE"
    assert res4["entities"]["target"] == "draft.txt"

def test_system_intents(intent_engine):
    assert intent_engine.parse_intent("Take a screenshot")["intent"] == "SCREENSHOT"
    assert intent_engine.parse_intent("Lock my computer")["intent"] == "SYSTEM_LOCK"
    assert intent_engine.parse_intent("Restart the computer")["intent"] == "SYSTEM_RESTART"
    assert intent_engine.parse_intent("Shut down computer")["intent"] == "SYSTEM_SHUTDOWN"
