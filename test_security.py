import pytest
from security.command_risk import CommandRiskClassifier, RiskLevel
from security.confirmation_manager import ConfirmationManager

def test_risk_classifier_tiers():
    classifier = CommandRiskClassifier()
    
    assert classifier.classify("OPEN_APP") == RiskLevel.LOW
    assert classifier.classify("WEB_SEARCH") == RiskLevel.LOW
    
    assert classifier.classify("MOVE_FILE") == RiskLevel.MEDIUM
    assert classifier.classify("RENAME_FILE") == RiskLevel.MEDIUM
    
    assert classifier.classify("DELETE_FILE") == RiskLevel.HIGH
    assert classifier.classify("SYSTEM_SHUTDOWN") == RiskLevel.HIGH

def test_confirmation_mode_requirements():
    classifier = CommandRiskClassifier()
    assert classifier.requires_confirmation("DELETE_FILE") is True
    assert classifier.requires_confirmation("SYSTEM_SHUTDOWN") is True
    assert classifier.requires_confirmation("OPEN_APP") is False

def test_affirmative_voice_responses():
    cm = ConfirmationManager()
    assert cm.is_affirmative("yes") is True
    assert cm.is_affirmative("confirm please") is True
    assert cm.is_affirmative("do it") is True
    assert cm.is_affirmative("no cancel") is False
