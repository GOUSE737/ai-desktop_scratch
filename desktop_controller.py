import os
import subprocess
import psutil
from typing import Optional, Tuple, List
from config.config_manager import get_config
from utils.logger import get_logger
from utils.paths import resolve_app_path

logger = get_logger("DesktopController")

try:
    import win32gui
    import win32con
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

class DesktopController:
    """
    Controls Windows desktop applications, process detection, window focus/minimize/maximize/close.
    """
    def __init__(self):
        self.config = get_config()

    def is_app_running(self, app_name_or_alias: str) -> Tuple[bool, List[int]]:
        """
        Checks if the specified application process is currently running.
        Returns (is_running: bool, list_of_pids: List[int]).
        """
        app_info = self.config.get_app_info(app_name_or_alias)
        exec_name = app_info["executable"] if app_info else f"{app_name_or_alias}.exe"
        
        pids = []
        exec_base = os.path.basename(exec_name).lower()

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name']
                if proc_name and proc_name.lower() == exec_base:
                    pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return len(pids) > 0, pids

    def launch_app(self, app_name_or_alias: str) -> Tuple[bool, str]:
        """
        Launches an application by name or alias using dynamic path resolution.
        """
        app_info = self.config.get_app_info(app_name_or_alias)
        
        if app_info and app_info.get("resolved_path"):
            target_path = app_info["resolved_path"]
        else:
            # Attempt to resolve raw name directly
            exec_name = app_info["executable"] if app_info else app_name_or_alias
            if not exec_name.endswith(".exe") and not exec_name.endswith(".cmd"):
                exec_name += ".exe"
            target_path = resolve_app_path(exec_name)

        if not target_path:
            logger.warning(f"Application '{app_name_or_alias}' could not be located in Registry or PATH.")
            return False, f"Application '{app_name_or_alias}' is not installed or path could not be resolved."

        try:
            logger.info(f"Launching application at path: '{target_path}'")
            subprocess.Popen([target_path], shell=True)
            return True, f"Application '{app_name_or_alias}' launched successfully."
        except Exception as e:
            logger.error(f"Failed to launch application '{app_name_or_alias}': {e}")
            return False, f"Failed to launch '{app_name_or_alias}': {str(e)}"

    def close_app(self, app_name_or_alias: str) -> Tuple[bool, str]:
        """
        Terminates active processes matching application name or alias.
        """
        is_running, pids = self.is_app_running(app_name_or_alias)
        if not is_running:
            return False, f"Application '{app_name_or_alias}' is not currently running."

        closed_count = 0
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                closed_count += 1
            except Exception as e:
                logger.warning(f"Could not terminate PID {pid}: {e}")

        if closed_count > 0:
            return True, f"Successfully closed '{app_name_or_alias}' ({closed_count} processes terminated)."
        return False, f"Could not close process for '{app_name_or_alias}'."

    def maximize_app_window(self, app_name_or_alias: str) -> bool:
        """Maximizes the main window of the application if running."""
        if not HAS_WIN32:
            return False

        is_running, pids = self.is_app_running(app_name_or_alias)
        if not is_running:
            return False

        def enum_windows_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid in pids:
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                    win32gui.SetForegroundWindow(hwnd)

        try:
            win32gui.EnumWindows(enum_windows_callback, None)
            return True
        except Exception as e:
            logger.error(f"Window maximize error: {e}")
            return False
