# =========================
# Imports
# =========================
import os
import uuid
import time
import json
import io
import tempfile
import subprocess
import numpy as np
import requests

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path

from backend.auth.password import hash_password, verify_password
from backend.auth.jwt import create_access_token, get_current_user
from backend.database import get_db, engine, Base
from backend.models.user import User

from faster_whisper import WhisperModel
from pypdf import PdfReader
from docx import Document

from app.memory import ShaktiMemory

# =========================
# App & DB Init
# =========================
app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Config
# =========================
BASE_DIR = Path(__file__).resolve().parent

AUDIO_IN_DIR = BASE_DIR / "audio/input"
AUDIO_OUT_DIR = BASE_DIR / "audio/output"

AUDIO_IN_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_OUT_DIR.mkdir(parents=True, exist_ok=True)

OLLAMA_URL = "http://l3.111.150.23:11434/api/chat"
OLLAMA_MODEL = "llama3"

PIPER_BIN = "/home/ubuntu/piper/piper"
PIPER_MODEL = "/home/ubuntu/piper/en_US-lessac-medium.onnx"

# =========================
# Whisper
# =========================
whisper = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

# =========================
# LLM (Ollama Chat API)
# =========================
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

# =========================
# TTS
# =========================
def speak(text: str, output_file: Path):
    process = subprocess.Popen(
        [
            PIPER_BIN,
            "--model", PIPER_MODEL,
            "--output_file", str(output_file)
        ],
        stdin=subprocess.PIPE,
        text=True
    )
    process.communicate(text)

# =========================
# Request Schemas
# =========================
class SignupRequest(BaseModel):
    username: str
    password: str

class TextChatRequest(BaseModel):
    text: str
    conversation_id: str

# =========================
# Helpers
# =========================
def build_messages(memory, user_text: str):
    messages = [
        {
            "role": "system",
            "content": "You are a voice assistant. Respond clearly and briefly in 2–4 sentences."
        }
    ]

    for role, content in memory.get_recent():
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_text})

    return messages

def extract_text_from_document(file: UploadFile) -> str:
    name = file.filename.lower()

    if name.endswith(".txt"):
        return file.file.read().decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        reader = PdfReader(file.file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if name.endswith(".docx"):
        doc = Document(io.BytesIO(file.file.read()))
        return "\n".join(p.text for p in doc.paragraphs)

    raise HTTPException(status_code=400, detail="Unsupported document type")

# =========================
# Auth Endpoints
# =========================
@app.post("/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(400, "User already exists")

    user = User(
        username=req.username,
        password_hash=hash_password(req.password)
    )

    db.add(user)
    db.commit()

    return {"message": "Signup successful"}

@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    username = body.get("username")
    password = body.get("password")

    if not username or not password:
        raise HTTPException(400, "Username and password required")

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# =========================
# TEXT CHAT
# =========================
@app.post("/text-chat")
async def text_chat(
    req: TextChatRequest,
    username: str = Depends(get_current_user)
):
    user_text = req.text.strip()

    if not user_text:
        raise HTTPException(400, "Empty message")

    memory = ShaktiMemory(username, req.conversation_id)

    memory.add("user", user_text)

    messages = build_messages(memory, user_text)
    reply = ask_ollama(messages)

    memory.add("assistant", reply)

    memory.close()

    return {"reply": reply}

# =========================
# VOICE CHAT
# =========================
@app.post("/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    conversation_id: str = Form(...),
    username: str = Depends(get_current_user)
):
    if not audio.filename.endswith(".wav"):
        raise HTTPException(400, "Only WAV files supported")

    uid = uuid.uuid4().hex
    input_path = AUDIO_IN_DIR / f"{uid}.wav"
    output_path = AUDIO_OUT_DIR / f"{uid}_response.wav"

    with open(input_path, "wb") as f:
        f.write(await audio.read())

    segments, _ = whisper.transcribe(str(input_path))
    user_text = " ".join(seg.text for seg in segments).strip()

    if not user_text:
        raise HTTPException(400, "No speech detected")

    memory = ShaktiMemory(username, conversation_id)

    memory.add("user", user_text)

    messages = build_messages(memory, user_text)
    reply = ask_ollama(messages)

    memory.add("assistant", reply)
    speak(reply, output_path)

    memory.close()

    return {
        "transcript": user_text,
        "reply": reply,
        "audio_url": f"/audio/{output_path.name}"
    }

# =========================
# DOC CHAT
# =========================
@app.post("/doc-chat")
async def doc_chat(
    document: UploadFile = File(...),
    conversation_id: str = Form(...),
    username: str = Depends(get_current_user)
):
    doc_text = extract_text_from_document(document)

    if not doc_text.strip():
        raise HTTPException(400, "Document is empty")

    doc_text = doc_text[:4000]

    memory = ShaktiMemory(username, conversation_id)

    memory.add("user", f"[Document uploaded: {document.filename}]")

    messages = [
        {
            "role": "system",
            "content": "Answer the user's questions based ONLY on the document."
        },
        {
            "role": "user",
            "content": doc_text
        }
    ]

    reply = ask_ollama(messages)
    memory.add("assistant", reply)

    memory.close()

    return {"reply": reply}

# =========================
# Serve Audio
# =========================
@app.get("/audio/{filename}")
def get_audio(
    filename: str,
    username: str = Depends(get_current_user)
):
    file_path = AUDIO_OUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(404, "Audio not found")

    return FileResponse(
        path=file_path,
        media_type="audio/wav",
        filename=filename
    )
@app.post("/process-voice")
async def process_voice(request: Request):
    # Headers for session tracking
    user_id = request.headers.get("X-User-ID", "default_user")
    conversation_id = request.headers.get("X-Conversation-ID", "default_conv")
    
    memory = ShaktiMemory(user_id, conversation_id)

    # Receive raw audio from local computer
    raw_audio = await request.body()
    audio_data = np.frombuffer(raw_audio, dtype=np.float32)

    # 1. STT (Whisper)
    segments, _ = whisper.transcribe(audio_data)
    user_text = " ".join(seg.text for seg in segments).strip()
    
    if not user_text:
        return {"error": "No speech detected"}

    memory.add("user", user_text)

    # 2. LLM (Ollama)
    messages = [{"role": "system", "content": "You are a brief voice assistant."}]
    for role, content in memory.get_recent():
        messages.append({"role": role, "content": content})
    
    reply = ask_ollama(messages)
    memory.add("assistant", reply)

    # 3. TTS (Piper)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        subprocess.run(
            [PIPER_BIN, "--model", PIPER_MODEL, "--output_file", tmp.name],
            input=reply,
            text=True
        )
        
        return StreamingResponse(open(tmp.name, "rb"), media_type="audio/wav")
@app.get("/health")
def health():
    return {"status": "ok"}
