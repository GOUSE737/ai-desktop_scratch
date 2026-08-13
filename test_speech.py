import pytest
import time
from speech.text_to_speech import TTSService
from speech.speech_to_text import STTService
from speech.wake_word import WakeWordDetector

def test_wake_word_detector():
    detector = WakeWordDetector()
    assert detector.contains_wake_word("Jarvis open Chrome") is True
    assert detector.contains_wake_word("Hey jarvis please help") is True
    assert detector.contains_wake_word("Open Chrome") is False
    
    assert detector.strip_wake_word("Jarvis open Chrome") == "open chrome"

def test_stt_mic_check():
    stt = STTService()
    # Ensure checking microphone device list does not throw unhandled exceptions
    avail = stt.check_microphone_available()
    assert isinstance(avail, bool)

def test_tts_non_blocking():
    tts = TTSService()
    # Non-blocking call should return immediately
    tts.speak("Testing text to speech service", sync=False)
    time.sleep(0.5)
    tts.stop()
