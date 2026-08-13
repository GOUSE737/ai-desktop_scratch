import pytest
from pathlib import Path
from config.config_manager import ConfigManager
from storage.database import DatabaseManager
from storage.history import HistoryManager

@pytest.fixture
def tmp_db(tmp_path):
    db_file = tmp_path / "test_assistant.db"
    return DatabaseManager(db_file)

def test_config_manager():
    config = ConfigManager()
    assert config.get_setting("assistant_name") is not None
    assert config.get_setting("listening_timeout") == 5
    
    # Test App Lookup
    chrome = config.get_app_info("Chrome")
    assert chrome is not None
    assert chrome["executable"] == "chrome.exe"
    
    calc = config.get_app_info("calculator")
    assert calc is not None
    assert calc["executable"] == "calc.exe"

def test_database_and_history(tmp_db):
    history = HistoryManager(tmp_db)
    
    # Test logging command
    success = history.log_command("open chrome", intent="OPEN_APP", action_type="LAUNCH", status="SUCCESS")
    assert success is True
    
    records = history.get_recent_history(10)
    assert len(records) == 1
    assert records[0]["raw_command"] == "open chrome"
    assert records[0]["intent"] == "OPEN_APP"

    # Test custom command macro
    macro_actions = [{"action": "open_app", "target": "vscode"}, {"action": "open_app", "target": "chrome"}]
    assert history.add_custom_command("start coding", macro_actions) is True
    
    fetched = history.get_custom_command("Start Coding")
    assert fetched is not None
    assert len(fetched) == 2
    assert fetched[0]["target"] == "vscode"

    # Test clear history
    assert history.clear_history() is True
    assert len(history.get_recent_history(10)) == 0
