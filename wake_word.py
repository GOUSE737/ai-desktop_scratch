import re
from typing import Tuple
from config.config_manager import get_config
from utils.helpers import sanitize_command_text

class WakeWordDetector:
    def __init__(self):
        self.config = get_config()
        self.wake_word = self.config.get_setting("wake_word", "jarvis").lower().strip()

    def contains_wake_word(self, text: str) -> bool:
        """Checks if text contains the wake word."""
        if not text:
            return False
        clean = sanitize_command_text(text)
        return self.wake_word in clean.split() or clean.startswith(self.wake_word)

    def strip_wake_word(self, text: str) -> str:
        """Removes the wake word from command text."""
        if not text:
            return ""
        clean = sanitize_command_text(text)
        pattern = re.compile(rf"\b{re.escape(self.wake_word)}\b", re.IGNORECASE)
        stripped = pattern.sub("", clean).strip()
        return stripped
