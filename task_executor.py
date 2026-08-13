from typing import Dict, Any, List, Tuple
from automation.desktop_controller import DesktopController
from automation.browser_controller import BrowserController
from automation.file_manager import FileManager
from automation.system_controller import SystemController
from storage.history import HistoryManager
from utils.logger import get_logger

logger = get_logger("TaskExecutor")

class TaskExecutor:
    """
    Executes individual task steps produced by TaskPlanner and validates outcome.
    """
    def __init__(self):
        self.desktop_ctrl = DesktopController()
        self.browser_ctrl = BrowserController()
        self.file_manager = FileManager()
        self.system_ctrl = SystemController()
        self.history = HistoryManager()

    def execute_step(self, step: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Routes an individual step dict to appropriate controller.
        Returns (success: bool, response_message: str).
        """
        intent = step.get("intent", "UNKNOWN")
        entities = step.get("entities", {})
        sub_prompt = step.get("sub_prompt", "")

        logger.info(f"Executing step {step.get('step_number', 1)}: Intent={intent}, Entities={entities}")

        try:
            if intent == "OPEN_APP":
                app_name = entities.get("app_name", "")
                success, msg = self.desktop_ctrl.launch_app(app_name)
                self.history.log_command(sub_prompt, intent, "LAUNCH", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "CLOSE_APP":
                app_name = entities.get("app_name", "")
                success, msg = self.desktop_ctrl.close_app(app_name)
                self.history.log_command(sub_prompt, intent, "CLOSE", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "WEB_SEARCH":
                query = entities.get("query", "")
                success, msg = self.browser_ctrl.search_google(query)
                self.history.log_command(sub_prompt, intent, "SEARCH", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "YOUTUBE_SEARCH":
                query = entities.get("query", "")
                success, msg = self.browser_ctrl.search_youtube(query)
                self.history.log_command(sub_prompt, intent, "YOUTUBE", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "PLAY_YOUTUBE_VIDEO":
                query = entities.get("query", "")
                success, msg = self.browser_ctrl.play_youtube_video(query)
                self.history.log_command(sub_prompt, intent, "YOUTUBE_PLAY", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "CREATE_FOLDER":
                folder_name = entities.get("folder_name", "")
                success, msg = self.file_manager.create_folder(folder_name)
                self.history.log_command(sub_prompt, intent, "FILE", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "FILE_SEARCH":
                query = entities.get("query", "")
                results = self.file_manager.search_files(query)
                if results:
                    msg = f"Found {len(results)} files matching '{query}': {results[0]['name']}"
                    self.history.log_command(sub_prompt, intent, "FILE", "SUCCESS", msg)
                    return True, msg
                else:
                    msg = f"No files found matching '{query}'."
                    self.history.log_command(sub_prompt, intent, "FILE", "FAILURE", msg)
                    return False, msg

            elif intent == "RENAME_FILE":
                old_name = entities.get("old_name", "")
                new_name = entities.get("new_name", "")
                success, msg = self.file_manager.rename_item(old_name, new_name)
                self.history.log_command(sub_prompt, intent, "FILE", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "MOVE_FILE":
                source = entities.get("source", "")
                dest = entities.get("destination", "")
                success, msg = self.file_manager.move_item(source, dest)
                self.history.log_command(sub_prompt, intent, "FILE", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "DELETE_FILE":
                target = entities.get("target", "")
                success, msg = self.file_manager.delete_item(target)
                self.history.log_command(sub_prompt, intent, "FILE", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "SCREENSHOT":
                success, msg = self.system_ctrl.take_screenshot()
                self.history.log_command(sub_prompt, intent, "SYSTEM", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "SYSTEM_VOLUME":
                action = entities.get("action", "toggle")
                level = entities.get("level")
                success, msg = self.system_ctrl.adjust_volume(action, level)
                self.history.log_command(sub_prompt, intent, "SYSTEM", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "SYSTEM_LOCK":
                success, msg = self.system_ctrl.lock_workstation()
                self.history.log_command(sub_prompt, intent, "SYSTEM", "SUCCESS" if success else "FAILURE", msg)
                return success, msg

            elif intent == "CUSTOM_COMMAND":
                sequence = entities.get("action_sequence", [])
                sub_results = []
                for sub_step in sequence:
                    s_intent = sub_step.get("intent", "OPEN_APP")
                    s_entities = sub_step.get("entities", {})
                    s_ok, s_msg = self.execute_step({"intent": s_intent, "entities": s_entities, "sub_prompt": sub_prompt})
                    sub_results.append(s_msg)
                return True, f"Custom command executed: {', '.join(sub_results)}"

            else:
                msg = f"Unknown command or unsupported intent: '{sub_prompt}'"
                self.history.log_command(sub_prompt, intent, "UNKNOWN", "FAILURE", msg)
                return False, msg

        except Exception as e:
            logger.error(f"Execution error for step {step}: {e}")
            return False, f"Step execution failed: {str(e)}"

    def execute_plan(self, plan: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        messages = []
        all_success = True

        for step in plan:
            success, msg = self.execute_step(step)
            messages.append(msg)
            if not success:
                all_success = False
                logger.warning(f"Step {step.get('step_number')} failed. Stopping plan execution.")
                break

        return all_success, messages
