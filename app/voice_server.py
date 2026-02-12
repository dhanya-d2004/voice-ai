from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import numpy as np
import tempfile
import subprocess
import requests
from faster_whisper import WhisperModel
from app.memory import ShaktiMemory

app = FastAPI()

# ---------------- CONFIG ----------------
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3"

PIPER_BIN = "/home/ubuntu/piper/piper"
PIPER_MODEL = "/home/ubuntu/piper/en_US-lessac-medium.onnx"

# ---------------- INIT MODELS ----------------
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

# ---------------- API ENDPOINT ----------------
@app.post("/process")
async def process_audio(request: Request):

    user_id = request.headers.get("X-User-ID")
    conversation_id = request.headers.get("X-Conversation-ID")

    if not user_id or not conversation_id:
        return {"error": "Missing X-User-ID or X-Conversation-ID"}

    memory = ShaktiMemory(user_id, conversation_id)

    raw = await request.body()
    audio = np.frombuffer(raw, dtype=np.float32)

    segments, _ = whisper.transcribe(audio)
    user_text = " ".join(seg.text for seg in segments).strip()

    if not user_text:
        return {"error": "No speech detected"}

    memory.add("user", user_text)

    messages = [
        {
            "role": "system",
            "content": "You are a voice assistant. Respond clearly and briefly."
        }
    ]

    for role, content in memory.get_recent():
        messages.append({"role": role, "content": content})

    reply = ask_ollama(messages)

    memory.add("assistant", reply)

    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        subprocess.run(
            [
                PIPER_BIN,
                "--model", PIPER_MODEL,
                "--output_file", tmp.name
            ],
            input=reply,
            text=True
        )

        return StreamingResponse(
            open(tmp.name, "rb"),
            media_type="audio/wav"
        )
