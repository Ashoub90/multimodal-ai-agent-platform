import React, { useRef, useState } from "react";

function VoiceStreamer() {
  const ws = useRef(null);
  const audioContext = useRef(null);
  const audioQueue = useRef([]);
  const isPlaying = useRef(false);

  const [recording, setRecording] = useState(false);
  const [messages, setMessages] = useState([]);
  const [selectedLang, setSelectedLang] = useState(null);

  const playNextInQueue = async () => {
    if (audioQueue.current.length === 0) {
      isPlaying.current = false;
      return;
    }
    isPlaying.current = true;
    const { bytes } = audioQueue.current.shift();
    try {
      const audioBuffer = await audioContext.current.decodeAudioData(bytes.buffer);
      const source = audioContext.current.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.current.destination);
      source.onended = () => playNextInQueue();
      source.start(0);
    } catch (err) {
      console.error("Decoding error:", err);
      playNextInQueue();
    }
  };

  const startStreaming = async (lang) => {
    setSelectedLang(lang);
    if (!audioContext.current) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      audioContext.current = new AudioContextClass({ sampleRate: 16000 });
    }
    if (audioContext.current.state === 'suspended') await audioContext.current.resume();

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    ws.current = new WebSocket("ws://localhost:8000/ws/voice");

    ws.current.onopen = () => {
      // Send the language choice immediately upon connection
      ws.current.send(JSON.stringify({ type: "set_language", value: lang }));
    };

    ws.current.onmessage = async (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "transcript" || message.type === "assistant_audio_chunk") {
        setMessages((prev) => [...prev, message]);
      }

      if (message.type === "assistant_audio_chunk") {
        const binaryString = window.atob(message.audio);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        audioQueue.current.push({ bytes, index: message.index });
        audioQueue.current.sort((a, b) => a.index - b.index);
        if (!isPlaying.current) playNextInQueue();
      }
    };

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
    setSelectedLang(null);
    audioQueue.current = [];
    isPlaying.current = false;
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h2>Premium Cairo AI Assistant</h2>
      {!recording ? (
        <div style={{ display: "flex", gap: "10px", justifyContent: "center" }}>
          <button onClick={() => startStreaming("ar")} style={{ padding: "10px 20px", fontSize: "16px" }}>
            Speak Arabic (العربية)
          </button>
          <button onClick={() => startStreaming("en")} style={{ padding: "10px 20px", fontSize: "16px" }}>
            Speak English
          </button>
        </div>
      ) : (
        <button onClick={stopStreaming} style={{ backgroundColor: "red", color: "white", padding: "10px 20px" }}>
          Stop ({selectedLang === "ar" ? "Arabic" : "English"})
        </button>
      )}

      <div style={{ marginTop: "20px", border: "1px solid #ccc", padding: "10px", minHeight: "200px" }}>
        {messages
          .filter((msg) => msg.type === "transcript" || (msg.type === "assistant_audio_chunk" && msg.text))
          .map((msg, index) => (
            <p key={index}>
              <strong>{msg.type === "transcript" ? "You:" : "AI:"}</strong> {msg.text}
            </p>
          ))}
      </div>
    </div>
  );
}

export default VoiceStreamer;