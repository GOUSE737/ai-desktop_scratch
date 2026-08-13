import pytest
from automation.browser_controller import BrowserController

def test_browser_controller_url_formatting():
    controller = BrowserController()
    
    # Test fallback web search formatting
    success_google, msg_google = controller.search_google("python tutorials")
    assert success_google is True
    assert "Opened https://www.google.com/search?q=python+tutorials" in msg_google

    success_yt, msg_yt = controller.search_youtube("machine learning")
    assert success_yt is True
    assert "Opened https://www.youtube.com/results?search_query=machine+learning" in msg_yt
