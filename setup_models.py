import os
import urllib.request

# Configuration
MODEL_DIR = "modalities/voice/tts"
MODEL_NAME = "en_US-lessac-medium.onnx"
BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium"

def download_file(url, dest):
    if os.path.exists(dest):
        print(f"✅ Already exists: {dest}")
        return
    
    print(f"📥 Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"✨ Successfully downloaded to {dest}")
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")

def main():
    # Ensure the directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Files to download
    files = [MODEL_NAME, f"{MODEL_NAME}.json"]

    for file in files:
        url = f"{BASE_URL}/{file}"
        dest = os.path.join(MODEL_DIR, file)
        download_file(url, dest)

if __name__ == "__main__":
    main()