import pytest
from core.context_manager import ContextManager

def test_context_manager_ordinal():
    cm = ContextManager()
    assert cm.resolve_ordinal("open the second result") == 2
    assert cm.resolve_ordinal("play the first video") == 1
    assert cm.resolve_ordinal("show 3rd item") == 3

def test_contextual_follow_up_search():
    cm = ContextManager()
    cm.update_app_context("youtube")
    
    intent, entities = cm.resolve_contextual_command("WEB_SEARCH", {"query": "Python tutorials"}, "search Python tutorials")
    assert intent == "YOUTUBE_SEARCH"
    assert entities["query"] == "Python tutorials"

def test_contextual_ordinal_resolution():
    cm = ContextManager()
    cm.update_search_context("youtube", "Python tutorials")
    
    intent, entities = cm.resolve_contextual_command("UNKNOWN", {}, "Open the second result")
    assert intent == "YOUTUBE_SEARCH"
    assert "result 2" in entities["query"]
