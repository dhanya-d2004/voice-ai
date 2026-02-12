
let ws;
let audioContext;
let micStream;
let workletNode;

// ✅ START MICROPHONE
async function startMic() {

    const token = localStorage.getItem("token");
    if (!token) {
        alert("Please login first");
        return;
    }

    // ✅ Use wss if deployed on HTTPS
    const protocol = location.protocol === "https:" ? "wss" : "ws";

    ws = new WebSocket(
        `${protocol}://${location.host}/ws/mic?token=${token}`
    );

    ws.onopen = () => {
        console.log("WebSocket connected");
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
    };

    ws.onmessage = (e) => {
        try {
            const msg = JSON.parse(e.data);

            if (msg.type === "partial") {
                add("bot", msg.text);
            }

            if (msg.type === "final") {
                add("user", msg.text);
            }

        } catch (err) {
            console.error("Invalid JSON:", e.data);
        }
    };

    // 🎤 AUDIO CONFIG
    audioContext = new AudioContext({ sampleRate: 16000 });

    await audioContext.audioWorklet.addModule("/js/pcm-worklet.js");

    micStream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const source = audioContext.createMediaStreamSource(micStream);

    workletNode = new AudioWorkletNode(audioContext, "pcm-processor");

    workletNode.port.onmessage = (e) => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(e.data);
        }
    };

    source.connect(workletNode);
}
