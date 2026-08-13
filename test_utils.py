import os
import pytest
from utils.logger import setup_logger, get_logger
from utils.paths import get_project_root, get_log_dir, get_user_home_dir, resolve_app_path
from utils.helpers import sanitize_command_text, is_windows_os

def test_is_windows():
    assert is_windows_os() is True

def test_sanitize_command_text():
    assert sanitize_command_text("  Open Chrome!  ") == "open chrome"
    assert sanitize_command_text("Can you OPEN 'VS Code'???") == "can you open vs code"
    assert sanitize_command_text("") == ""

def test_path_resolution():
    root = get_project_root()
    assert root.exists()
    assert (root / "utils").exists()

    log_dir = get_log_dir()
    assert log_dir.exists()

    home = get_user_home_dir()
    assert home.exists()

def test_logger():
    logger = setup_logger("TestLogger")
    assert logger is not None
    logger.info("Test log message")
    log_file = get_log_dir() / "assistant.log"
    assert log_file.exists()
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Test log message" in content
