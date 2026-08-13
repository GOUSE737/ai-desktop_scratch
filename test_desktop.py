import pytest
from automation.desktop_controller import DesktopController
from automation.system_controller import SystemController

def test_is_app_running():
    controller = DesktopController()
    running, pids = controller.is_app_running("python")
    assert isinstance(running, bool)
    assert isinstance(pids, list)

def test_launch_app_validation():
    controller = DesktopController()
    success, msg = controller.launch_app("non_existent_fake_app_xyz")
    assert success is False
    assert "not installed" in msg or "could not be located" in msg

def test_screenshot_generation():
    sys_ctrl = SystemController()
    success, msg = sys_ctrl.take_screenshot()
    assert success is True
    assert "saved" in msg.lower()
