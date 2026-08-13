from enum import Enum
from typing import Dict, Any

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class CommandRiskClassifier:
    """
    Classifies intent and action requests into LOW, MEDIUM, or HIGH risk categories.
    """
    # High risk commands that can cause data loss or system shutdown
    HIGH_RISK_INTENTS = {
        "DELETE_FILE",
        "SYSTEM_SHUTDOWN",
        "SYSTEM_RESTART"
    }

    # Medium risk commands modifying state
    MEDIUM_RISK_INTENTS = {
        "MOVE_FILE",
        "RENAME_FILE",
        "CLOSE_APP"
    }

    def classify(self, intent: str, entities: Dict[str, Any] = None) -> RiskLevel:
        """Determines the RiskLevel for a given intent."""
        if intent in self.HIGH_RISK_INTENTS:
            return RiskLevel.HIGH
        elif intent in self.MEDIUM_RISK_INTENTS:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def requires_confirmation(self, intent: str, confirmation_mode: str = "strict") -> bool:
        """
        Checks whether confirmation is required before execution based on risk classification.
        """
        risk = self.classify(intent)
        if risk == RiskLevel.HIGH:
            return True
        if risk == RiskLevel.MEDIUM and confirmation_mode.lower() == "strict":
            return True
        return False
