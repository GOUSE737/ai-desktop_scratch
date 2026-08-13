from typing import Dict, Any, Optional
from ai.base_engine import AIEngine
from ai.rule_based_engine import RuleBasedEngine
from storage.history import HistoryManager
from utils.logger import get_logger

logger = get_logger("IntentEngine")

class IntentEngine:
    """
    Core NLU router that evaluates incoming user prompts against:
    1. Custom macro commands stored in DB.
    2. Selected AI engine (RuleBasedEngine or LocalLLMEngine).
    """
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        self.ai_engine = ai_engine or RuleBasedEngine()
        self.history_manager = HistoryManager()

    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parses text and returns canonical intent structure.
        """
        if not text:
            return {"intent": "UNKNOWN", "entities": {}, "confidence": 0.0, "raw_text": ""}

        # 1. Check if phrase matches custom macro in database
        custom_macro = self.history_manager.get_custom_command(text)
        if custom_macro:
            return {
                "intent": "CUSTOM_COMMAND",
                "entities": {"action_sequence": custom_macro},
                "confidence": 1.0,
                "raw_text": text
            }

        # 2. Delegate to AI engine
        parsed = self.ai_engine.understand(text)
        logger.info(f"Parsed text '{text}' -> Intent: {parsed['intent']} Entities: {parsed['entities']}")
        return parsed
