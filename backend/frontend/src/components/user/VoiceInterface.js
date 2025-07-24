import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Mic, MicOff, Phone, PhoneOff, Volume2, Settings,
  Activity, Brain, Loader
} from 'lucide-react';

export default function VoiceInterface() {
  const { currentUser } = useAuth();
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);
  
  const mediaRecorder = useRef(null);
  const audioContext = useRef(null);
  const analyser = useRef(null);
  const websocket = useRef(null);

  useEffect(() => {
    // Initialize WebSocket connection
    initializeWebSocket();
    
    // Initialize audio context
    audioContext.current = new (window.AudioContext || window.webkitAudioContext)();
    
    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
      if (audioContext.current) {
        audioContext.current.close();
      }
    };
  }, []);

  function initializeWebSocket() {
    const ws = new WebSocket('wss://sovrenai.app/ws/voice');
    
    ws.onopen = () => {
      console.log('Voice WebSocket connected');
      // Send authentication
      ws.send(JSON.stringify({ 
        type: 'auth', 
        token: localStorage.getItem('sovren_token') 
      }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt reconnection after 3 seconds
      setTimeout(initializeWebSocket, 3000);
    };
    
    websocket.current = ws;
  }

  function handleWebSocketMessage(data) {
    switch (data.type) {
      case 'transcript':
        setTranscript(data.text);
        break;
      case 'response':
        setResponse(data.text);
        setIsProcessing(false);
        // Play TTS audio if provided
        if (data.audio) {
          playAudio(data.audio);
        }
        break;
      case 'processing':
        setIsProcessing(true);
        break;
      case 'error':
        console.error('Voice error:', data.message);
        setIsProcessing(false);
        break;
    }
  }

  async function startListening() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Set up audio analysis
      const source = audioContext.current.createMediaStreamSource(stream);
      analyser.current = audioContext.current.createAnalyser();
      analyser.current.fftSize = 256;
      source.connect(analyser.current);
      
      // Start audio level monitoring
      monitorAudioLevel();
      
      // Set up media recorder
      const recorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0 && websocket.current.readyState === WebSocket.OPEN) {
          // Send audio chunk to server
          websocket.current.send(event.data);
        }
      };
      
      recorder.start(100); // Send chunks every 100ms
      mediaRecorder.current = recorder;
      setIsListening(true);
      
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Please allow microphone access to use voice commands');
    }
  }

  function stopListening() {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      setIsListening(false);
      
      // Send end of speech signal
      if (websocket.current.readyState === WebSocket.OPEN) {
        websocket.current.send(JSON.stringify({ type: 'end_of_speech' }));
      }
    }
  }

  function monitorAudioLevel() {
    if (!analyser.current || !isListening) return;
    
    const dataArray = new Uint8Array(analyser.current.frequencyBinCount);
    analyser.current.getByteFrequencyData(dataArray);
    
    // Calculate average volume
    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    setAudioLevel(average / 255);
    
    requestAnimationFrame(monitorAudioLevel);
  }

  function playAudio(audioBase64) {
    const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
    audio.play();
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8 text-center">Voice Interface</h1>
        
        {/* Voice Visualization */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-3xl p-8 mb-8 border border-purple-500/20">
          <div className="flex flex-col items-center">
            {/* Audio Visualizer */}
            <div className="relative mb-8">
              <div className={`w-32 h-32 rounded-full bg-purple-600/20 flex items-center justify-center transition-all duration-300 ${
                isListening ? 'animate-pulse' : ''
              }`}>
                {isListening ? (
                  <Mic className="w-12 h-12 text-purple-400" />
                ) : (
                  <MicOff className="w-12 h-12 text-gray-400" />
                )}
              </div>
              
              {/* Audio level indicator */}
              {isListening && (
                <div className="absolute inset-0 rounded-full border-4 border-purple-400/30"
                  style={{
                    transform: `scale(${1 + audioLevel * 0.5})`,
                    opacity: audioLevel * 0.8,
                    transition: 'all 100ms'
                  }}
                />
              )}
            </div>
            
            {/* Control Button */}
            <button
              onClick={isListening ? stopListening : startListening}
              disabled={isProcessing}
              className={`px-8 py-3 rounded-full font-semibold transition-all duration-300 ${
                isListening 
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-purple-600 hover:bg-purple-700 text-white'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isListening ? 'Stop Listening' : 'Start Listening'}
            </button>
            
            {/* Status */}
            <div className="mt-4 text-center">
              {isProcessing && (
                <div className="flex items-center justify-center text-purple-400">
                  <Loader className="w-5 h-5 animate-spin mr-2" />
                  Processing...
                </div>
              )}
              {isListening && !isProcessing && (
                <div className="flex items-center justify-center text-green-400">
                  <Activity className="w-5 h-5 mr-2" />
                  Listening...
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Transcript */}
        {transcript && (
          <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 mb-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-2">You said:</h3>
            <p className="text-gray-300">{transcript}</p>
          </div>
        )}
        
        {/* Response */}
        {response && (
          <div className="bg-purple-900/20 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20">
            <div className="flex items-start space-x-3">
              <Brain className="w-6 h-6 text-purple-400 mt-1" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white mb-2">SOVREN Response:</h3>
                <p className="text-gray-300">{response}</p>
              </div>
            </div>
          </div>
        )}
        
        {/* Voice Commands Help */}
        <div className="mt-8 bg-gray-800/30 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Voice Commands</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <CommandExample
              command="What's my SOVREN score?"
              description="Check your current sovereignty score"
            />
            <CommandExample
              command="Analyze this decision..."
              description="Get PhD-level decision analysis"
            />
            <CommandExample
              command="Connect me to the CFO"
              description="Speak with Shadow Board executive"
            />
            <CommandExample
              command="Show me future scenarios"
              description="Activate Time Machine predictions"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function CommandExample({ command, description }) {
  return (
    <div className="border-l-2 border-purple-500/50 pl-3">
      <p className="text-white font-medium">"{command}"</p>
      <p className="text-gray-400 text-xs">{description}</p>
    </div>
  );
} 