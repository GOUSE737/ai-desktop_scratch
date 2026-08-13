from typing import Callable, Optional, Tuple
from security.command_risk import CommandRiskClassifier, RiskLevel
from utils.logger import get_logger
from utils.helpers import sanitize_command_text

logger = get_logger("ConfirmationManager")

class ConfirmationManager:
    """
    Solits explicit user confirmation for High/Medium risk commands.
    Supports audio confirmation ("yes", "confirm", "proceed") or GUI button approval.
    """
    def __init__(self):
        self.risk_classifier = CommandRiskClassifier()

    def is_affirmative(self, response_text: str) -> bool:
        """Evaluates whether user speech or input means YES/CONFIRMED."""
        if not response_text:
            return False
        clean = sanitize_command_text(response_text)
        affirmative_words = ["yes", "yep", "yeah", "confirm", "proceed", "do it", "sure", "ok", "okay"]
        return any(word in clean.split() or clean == word for word in affirmative_words)

    def request_confirmation(
        self,
        intent: str,
        target_description: str,
        tts_func: Optional[Callable[[str], None]] = None,
        stt_func: Optional[Callable[[], Tuple[bool, str]]] = None
    ) -> bool:
        """
        Requests confirmation via TTS and STT if audio callbacks are provided.
        Returns True if confirmed, False if denied or timed out.
        """
        prompt_msg = f"Warning: {target_description}. This action requires confirmation. Do you want to proceed?"
        logger.warning(prompt_msg)

        if tts_func:
            tts_func(prompt_msg)

        if stt_func:
            success, speech_text = stt_func()
            if success and self.is_affirmative(speech_text):
                logger.info("Confirmation received via voice.")
                if tts_func:
                    tts_func("Confirmed. Executing action.")
                return True
            else:
                logger.info("Confirmation denied or not received.")
                if tts_func:
                    tts_func("Operation cancelled.")
                return False

        # If no audio callback, default to requiring explicit GUI flag
        return False
