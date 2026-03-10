import React, { useRef, useState } from "react";

function VoiceStreamer() {
  const ws = useRef(null);
  const audioContext = useRef(null);

  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");

  const startStreaming = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    ws.current = new WebSocket("ws://localhost:8000/ws/voice");
    ws.current.binaryType = "arraybuffer";

    // Receive transcript from backend
    ws.current.onmessage = (event) => {
      setTranscript(event.data);
    };

    audioContext.current = new (window.AudioContext || window.webkitAudioContext)({
      sampleRate: 16000,
    });

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

      <p>Transcript: {transcript}</p>
    </div>
  );
}

export default VoiceStreamer;