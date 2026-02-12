import requests

OLLAMA_URL = "http://localhost:11434"

def ask_ollama(prompt: str) -> str:
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    r.raise_for_status()
    return r.json()["response"]

if __name__ == "__main__":
    text = "Hello, explain what a voice assistant is in one sentence."
    print("Sending to Ollama...")
    reply = ask_ollama(text)
    print("Ollama response:\n", reply)
