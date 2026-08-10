import os
import sys
import time
import urllib.request

MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat.v1.0.q4_k_m.gguf"
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "tinyllama-1.1b-chat.Q4_K_M.gguf")

def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 10 * 1024 * 1024:
        print(f"Model already exists at: {MODEL_PATH} ({os.path.getsize(MODEL_PATH)} bytes)")
        return True

    print(f"Downloading TinyLlama GGUF model to: {MODEL_PATH}...")
    try:
        req = urllib.request.Request(MODEL_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(MODEL_PATH, "wb") as out_file:
            chunk_size = 1024 * 1024
            downloaded = 0
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                print(f"Downloaded: {downloaded / (1024*1024):.1f} MB", end="\r")
        print(f"\nModel download complete: {MODEL_PATH}")
        return True
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in download_gguf_model.py: {e}")
        print(f"Model download failed or offline: {e}")
        # Create minimal placeholder so local GGUF engine falls back cleanly
        with open(MODEL_PATH, "w", encoding="utf-8") as f:
            f.write("OFFLINE_GGUF_PLACEHOLDER")
        return False

if __name__ == "__main__":
    download_model()
