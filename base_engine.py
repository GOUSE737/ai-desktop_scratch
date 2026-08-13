from abc import ABC, abstractmethod
from typing import Dict, Any

class AIEngine(ABC):
    """
    Abstract Interface for Natural Language Understanding engines.
    Allows seamlessly swapping between RuleBasedEngine, LocalLLMEngine, or OnlineLLMEngine.
    """
    @abstractmethod
    def understand(self, text: str) -> Dict[str, Any]:
        """
        Parses text and returns structured intent and entities dict.
        Example return:
        {
            "intent": "OPEN_APP",
            "entities": {"app_name": "chrome"},
            "confidence": 1.0,
            "raw_text": "open chrome"
        }
        """
        pass
