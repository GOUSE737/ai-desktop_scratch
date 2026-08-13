import re
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger("ContextManager")

class ContextManager:
    """
    Maintains short-term conversational context:
    - last active app
    - last search query & platform (Google / YouTube / Files)
    - last file or folder referenced
    - last ordinal result index ("first result", "second result")
    """
    def __init__(self):
        self.context: Dict[str, Any] = {
            "last_app": None,
            "last_search_platform": None,
            "last_search_query": None,
            "last_file": None,
            "last_folder": None,
            "last_results": []
        }

    def update_app_context(self, app_name: str):
        self.context["last_app"] = app_name
        logger.info(f"Context updated: last_app = '{app_name}'")

    def update_search_context(self, platform: str, query: str, results: Optional[list] = None):
        self.context["last_search_platform"] = platform
        self.context["last_search_query"] = query
        if results is not None:
            self.context["last_results"] = results
        logger.info(f"Context updated: search platform='{platform}', query='{query}'")

    def update_file_context(self, file_path: str):
        self.context["last_file"] = file_path
        logger.info(f"Context updated: last_file = '{file_path}'")

    def update_folder_context(self, folder_path: str):
        self.context["last_folder"] = folder_path
        logger.info(f"Context updated: last_folder = '{folder_path}'")

    def resolve_ordinal(self, text: str) -> Optional[int]:
        """
        Extracts 1-based index from ordinal phrases like 'first result', 'second', '3rd', 'latest'.
        """
        text_lower = text.lower()
        ordinals = {
            "first": 1, "1st": 1,
            "second": 2, "2nd": 2,
            "third": 3, "3rd": 3,
            "fourth": 4, "4th": 4,
            "fifth": 5, "5th": 5,
            "latest": 1, "last": -1
        }
        for k, v in ordinals.items():
            if k in text_lower:
                return v

        m = re.search(r"\b(\d+)(st|nd|rd|th)?\b", text_lower)
        if m:
            return int(m.group(1))
        return None

    def resolve_contextual_command(self, intent: str, entities: Dict[str, Any], raw_text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Resolves dynamic context references (e.g. 'search python' after 'open youtube', or 'open second result').
        """
        clean_text = raw_text.lower().strip()

        # Follow-up search after 'open youtube'
        if intent == "WEB_SEARCH" and self.context["last_app"] == "youtube":
            return "YOUTUBE_SEARCH", {"query": entities.get("query", "")}

        # Follow-up ordinal result selection
        if "result" in clean_text or "one" in clean_text or "number" in clean_text:
            idx = self.resolve_ordinal(clean_text)
            if idx and self.context["last_search_platform"] == "youtube":
                return "YOUTUBE_SEARCH", {"query": f"{self.context['last_search_query']} result {idx}"}

        # Referencing "this folder" / "that folder"
        if ("this folder" in clean_text or "that folder" in clean_text) and self.context["last_folder"]:
            entities["folder_name"] = self.context["last_folder"]

        # Referencing "it" / "the file"
        if ("it" in clean_text or "the file" in clean_text) and self.context["last_file"]:
            entities["target"] = self.context["last_file"]

        return intent, entities

    def clear(self):
        """Clears current short-term context memory."""
        self.context = {
            "last_app": None,
            "last_search_platform": None,
            "last_search_query": None,
            "last_file": None,
            "last_folder": None,
            "last_results": []
        }
