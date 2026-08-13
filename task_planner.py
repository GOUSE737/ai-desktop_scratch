import re
from typing import List, Dict, Any
from core.intent_engine import IntentEngine
from utils.logger import get_logger

logger = get_logger("TaskPlanner")

class TaskPlanner:
    """
    Decomposes compound natural language prompts into an ordered sequence of atomic task steps.
    """
    def __init__(self, intent_engine: IntentEngine = None):
        self.intent_engine = intent_engine or IntentEngine()

    def split_compound_prompt(self, text: str) -> List[str]:
        """
        Splits text by step conjunctions such as 'and then', 'then', 'and', or commas.
        Example: "Open Chrome, search YouTube for Python tutorials, and open the first result"
        -> ["Open Chrome", "search YouTube for Python tutorials", "open the first result"]
        """
        if not text:
            return []

        # Replace compound connectors with split markers
        normalized = text.strip()
        normalized = re.sub(r"\b(and\s+then|then|after\s+that)\b", "|", normalized, flags=re.IGNORECASE)
        
        # Handle commas and 'and' when connecting clauses
        clauses = []
        for part in normalized.split("|"):
            sub_parts = re.split(r",|\band\b", part, flags=re.IGNORECASE)
            for sp in sub_parts:
                sp_clean = sp.strip()
                if sp_clean:
                    clauses.append(sp_clean)

        return clauses

    def create_plan(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Generates an ordered task plan containing intent and step details.
        """
        sub_prompts = self.split_compound_prompt(prompt)
        plan = []

        for idx, sub_text in enumerate(sub_prompts, start=1):
            intent_data = self.intent_engine.parse_intent(sub_text)
            plan.append({
                "step_number": idx,
                "sub_prompt": sub_text,
                "intent": intent_data["intent"],
                "entities": intent_data["entities"],
                "confidence": intent_data["confidence"]
            })

        logger.info(f"Generated task plan with {len(plan)} steps for prompt: '{prompt}'")
        return plan
