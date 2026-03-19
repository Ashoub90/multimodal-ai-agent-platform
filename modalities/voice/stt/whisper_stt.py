import os
import sys
import numpy as np
from faster_whisper import WhisperModel

# ==========================================
# CRITICAL WINDOWS DLL & PATH INJECTION
# ==========================================
if sys.platform == "win32":
    # Identify the venv site-packages directory
    # Assumes structure: project_root/modalities/voice/stt/whisper_stt.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_base = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "venv"))
    site_packages = os.path.join(venv_base, "Lib", "site-packages")
    
    # List of every possible location for NVIDIA/CUDA DLLs in a venv
    nvidia_paths = [
        os.path.join(site_packages, "nvidia", "cublas", "bin"),
        os.path.join(site_packages, "nvidia", "cudnn", "bin"),
        os.path.join(site_packages, "nvidia", "cuda_runtime", "bin"),
        os.path.join(site_packages, "nvidia", "cublas", "lib", "x64"),
        os.path.join(site_packages, "nvidia", "cudnn", "lib", "x64"),
    ]
    
    for path in nvidia_paths:
        if os.path.exists(path):
            # For Python 3.8+, this is the required way to load DLLs
            try:
                os.add_dll_directory(path)
            except Exception:
                pass
            # Also add to system PATH for the underlying CTranslate2 binaries
            os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]

    print("🔧 System PATH updated with NVIDIA binaries.")

class WhisperSTT:
    def __init__(self):
        # We try CUDA first (RTX 2060), fallback to CPU if the DLLs still scream
        try:
            self.model = WhisperModel(
                "small", 
                device="cuda", 
                device_index=0,
                compute_type="float16"
            )
            print("✅ Whisper 'Small' active on RTX 2060 (GPU)")
        except Exception as e:
            print(f"⚠️ GPU Initialization failed: {e}")
            print("🔄 Falling back to CPU mode (int8)...")
            self.model = WhisperModel("small", device="cpu", compute_type="int8")
        
        # Egyptian slang prompts to guide the transcription
        self.initial_prompt = (
            "يا فندم، عايز أطلب، أعمل أوردر، مساعدة، شكراً، تمام، "
            "بص حضرتك، اؤمرني، مش، هنعمل، هبعت."
        )

    def transcribe(self, audio_bytes: bytes, language: str = "ar") -> str:
        """
        Transcribes raw PCM bytes to text.
        :param audio_bytes: Raw 16-bit PCM audio.
        :param language: 'ar' for Arabic, 'en' for English.
        """
        if not audio_bytes:
            return ""

        # Convert raw bytes to float32 normalized array
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        try:
            # transcription logic
            segments, info = self.model.transcribe(
                audio_data, 
                language=language, 
                task="transcribe",
                # Only use Egyptian prompts if the current UI language is Arabic
                initial_prompt=self.initial_prompt if language == "ar" else "",
                beam_size=2 
            )
            
            # Combine segments into a single string
            text = "".join([segment.text for segment in segments]).strip()
            return text
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return ""

# Test block (optional)
if __name__ == "__main__":
    stt = WhisperSTT()