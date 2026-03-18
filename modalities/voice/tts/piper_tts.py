import io
import wave
import os
from piper.voice import PiperVoice

class PiperTTS:
    def __init__(self, model_path):
        # 1. Setup the DLL directory for Windows
        current_file_path = os.path.abspath(__file__)
        # Adjusting path to find the 'Piper' folder in your project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))))
        piper_bin_path = os.path.join(project_root, "Piper")

        if os.path.exists(piper_bin_path):
            os.environ["PATH"] = piper_bin_path + os.pathsep + os.environ["PATH"]
            if hasattr(os, 'add_dll_directory'):
                try:
                    os.add_dll_directory(piper_bin_path)
                except Exception:
                    pass 

        # 2. Load the voice
        # We ensure the path is absolute for Windows stability
        self.voice = PiperVoice.load(os.path.abspath(model_path))

    async def synthesize(self, text: str):
        if not text.strip():
            return b""
            
        buffer = io.BytesIO()
        
        # 3. Use synthesize_wav as suggested by the error
        # This method handles the WAV header and the writing in one go
        with wave.open(buffer, "wb") as wav_file:
            # We pass the wav_file object directly
            self.voice.synthesize_wav(text, wav_file)
            
        audio_bytes = buffer.getvalue()
        print(f"DEBUG: Generated {len(audio_bytes)} bytes")
        return audio_bytes