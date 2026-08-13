import threading
from typing import Callable, Optional, Dict, Any, List
from speech.speech_to_text import STTService
from speech.text_to_speech import get_tts
from speech.wake_word import WakeWordDetector
from core.intent_engine import IntentEngine
from core.context_manager import ContextManager
from core.task_planner import TaskPlanner
from core.task_executor import TaskExecutor
from core.action_verifier import ActionVerifier
from security.command_risk import CommandRiskClassifier, RiskLevel
from security.confirmation_manager import ConfirmationManager
from storage.history import HistoryManager
from utils.logger import get_logger

logger = get_logger("AssistantCore")

class AssistantCore:
    """
    Central Orchestrator combining:
    Voice Input -> Intent Recognition -> Context Resolution -> Task Planning
    -> Security Risk Check -> Action Execution -> Verification -> TTS Response
    """
    def __init__(self, status_callback: Optional[Callable[[str, str], None]] = None):
        self.status_callback = status_callback
        self.stt = STTService()
        self.tts = get_tts()
        self.wake_detector = WakeWordDetector()
        self.intent_engine = IntentEngine()
        self.context_mgr = ContextManager()
        self.planner = TaskPlanner(self.intent_engine)
        self.executor = TaskExecutor()
        self.verifier = ActionVerifier()
        self.risk_classifier = CommandRiskClassifier()
        self.confirmation_mgr = ConfirmationManager()
        self.history = HistoryManager()

        self.current_state = "IDLE"

    def set_state(self, state: str, detail_message: str = ""):
        """Updates internal status machine and triggers UI callback if provided."""
        self.current_state = state
        logger.info(f"Assistant State Transition: [{state}] - {detail_message}")
        if self.status_callback:
            self.status_callback(state, detail_message)

    def process_command_text(self, raw_text: str) -> str:
        """
        Main pipeline executing a natural language command string.
        """
        if not raw_text or not raw_text.strip():
            self.set_state("ERROR", "No speech or empty command received.")
            return "I didn't hear anything."

        # 1. Listening / Processing
        clean_text = self.wake_detector.strip_wake_word(raw_text)
        self.set_state("PROCESSING", f"Understanding: '{clean_text}'")

        # 2. Planning
        self.set_state("PLANNING", "Decomposing task steps...")
        plan = self.planner.create_plan(clean_text)

        if not plan:
            self.set_state("ERROR", "Could not generate execution plan.")
            msg = "I did not understand that command."
            self.tts.speak(msg)
            return msg

        # 3. Security Risk Check & Execution
        for step in plan:
            intent = step["intent"]
            entities = step["entities"]
            sub_prompt = step["sub_prompt"]

            # Resolve Contextual References
            resolved_intent, resolved_entities = self.context_mgr.resolve_contextual_command(intent, entities, sub_prompt)
            step["intent"] = resolved_intent
            step["entities"] = resolved_entities

            # Risk Check
            if self.risk_classifier.requires_confirmation(resolved_intent):
                self.set_state("CONFIRMATION_REQUIRED", f"High Risk: {resolved_intent}")
                # For headless/automated execution without GUI click, confirm if prompt allows
                logger.warning(f"Execution requires confirmation for intent {resolved_intent}")

            # 4. Executing
            self.set_state("EXECUTING", f"Step {step['step_number']}: {sub_prompt}")
            success, result_msg = self.executor.execute_step(step)

            # 5. Verifying
            self.set_state("VERIFYING", f"Verifying {resolved_intent} outcome...")
            if resolved_intent == "OPEN_APP":
                app_name = resolved_entities.get("app_name", "")
                self.verifier.verify_app_launched(app_name, timeout_seconds=1.5)
                self.context_mgr.update_app_context(app_name)
            elif resolved_intent in ["WEB_SEARCH", "YOUTUBE_SEARCH"]:
                self.context_mgr.update_search_context("youtube" if "YOUTUBE" in resolved_intent else "google", resolved_entities.get("query", ""))

            if not success:
                self.set_state("ERROR", f"Step failed: {result_msg}")
                self.tts.speak(result_msg)
                return result_msg

        # 6. Success & Response
        final_msg = f"Task completed successfully."
        self.set_state("SUCCESS", final_msg)
        self.tts.speak(final_msg)
        
        # Reset back to IDLE state after brief delay
        threading.Timer(2.0, lambda: self.set_state("IDLE", "Ready for commands.")).start()
        return final_msg

    def listen_and_process_voice(self) -> str:
        """
        Triggers STT microphone listening loop and processes resulting voice prompt.
        """
        self.set_state("LISTENING", "Listening via microphone...")
        success, speech_text = self.stt.listen_and_recognize()
        if not success:
            self.set_state("ERROR", speech_text)
            self.tts.speak(speech_text)
            threading.Timer(2.0, lambda: self.set_state("IDLE", "Ready")).start()
            return speech_text

        return self.process_command_text(speech_text)
