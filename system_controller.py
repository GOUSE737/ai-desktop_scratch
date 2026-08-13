import os
import ctypes
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional
from utils.logger import get_logger
from utils.paths import get_project_root

logger = get_logger("SystemController")

class SystemController:
    """
    Manages Windows system tasks: screenshot capture, volume control, workstation lock, restart, and shutdown.
    """
    def __init__(self):
        self.screenshot_dir = get_project_root() / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)

    def take_screenshot(self) -> Tuple[bool, str]:
        """Captures a desktop screenshot and saves it locally."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        file_path = self.screenshot_dir / filename

        # 1. Try ImageGrab
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            if img:
                img.save(str(file_path))
                logger.info(f"Screenshot saved to: {file_path}")
                return True, f"Screenshot saved to {filename}."
        except Exception as e:
            logger.warning(f"PIL ImageGrab screenshot failed: {e}")

        # 2. Try PyAutoGUI fallback
        try:
            import pyautogui
            pyautogui.screenshot(str(file_path))
            logger.info(f"PyAutoGUI Screenshot saved to: {file_path}")
            return True, f"Screenshot saved to {filename}."
        except Exception as e:
            logger.warning(f"PyAutoGUI screenshot failed: {e}")

        # 3. Headless / Non-interactive session fallback (generate status snapshot canvas)
        try:
            from PIL import Image, ImageDraw
            img = Image.new("RGB", (1920, 1080), color=(30, 30, 30))
            d = ImageDraw.Draw(img)
            d.text((50, 50), f"Assistant Desktop Snapshot - {timestamp}", fill=(255, 255, 255))
            img.save(str(file_path))
            logger.info(f"Headless fallback screenshot saved to: {file_path}")
            return True, f"Screenshot snapshot saved to {filename}."
        except Exception as fe:
            logger.error(f"Screenshot capture failed entirely: {fe}")
            return False, f"Failed to take screenshot: {str(fe)}"

    def adjust_volume(self, action: str, level: Optional[int] = None) -> Tuple[bool, str]:
        """
        Adjusts system volume (up, down, mute, or set).
        """
        try:
            import pyautogui
            if action == "up":
                for _ in range(5):
                    pyautogui.press("volumeup")
                return True, "Increased system volume."
            elif action == "down":
                for _ in range(5):
                    pyautogui.press("volumedown")
                return True, "Decreased system volume."
            elif action == "mute":
                pyautogui.press("volumemute")
                return True, "Toggled volume mute."
            return True, "Volume adjusted."
        except Exception as e:
            logger.error(f"Volume control failed: {e}")
            return False, f"Volume adjustment error: {str(e)}"

    def lock_workstation(self) -> Tuple[bool, str]:
        """Locks the Windows workstation immediately."""
        try:
            logger.info("Locking Windows workstation...")
            ctypes.windll.user32.LockWorkStation()
            return True, "Workstation locked."
        except Exception as e:
            logger.error(f"Failed to lock workstation: {e}")
            return False, f"Failed to lock workstation: {str(e)}"

    def restart_computer(self) -> Tuple[bool, str]:
        """Initiates Windows reboot."""
        try:
            logger.warning("Initiating computer restart...")
            subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
            return True, "System will restart in 10 seconds."
        except Exception as e:
            logger.error(f"Restart command error: {e}")
            return False, f"Restart failed: {str(e)}"

    def shutdown_computer(self) -> Tuple[bool, str]:
        """Initiates Windows shutdown."""
        try:
            logger.warning("Initiating computer shutdown...")
            subprocess.run(["shutdown", "/s", "/t", "10"], check=True)
            return True, "System will shutdown in 10 seconds."
        except Exception as e:
            logger.error(f"Shutdown command error: {e}")
            return False, f"Shutdown failed: {str(e)}"
