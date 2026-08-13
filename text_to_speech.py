import pyttsx3
import threading
import queue
from typing import Optional
from utils.logger import get_logger
from config.config_manager import get_config

logger = get_logger("TTSService")

class TTSService:
    """
    Offline Text-To-Speech engine utilizing Windows SAPI5 via pyttsx3.
    Uses a dedicated background thread and message queue to prevent blocking UI/main loop.
    """
    def __init__(self):
        self.config = get_config()
        self.speech_queue = queue.Queue()
        self._is_running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def _worker_loop(self):
        """Worker thread executing speech synthesis requests sequentially."""
        try:
            engine = pyttsx3.init("sapi5")
            rate = self.config.get_setting("voice_rate", 185)
            volume = self.config.get_setting("voice_volume", 1.0)
            engine.setProperty("rate", rate)
            engine.setProperty("volume", volume)
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 SAPI5 engine: {e}")
            engine = None

        while self._is_running:
            try:
                text = self.speech_queue.get(timeout=0.5)
                if text is None:
                    break
                
                logger.info(f"Speaking: '{text}'")
                if engine:
                    engine.say(text)
                    engine.runAndWait()
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error during TTS playback: {e}")

    def speak(self, text: str, sync: bool = False):
        """
        Enqueues text for speech synthesis.
        If sync is True, waits until speech completes.
        """
        if not text or not text.strip():
            return
        
        self.speech_queue.put(text.strip())
        if sync:
            self.speech_queue.join()

    def stop(self):
        """Stops the TTS worker thread."""
        self._is_running = False
        self.speech_queue.put(None)

_tts_instance: Optional[TTSService] = None

def get_tts() -> TTSService:
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSService()
    return _tts_instance
