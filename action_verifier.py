import os
import time
from pathlib import Path
from typing import Tuple, Dict, Any
from automation.desktop_controller import DesktopController
from utils.logger import get_logger

logger = get_logger("ActionVerifier")

class ActionVerifier:
    """
    Verifies that actions have achieved their expected physical side-effects on Windows OS.
    Checks process existence, window existence, or filesystem path state.
    """
    def __init__(self):
        self.desktop_ctrl = DesktopController()

    def verify_app_launched(self, app_name: str, timeout_seconds: float = 3.0) -> Tuple[bool, str]:
        """
        Verifies that an application process is active and running within timeout window.
        """
        start_time = time.time()
        while time.time() - start_time <= timeout_seconds:
            is_running, pids = self.desktop_ctrl.is_app_running(app_name)
            if is_running:
                logger.info(f"Verification SUCCESS: App '{app_name}' is running with PIDs {pids}.")
                return True, f"Verified: '{app_name}' is running (PID {pids[0]})."
            time.sleep(0.5)

        logger.warning(f"Verification FAILED: App '{app_name}' did not start within {timeout_seconds}s.")
        return False, f"Verification failed: '{app_name}' process was not detected."

    def verify_app_closed(self, app_name: str, timeout_seconds: float = 3.0) -> Tuple[bool, str]:
        """
        Verifies that an application process has terminated.
        """
        start_time = time.time()
        while time.time() - start_time <= timeout_seconds:
            is_running, _ = self.desktop_ctrl.is_app_running(app_name)
            if not is_running:
                logger.info(f"Verification SUCCESS: App '{app_name}' has terminated.")
                return True, f"Verified: '{app_name}' process terminated."
            time.sleep(0.5)

        logger.warning(f"Verification FAILED: App '{app_name}' is still running.")
        return False, f"Verification failed: '{app_name}' is still running."

    def verify_file_exists(self, file_path_str: str) -> Tuple[bool, str]:
        """Verifies file or folder exists on disk."""
        path = Path(file_path_str)
        if path.exists():
            return True, f"Verified: Item exists at '{path.name}'."
        return False, f"Verification failed: '{path.name}' does not exist."

    def verify_file_deleted(self, file_path_str: str) -> Tuple[bool, str]:
        """Verifies file or folder has been removed from disk."""
        path = Path(file_path_str)
        if not path.exists():
            return True, f"Verified: Item '{path.name}' removed."
        return False, f"Verification failed: Item '{path.name}' still exists."
