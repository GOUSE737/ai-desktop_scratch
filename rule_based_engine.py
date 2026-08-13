import re
from typing import Dict, Any, Optional
from ai.base_engine import AIEngine
from utils.helpers import sanitize_command_text
from config.config_manager import get_config

class RuleBasedEngine(AIEngine):
    """
    Deterministic rule-based NLU engine operating fully offline.
    Uses regex patterns, entity extractors, and dictionary mapping.
    """
    def __init__(self):
        self.config = get_config()

    def understand(self, text: str) -> Dict[str, Any]:
        clean_text = sanitize_command_text(text)
        if not clean_text:
            return {"intent": "UNKNOWN", "entities": {}, "confidence": 0.0, "raw_text": text}

        # 1. System Controls (Lock, Restart, Shutdown, Screenshot)
        if re.search(r"\b(take|capture)\b.*\bscreenshot\b", clean_text):
            return {"intent": "SCREENSHOT", "entities": {}, "confidence": 1.0, "raw_text": clean_text}
        
        if re.search(r"\b(lock)\b.*\b(computer|pc|system|screen)\b", clean_text) or clean_text == "lock":
            return {"intent": "SYSTEM_LOCK", "entities": {}, "confidence": 1.0, "raw_text": clean_text}

        if re.search(r"\b(restart|reboot)\b.*\b(computer|pc|system)\b", clean_text) or clean_text == "restart":
            return {"intent": "SYSTEM_RESTART", "entities": {}, "confidence": 1.0, "raw_text": clean_text}

        if re.search(r"\b(shutdown|shut down|turn off)\b.*\b(computer|pc|system)\b", clean_text) or clean_text in ["shutdown", "turn off"]:
            return {"intent": "SYSTEM_SHUTDOWN", "entities": {}, "confidence": 1.0, "raw_text": clean_text}

        # Volume Controls
        vol_match = re.search(r"\b(volume|sound)\b.*\b(up|down|mute|set|turn)\b", clean_text)
        if vol_match or "turn volume" in clean_text or "set volume" in clean_text:
            action = "toggle"
            if "up" in clean_text or "increase" in clean_text:
                action = "up"
            elif "down" in clean_text or "decrease" in clean_text:
                action = "down"
            elif "mute" in clean_text:
                action = "mute"
            
            num_match = re.search(r"\b(\d+)\b", clean_text)
            level = int(num_match.group(1)) if num_match else None
            return {"intent": "SYSTEM_VOLUME", "entities": {"action": action, "level": level}, "confidence": 0.9, "raw_text": clean_text}

        # 2. Play YouTube Video Direct Intent ("play python video", "play python on youtube")
        play_yt_match = re.search(r"\b(play)\b\s+(.*?)\s*\b(on youtube|video|in youtube)?\b", clean_text)
        if play_yt_match and not clean_text.startswith("open"):
            query = play_yt_match.group(2).strip()
            query = re.sub(r"^(video|song|tutorial|on youtube|in youtube)\s*", "", query, flags=re.IGNORECASE).strip()
            query = re.sub(r"\s*(on|in)\s+youtube$", "", query, flags=re.IGNORECASE).strip()
            if not query:
                query = clean_text
            return {"intent": "PLAY_YOUTUBE_VIDEO", "entities": {"query": query}, "confidence": 0.98, "raw_text": clean_text}

        # YouTube Search Intent
        if "youtube" in clean_text and ("search" in clean_text or "find" in clean_text or "look for" in clean_text):
            query = re.sub(r".*?\b(search|find|play|look for)\s*(youtube|for)?\s*", "", clean_text, flags=re.IGNORECASE).strip()
            query = re.sub(r"^(youtube|for|on youtube|in youtube)\s*", "", query, flags=re.IGNORECASE).strip()
            query = re.sub(r"\s*(on|in)\s+youtube$", "", query, flags=re.IGNORECASE).strip()
            if not query or query == "youtube":
                query = clean_text
            return {"intent": "YOUTUBE_SEARCH", "entities": {"query": query}, "confidence": 0.95, "raw_text": clean_text}

        # 3. Application Controls (Open / Close)
        open_match = re.search(r"^\b(open|launch|start|run|can you open)\b\s+(.*)", clean_text)
        if open_match or "i want to browse" in clean_text or "i want to code" in clean_text:
            raw_target = open_match.group(2).strip() if open_match else clean_text
            target = raw_target
            if "browse" in clean_text or "internet" in clean_text or "browser" in clean_text:
                target = "chrome"
            elif "code" in clean_text:
                target = "vscode"
            elif "calculate" in clean_text:
                target = "calculator"

            app_info = self.config.get_app_info(target)
            if not app_info:
                clean_target = re.sub(r"\b(google|app|browser|application|editor)\b", "", target).strip()
                app_info = self.config.get_app_info(clean_target) if clean_target else None

            app_key = app_info["key"] if app_info else target
            return {"intent": "OPEN_APP", "entities": {"app_name": app_key, "query": target}, "confidence": 0.9, "raw_text": clean_text}

        close_match = re.search(r"^\b(close|exit|terminate|stop|kill)\b\s+(.*)", clean_text)
        if close_match:
            target = close_match.group(2).strip()
            app_info = self.config.get_app_info(target)
            app_key = app_info["key"] if app_info else target
            return {"intent": "CLOSE_APP", "entities": {"app_name": app_key, "query": target}, "confidence": 0.9, "raw_text": clean_text}

        # 4. Folder Creation
        create_dir_match = re.search(r"\b(create|make|new)\b\s+(a\s+)?(folder|directory)\b\s*(called|named|with name)?\s*(.*)", clean_text)
        if create_dir_match:
            folder_name = create_dir_match.group(5).strip()
            return {"intent": "CREATE_FOLDER", "entities": {"folder_name": folder_name}, "confidence": 0.95, "raw_text": clean_text}

        # 5. File Operations
        if clean_text.startswith("find") or clean_text.startswith("show my") or "search file" in clean_text or "search for file" in clean_text:
            query = re.sub(r"^(find my|find|show my|search file|search for file|search for)", "", clean_text).strip()
            return {"intent": "FILE_SEARCH", "entities": {"query": query}, "confidence": 0.9, "raw_text": clean_text}

        rename_match = re.search(r"\b(rename)\b\s+(.*?)\s+\bto\b\s+(.*)", clean_text)
        if rename_match:
            old_name = rename_match.group(2).strip()
            new_name = rename_match.group(3).strip()
            return {"intent": "RENAME_FILE", "entities": {"old_name": old_name, "new_name": new_name}, "confidence": 0.95, "raw_text": clean_text}

        move_match = re.search(r"\b(move)\b\s+(.*?)\s+\bto\b\s+(.*)", clean_text)
        if move_match:
            source = move_match.group(2).strip()
            destination = move_match.group(3).strip()
            return {"intent": "MOVE_FILE", "entities": {"source": source, "destination": destination}, "confidence": 0.95, "raw_text": clean_text}

        delete_match = re.search(r"\b(delete|remove)\b\s+(.*)", clean_text)
        if delete_match:
            target = delete_match.group(2).strip()
            return {"intent": "DELETE_FILE", "entities": {"target": target}, "confidence": 0.95, "raw_text": clean_text}

        # 6. Web Search
        web_match = re.search(r"\b(search|google|look up|search google for)\b\s+(.*)", clean_text)
        if web_match:
            query = web_match.group(2).strip()
            query = re.sub(r"^(google for|for|on google)", "", query).strip()
            return {"intent": "WEB_SEARCH", "entities": {"query": query}, "confidence": 0.9, "raw_text": clean_text}

        return {"intent": "UNKNOWN", "entities": {}, "confidence": 0.0, "raw_text": clean_text}
