import subprocess
import requests
from faster_whisper import WhisperModel
from app.memory import ShaktiMemory

# ---------------- CONFIG ----------------
AUDIO_IN = "audio/test1.wav"
AUDIO_OUT = "audio/response.wav"

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3"

PIPER_BIN = "/home/ubuntu/piper/piper"
PIPER_MODEL = "/home/ubuntu/piper/en_US-lessac-medium.onnx"

# ---------------- STT ----------------
whisper = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

# ---------------- LLM ----------------
def ask_ollama(messages) -> str:
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False
        },
        timeout=300
    )

    r.raise_for_status()
    return r.json()["message"]["content"].strip()

# ---------------- TTS ----------------
def speak(text: str, output_path: str):
    subprocess.run(
        [
            PIPER_BIN,
            "--model", PIPER_MODEL,
            "--output_file", output_path
        ],
        input=text,
        text=True
    )

# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("Transcribing audio...")
    segments, _ = whisper.transcribe(AUDIO_IN)

    user_text = " ".join(seg.text for seg in segments).strip()
    print(f"\nYou said: {user_text}")

    memory = ShaktiMemory()
    memory.add("user", user_text)

    print("Thinking...")
    reply = ask_ollama(user_text)

    memory.add("assistant", reply)

    print(f"\nAssistant: {reply}")

    print("Generating speech...")
    speak(reply, AUDIO_OUT)

    print(f"\nDone. Saved to {AUDIO_OUT}")
