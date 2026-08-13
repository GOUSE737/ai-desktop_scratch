import json
from typing import Any, Dict, List, Optional
from storage.database import get_db, DatabaseManager
from utils.logger import get_logger

logger = get_logger("HistoryManager")

class HistoryManager:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or get_db()

    def log_command(
        self,
        raw_command: str,
        intent: Optional[str] = None,
        action_type: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[str] = None
    ) -> bool:
        """
        Records a command execution entry in sqlite history.
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO command_history (raw_command, intent, action_type, status, details)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (raw_command, intent, action_type, status, details)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging command to history: {e}")
            return False

    def get_recent_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves recent command execution history."""
        results = []
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, timestamp, raw_command, intent, action_type, status, details
                    FROM command_history
                    ORDER BY id DESC
                    LIMIT ?;
                    """,
                    (limit,)
                )
                rows = cursor.fetchall()
                for r in rows:
                    results.append({
                        "id": r["id"],
                        "timestamp": r["timestamp"],
                        "raw_command": r["raw_command"],
                        "intent": r["intent"],
                        "action_type": r["action_type"],
                        "status": r["status"],
                        "details": r["details"]
                    })
        except Exception as e:
            logger.error(f"Error retrieving command history: {e}")
        return results

    def clear_history(self) -> bool:
        """Clears all records in command history."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM command_history;")
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False

    # Custom Macro Commands Management
    def add_custom_command(self, trigger_phrase: str, action_sequence: List[Dict[str, Any]]) -> bool:
        """Saves a user-defined custom command macro."""
        try:
            actions_json = json.dumps(action_sequence)
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO custom_commands (trigger_phrase, action_sequence)
                    VALUES (?, ?);
                    """,
                    (trigger_phrase.lower().strip(), actions_json)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding custom command '{trigger_phrase}': {e}")
            return False

    def get_custom_command(self, trigger_phrase: str) -> Optional[List[Dict[str, Any]]]:
        """Looks up action sequence for a custom macro trigger phrase."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT action_sequence FROM custom_commands WHERE trigger_phrase = ?;
                    """,
                    (trigger_phrase.lower().strip(),)
                )
                row = cursor.fetchone()
                if row:
                    return json.loads(row["action_sequence"])
        except Exception as e:
            logger.error(f"Error reading custom command '{trigger_phrase}': {e}")
        return None
