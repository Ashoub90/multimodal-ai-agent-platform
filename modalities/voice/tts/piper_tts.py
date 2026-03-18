import os
import io
import wave
from piper.voice import PiperVoice
from .base_tts import BaseTTS
import numpy as np

class PiperTTS(BaseTTS):
    def __init__(self, default_model_path):
        self._setup_windows_dll()
        self.model_dir = os.path.dirname(os.path.abspath(default_model_path))
        
        # Pre-load for instant switching
        self.voices = {
            "en": PiperVoice.load(os.path.abspath(default_model_path)),
            "ar": self._load_arabic_if_exists()
        }
        self.current_lang = "en"

    def _setup_windows_dll(self):
            import os
            current_file_path = os.path.abspath(__file__)
            # This points to the "Piper" folder in your root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))))
            piper_bin_path = os.path.join(project_root, "Piper")
            espeak_data_path = os.path.join(piper_bin_path, "espeak-ng-data")

            if os.path.exists(piper_bin_path):
                # Tell Piper where the phoneme dictionary is (CRITICAL for Arabic)
                os.environ["ESPEAK_DATA_PATH"] = espeak_data_path
                os.environ["PATH"] = piper_bin_path + os.pathsep + os.environ["PATH"]
                
                if hasattr(os, 'add_dll_directory'):
                    try:
                        os.add_dll_directory(piper_bin_path)
                    except Exception:
                        pass

    def _load_arabic_if_exists(self):
        ar_path = os.path.join(self.model_dir, "ar_JO-kareem-medium.onnx")
        if os.path.exists(ar_path):
            return PiperVoice.load(ar_path)
        return None

    def set_language(self, language_code: str):
        if language_code in self.voices and self.voices[language_code]:
            self.current_lang = language_code

    async def synthesize(self, text: str):
            import numpy as np
            if not text.strip(): return b""
                
            buffer = io.BytesIO()
            voice_to_use = self.voices.get(self.current_lang)
            if not voice_to_use:
                return b""
                
            voice_to_use.config.length_scale = 0.85 

            with wave.open(buffer, "wb") as wav_file:
                wav_file.setnchannels(1) 
                wav_file.setsampwidth(2) 
                wav_file.setframerate(voice_to_use.config.sample_rate)
                
                for result in voice_to_use.synthesize(text):
                    # 1. Check if we have the float array (which we saw in your log)
                    if hasattr(result, "audio_float_array") and result.audio_float_array is not None:
                        # Convert float32 (-1.0 to 1.0) to int16 (-32768 to 32767)
                        audio_int16 = (result.audio_float_array * 32767).astype(np.int16)
                        wav_file.writeframes(audio_int16.tobytes())
                    
                    # 2. Fallback: Check for the int16 array if it exists
                    elif hasattr(result, "audio_int16_array") and result.audio_int16_array is not None:
                        wav_file.writeframes(np.array(result.audio_int16_array, dtype=np.int16).tobytes())
                    
            return buffer.getvalue()