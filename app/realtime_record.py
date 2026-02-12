import sounddevice as sd
import numpy as np
import queue

# ---------------- CONFIG ----------------
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 0.5

SILENCE_THRESHOLD = 0.005
MAX_SILENCE_CHUNKS = 8

# --------------------------------------
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

def record_until_silence():
    recorded = []
    silence_chunks = 0
    speech_started = False

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=int(SAMPLE_RATE * CHUNK_DURATION),
        callback=audio_callback
    ):
        print("🎤 Speak now...")

        while True:
            chunk = audio_queue.get()
            rms = np.sqrt(np.mean(chunk**2))

            recorded.append(chunk)

            if rms > SILENCE_THRESHOLD:
                speech_started = True
                silence_chunks = 0
            elif speech_started:
                silence_chunks += 1

            if speech_started and silence_chunks >= MAX_SILENCE_CHUNKS:
                print("🛑 Silence detected")
                break

    return np.concatenate(recorded, axis=0).flatten()
