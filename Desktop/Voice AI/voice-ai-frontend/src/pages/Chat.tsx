
import { useState } from "react";

export default function Chat() {
  const [message, setMessage] = useState("");

  const startListening = () => {
    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.start();
    recognition.onresult = (event: any) => {
      setMessage(event.results[0][0].transcript);
    };
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", background: "#f3f4f6" }}>

      {/* NAVBAR */}
      <div style={{
        height: "60px",
        background: "white",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "0 30px",
        borderBottom: "1px solid #e5e7eb"
      }}>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{
            width: "40px",
            height: "40px",
            background: "#5b5ff9",
            borderRadius: "10px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontWeight: "bold"
          }}>
            AI
          </div>

          <div>
            <strong>AI Voice Assistant</strong>
            <div style={{ fontSize: "12px", color: "#6b7280" }}>
              Text, voice & file support
            </div>
          </div>
        </div>

        <div style={{ display: "flex", gap: "20px", color: "#4f46e5", fontSize: "14px" }}>
          <div>🔊 Voice on</div>
          <div style={{ cursor: "pointer" }}>Sign out</div>
        </div>
      </div>

      {/* CENTER EMPTY AREA */}
      <div style={{
        flex: 1,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        textAlign: "center",
        color: "#6b7280",
        flexDirection: "column"
      }}>

        <div style={{ fontSize: "45px" }}>🎧</div>

        <h2 style={{ marginTop: "10px", color: "#111827" }}>
          Start a conversation
        </h2>

        <p style={{ marginTop: "5px" }}>
          Type a message, use your microphone, or upload a file
          to get started.
        </p>

        <div style={{
          marginTop: "15px",
          padding: "8px 15px",
          borderRadius: "20px",
          background: "#e5e7eb",
          fontSize: "13px"
        }}>
          Supported format : .pdf,.jpg,.jpeg,.png,.wav,.mp3  <br />
          Max file size : 5 MB
        </div>
      </div>

      {/* BOTTOM INPUT BAR */}
      <div style={{
        height: "70px",
        background: "white",
        borderTop: "1px solid #e5e7eb",
        display: "flex",
        alignItems: "center",
        padding: "0 20px"
      }}>

        <div style={{ marginRight: "10px", cursor: "pointer" }}>📎</div>

        <div style={{ marginRight: "10px", cursor: "pointer" }} onClick={startListening}>
          🎤
        </div>

        <input
          type="text"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={{
            flex: 1,
            padding: "12px 18px",
            borderRadius: "25px",
            border: "1px solid #d1d5db",
            outline: "none",
            fontSize: "14px"
          }}
        />

        <div style={{
          marginLeft: "10px",
          width: "45px",
          height: "45px",
          borderRadius: "12px",
          background: "#6366f1",
          color: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer"
        }}>
          ➤
        </div>
      </div>

    </div>
  );
}
