import sounddevice as sd
import numpy as np
import requests
import io
import soundfile as sf

# --- CONFIGURATION ---
EC2_PUBLIC_IP = "13.233.92.226"
URL = f"http://{EC2_PUBLIC_IP}:8000/process-voice"
SAMPLE_RATE = 16000
DURATION = 5  # seconds

def record_and_send():
    print("🎤 Recording for 5 seconds...")

    # Record mono audio (shape: [N])
    recording = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    # Flatten (N,1) -> (N,)
    recording = recording.squeeze()

    # Encode as REAL WAV
    wav_buffer = io.BytesIO()
    sf.write(
        wav_buffer,
        recording,
        SAMPLE_RATE,
        format="WAV",
        subtype="FLOAT"
    )
    wav_buffer.seek(0)

    files = {
        "audio": ("recording.wav", wav_buffer.read(), "audio/wav")
    }

    headers = {
        "X-User-ID": "local_user_01",
        "X-Conversation-ID": "session_abc_123",
        "Connection": "close"
    }

    # Disable retries
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=0)
    session.mount("http://", adapter)

    print("🚀 Sending to EC2 Cloud...")
    try:
        response = session.post(
            URL,
            files=files,
            headers=headers,
            timeout=180
        )

        if response.status_code == 200:
            print("🔊 Playing Assistant Response...")
            audio_out, fs = sf.read(io.BytesIO(response.content))
            sd.play(audio_out, fs)
            sd.wait()
            print("✅ Done.\n")
        else:
            print(f"❌ Server Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"⚠️ Connection failed: {e}")

if __name__ == "__main__":
    print(f"Connected to: {URL}")
    while True:
        input("Press [Enter] to start talking...")
        record_and_send()
