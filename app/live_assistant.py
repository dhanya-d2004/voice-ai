import numpy as np
import requests
import subprocess
from faster_whisper import WhisperModel

from realtime_record import record_until_silence
from memory import ShaktiMemory

# ---------------- CONFIG ----------------
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral"   # fast & ideal for voice

PIPER_BIN = "/home/ubuntu/piper/piper"
PIPER_MODEL = "/home/ubuntu/piper/en_US-lessac-medium.onnx"

# ---------------- STT ----------------
whisper = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

# ---------------- LLM (STREAMING) ----------------
def ask_ollama(prompt: str) -> str:
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": True
        },
        stream=True,
        timeout=None
    )

    full_response = ""

    for line in r.iter_lines():
        if not line:
            continue

        data = line.decode("utf-8")
        try:
            chunk = __import__("json").loads(data)
        except Exception:
            continue

        if "response" in chunk:
            full_response += chunk["response"]

        if chunk.get("done"):
            break

    return full_response.strip()

# ---------------- PROMPT BUILDER ----------------
def build_prompt(memory, user_text):
    prompt = (
        "You are a voice assistant. "
        "Respond clearly and briefly in 2–4 sentences.\n\n"
    )

    for role, content in memory:
        prompt += f"{role.upper()}: {content}\n"

    prompt += f"USER: {user_text}\nASSISTANT:"
    return prompt

# ---------------- TTS ----------------
def speak(text: str):
    p = subprocess.Popen(
        [
            PIPER_BIN,
            "--model", PIPER_MODEL,
            "--output_file", "response.wav"
        ],
        stdin=subprocess.PIPE,
        text=True
    )
    p.communicate(text)

# ---------------- MAIN LOOP ----------------
if __name__ == "__main__":
    print("🤖 Live voice assistant started")
    print("Press CTRL+C to stop\n")

    memory = ShaktiMemory()

    try:
        while True:
            print("🎤 Listening...")
            audio = record_until_silence()

            print("🧠 Transcribing...")
            segments, _ = whisper.transcribe(audio)
            user_text = " ".join(seg.text for seg in segments).strip()

            if not user_text:
                print("⚠️ No speech detected, retrying...\n")
                continue

            print(f"\n🧑 You said: {user_text}")

            memory.add("user", user_text)

            prompt = build_prompt(memory.get_recent(), user_text)

            print("🤖 Thinking...")
            reply = ask_ollama(prompt)

            print(f"\n🤖 Assistant: {reply}\n")

            memory.add("assistant", reply)

            print("🔊 Speaking...\n")
            speak(reply)

    except KeyboardInterrupt:
        print("\n👋 Stopped. Goodbye!")
