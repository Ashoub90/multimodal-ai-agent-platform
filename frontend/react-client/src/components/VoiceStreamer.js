import React, { useRef, useState } from "react";

function VoiceStreamer() {
  const ws = useRef(null);
  const audioContext = useRef(null);

  const [recording, setRecording] = useState(false);
  const [messages, setMessages] = useState([]);

  const startStreaming = async () => {
      // 1. Create/Resume context immediately on click
      if (!audioContext.current) {
          const AudioContextClass = window.AudioContext || window.webkitAudioContext;
          audioContext.current = new AudioContextClass({ sampleRate: 16000 });
      }
      
      if (audioContext.current.state === 'suspended') {
          await audioContext.current.resume();
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    ws.current = new WebSocket("ws://localhost:8000/ws/voice");
    ws.current.binaryType = "arraybuffer";

    ws.current.onmessage = async (event) => {
      const message = JSON.parse(event.data);

      // Keep your existing message list update
      setMessages((prev) => [...prev, message]);

      if (message.type === "assistant_audio") {
        try {
          // 1. Convert Base64 string to a binary string
          const binaryString = window.atob(message.audio);
          
          // --- DEBUGGING LOGS ---
          console.log("Audio byte length:", binaryString.length);
          console.log("First 4 bytes (Should be RIFF):", binaryString.substring(0, 4));

          // 2. Check for empty header (The 44-byte error)
          if (binaryString.length <= 44) {
            console.error("AI sent an empty audio header (44 bytes). Check backend Piper synthesis.");
            return;
          }

          // 3. Check for valid WAV format
          if (binaryString.substring(0, 4) !== "RIFF") {
            console.error("ERROR: Received audio data is missing WAV header!");
            return;
          }

          // 4. Convert to ArrayBuffer for the AudioContext
          const len = binaryString.length;
          const bytes = new Uint8Array(len);
          for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
          }

          // 5. Decode and Play
          // Ensure audioContext.current is resumed/initialized
          const audioBuffer = await audioContext.current.decodeAudioData(bytes.buffer);
          const source = audioContext.current.createBufferSource();
          source.buffer = audioBuffer;
          source.connect(audioContext.current.destination);
          source.start(0);

        } catch (err) {
          console.error("Audio Context playback failed:", err);
        }
      }
    };

    // ✅ CREATE AUDIO CONTEXT
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    audioContext.current = new AudioContextClass({ sampleRate: 16000 });

    const source = audioContext.current.createMediaStreamSource(stream);
    const processor = audioContext.current.createScriptProcessor(4096, 1, 1);

    source.connect(processor);
    processor.connect(audioContext.current.destination);

    processor.onaudioprocess = (e) => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        const inputData = e.inputBuffer.getChannelData(0);

        const pcmData = new Int16Array(inputData.length);

        for (let i = 0; i < inputData.length; i++) {
          pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7fff;
        }

        ws.current.send(pcmData.buffer);
      }
    };

    setRecording(true);
  };

  const stopStreaming = () => {
    if (audioContext.current) audioContext.current.close();
    if (ws.current) ws.current.close();
    setRecording(false);
  };

  return (
    <div>
      <h2>Voice Streaming (PCM)</h2>

      {!recording ? (
        <button onClick={startStreaming}>Start Mic</button>
      ) : (
        <button onClick={stopStreaming}>Stop Mic</button>
      )}

      <div style={{ marginTop: "20px" }}>
        {messages
          .filter((msg) => msg.type === "transcript" || msg.type === "assistant")
          .map((msg, index) => (
            <p key={index}>
              {msg.type === "transcript" && <strong>You:</strong>}
              {msg.type === "assistant" && <strong>AI:</strong>} {msg.text}
            </p>
          ))}
      </div>
    </div>
  );
}

export default VoiceStreamer;