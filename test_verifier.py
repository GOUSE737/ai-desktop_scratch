import pytest
from core.action_verifier import ActionVerifier

def test_verify_running_process():
    verifier = ActionVerifier()
    # Check currently active Python process
    success, msg = verifier.verify_app_launched("python", timeout_seconds=1.0)
    assert success is True
    assert "Verified" in msg

def test_verify_file_existence(tmp_path):
    verifier = ActionVerifier()
    test_file = tmp_path / "sample.txt"
    
    # Pre-creation check
    s_before, _ = verifier.verify_file_exists(str(test_file))
    assert s_before is False

    # Create file
    test_file.write_text("hello")
    s_after, _ = verifier.verify_file_exists(str(test_file))
    assert s_after is True
