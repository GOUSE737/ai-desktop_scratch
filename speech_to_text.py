import os
import io
import json
import wave
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from typing import Optional, Tuple
from utils.logger import get_logger
from config.config_manager import get_config

logger = get_logger("STTService")

class STTService:
    """
    Speech-To-Text service using sounddevice for reliable audio capture across Windows/Python 3.14,
    combined with offline Vosk or SpeechRecognition engine.
    """
    def __init__(self):
        self.config = get_config()
        self.recognizer = sr.Recognizer()
        self.timeout = self.config.get_setting("listening_timeout", 5)
        self.phrase_time_limit = self.config.get_setting("speech_phrase_limit", 10)
        self.sample_rate = 16000

    def check_microphone_available(self) -> bool:
        """Verifies if at least one audio input device is available via sounddevice."""
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d.get('max_input_channels', 0) > 0]
            if not input_devices:
                logger.warning("No input microphone devices found on system.")
                return False
            return True
        except Exception as e:
            logger.warning(f"Error checking microphone devices via sounddevice: {e}")
            return False

    def record_audio_stream(self, duration: int = 5) -> Tuple[bool, Optional[bytes]]:
        """
        Records PCM audio data from microphone using sounddevice.
        Returns (success: bool, wav_bytes: bytes).
        """
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            num_samples = int(duration * self.sample_rate)
            audio_data = sd.rec(num_samples, samplerate=self.sample_rate, channels=1, dtype='int16')
            sd.wait()

            buf = io.BytesIO()
            with wave.open(buf, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())

            buf.seek(0)
            return True, buf.getvalue()
        except Exception as e:
            logger.error(f"Failed to record audio via sounddevice: {e}")
            return False, None

    def listen_and_recognize(self, timeout: Optional[int] = None) -> Tuple[bool, str]:
        """
        Listens from microphone and transcribes audio to text.
        """
        if not self.check_microphone_available():
            return False, "Microphone is unavailable or not connected."

        record_duration = timeout or self.timeout
        success, wav_data = self.record_audio_stream(duration=record_duration)
        
        if not success or not wav_data:
            return False, "Failed to capture microphone audio."

        try:
            logger.info("Transcribing captured audio...")
            buf = io.BytesIO(wav_data)
            with sr.AudioFile(buf) as source:
                audio = self.recognizer.record(source)

            # Primary offline attempt using Vosk if model path configured
            vosk_model_path = self.config.get_setting("VOSK_MODEL_PATH", "")
            if vosk_model_path and os.path.exists(vosk_model_path):
                try:
                    text = self.recognizer.recognize_vosk(audio)
                    res = json.loads(text)
                    transcribed = res.get("text", "").strip()
                    if transcribed:
                        return True, transcribed
                except Exception as ve:
                    logger.warning(f"Vosk recognition failed, falling back: {ve}")

            # Standard SpeechRecognition fallback engine
            try:
                text = self.recognizer.recognize_google(audio).strip()
                if text:
                    logger.info(f"Transcribed Text: '{text}'")
                    return True, text
                return False, "No speech detected in audio."
            except sr.UnknownValueError:
                return False, "Could not understand audio speech. Please speak clearly into the microphone."
            except sr.RequestError as re:
                return False, f"Speech recognition service error: {re}"

        except Exception as e:
            logger.error(f"Unexpected speech recognition error: {e}")
            return False, f"Speech recognition failed: {str(e)}"
