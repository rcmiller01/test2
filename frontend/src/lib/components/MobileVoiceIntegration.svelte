<!-- MobileVoiceIntegration.svelte -->
<!-- Web-Based Voice Integration for iPhone Safari -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';

  const dispatch = createEventDispatcher();

  // Component state
  let isListening = false;
  let isSpeaking = false;
  let recognizedText = "";
  let voiceError = null;
  let voiceStatus = "idle";
  let isSupported = false;

  // Web Speech API objects
  let recognition = null;
  let synthesis = window.speechSynthesis;
  let audioContext = null;
  let mediaStream = null;

  // Voice configuration for web
  const voiceConfigs = {
    "mia": {
      voice: "Samantha", // iOS default female voice
      pitch: 1.1,
      rate: 0.8,
      volume: 0.8,
      personality: "warm_affectionate"
    },
    "solene": {
      voice: "Samantha",
      pitch: 0.9,
      rate: 0.9,
      volume: 0.9,
      personality: "sophisticated_passionate"
    },
    "lyra": {
      voice: "Samantha",
      pitch: 1.2,
      rate: 0.7,
      volume: 0.7,
      personality: "mystical_ethereal"
    },
    "doc": {
      voice: "Alex", // iOS default male voice
      pitch: 1.0,
      rate: 1.0,
      volume: 0.8,
      personality: "professional_analytical"
    }
  };

  // Initialize voice integration
  onMount(async () => {
    await initializeVoiceIntegration();
  });

  onDestroy(() => {
    cleanupVoiceIntegration();
  });

  async function initializeVoiceIntegration() {
    try {
      // Check Web Speech API support
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        throw new Error('Speech recognition not supported in this browser');
      }

      if (!('speechSynthesis' in window)) {
        throw new Error('Speech synthesis not supported in this browser');
      }

      // Initialize speech recognition
      recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      setupSpeechRecognition();

      // Initialize audio context for advanced audio features
      try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      } catch (e) {
        console.warn('AudioContext not available:', e);
      }

      isSupported = true;
      voiceStatus = "ready";
      
      console.log('[Mobile Voice Integration] Initialized successfully');
      
    } catch (error) {
      voiceError = error.message;
      voiceStatus = "error";
      console.error('[Mobile Voice Integration] Initialization failed:', error);
    }
  }

  function setupSpeechRecognition() {
    if (!recognition) return;

    // Configure recognition
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    // Event handlers
    recognition.onstart = () => {
      isListening = true;
      voiceStatus = "listening";
      voiceError = null;
      console.log('[Mobile Voice Integration] Started listening');
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      recognizedText = finalTranscript || interimTranscript;

      if (finalTranscript) {
        handleFinalRecognition(finalTranscript);
      }
    };

    recognition.onerror = (event) => {
      handleRecognitionError(event.error);
    };

    recognition.onend = () => {
      isListening = false;
      voiceStatus = "ready";
      console.log('[Mobile Voice Integration] Stopped listening');
    };
  }

  function handleRecognitionError(error) {
    isListening = false;
    voiceStatus = "error";
    
    const errorMessages = {
      'no-speech': 'No speech detected. Please try again.',
      'audio-capture': 'Microphone access denied. Please allow microphone access.',
      'not-allowed': 'Microphone access denied. Please allow microphone access.',
      'network': 'Network error. Please check your connection.',
      'service-not-allowed': 'Speech recognition service not available.',
      'bad-grammar': 'Speech recognition grammar error.',
      'language-not-supported': 'Language not supported.'
    };

    voiceError = errorMessages[error] || `Recognition error: ${error}`;
    console.error('[Mobile Voice Integration] Recognition error:', error);
  }

  function handleFinalRecognition(text) {
    if (!text.trim()) return;

    // Send to backend API
    sendRecognizedText(text);
    
    // Clear recognized text
    recognizedText = "";
  }

  async function sendRecognizedText(text) {
    try {
      const response = await fetch('/api/voice/input', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          persona: $currentPersona,
          timestamp: Date.now(),
          platform: 'web_mobile'
        })
      });

      if (response.ok) {
        const result = await response.json();
        handleVoiceResponse(result);
      } else {
        throw new Error(`API error: ${response.status}`);
      }
    } catch (error) {
      voiceError = `Failed to send voice input: ${error.message}`;
      console.error('[Mobile Voice Integration] API error:', error);
    }
  }

  function handleVoiceResponse(response) {
    // Speak the response if provided
    if (response.speech_text) {
      speak(response.speech_text, response.persona);
    }

    // Update persona if changed
    if (response.persona && response.persona !== $currentPersona) {
      // This would update the persona store
      console.log('[Mobile Voice Integration] Persona changed to:', response.persona);
    }

    // Handle additional actions
    if (response.actions) {
      handleVoiceActions(response.actions);
    }
  }

  function handleVoiceActions(actions) {
    actions.forEach(action => {
      switch (action.type) {
        case 'mood_change':
          console.log('[Mobile Voice Integration] Mood change:', action.parameters);
          break;
        case 'scene_trigger':
          console.log('[Mobile Voice Integration] Scene trigger:', action.parameters);
          break;
        case 'memory_store':
          console.log('[Mobile Voice Integration] Memory store:', action.parameters);
          break;
        default:
          console.log('[Mobile Voice Integration] Unknown action:', action.type);
      }
    });
  }

  // Start listening
  function startListening() {
    if (!isSupported || isListening) return;

    try {
      // Request microphone permission
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          mediaStream = stream;
          recognition.start();
        })
        .catch(error => {
          voiceError = 'Microphone access denied. Please allow microphone access.';
          voiceStatus = "error";
          console.error('[Mobile Voice Integration] Microphone error:', error);
        });
    } catch (error) {
      voiceError = `Failed to start listening: ${error.message}`;
      voiceStatus = "error";
    }
  }

  // Stop listening
  function stopListening() {
    if (!isListening) return;

    if (recognition) {
      recognition.stop();
    }

    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
      mediaStream = null;
    }
  }

  // Speak text
  function speak(text, persona = null) {
    if (!text || isSpeaking) return;

    const targetPersona = persona || $currentPersona;
    const config = voiceConfigs[targetPersona] || voiceConfigs["mia"];

    // Stop any ongoing speech
    synthesis.cancel();

    // Create speech utterance
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set voice properties
    utterance.voice = getVoiceByName(config.voice);
    utterance.pitch = config.pitch;
    utterance.rate = config.rate;
    utterance.volume = config.volume;

    // Add persona-specific speech patterns
    applyPersonaSpeechPatterns(utterance, targetPersona);

    // Event handlers
    utterance.onstart = () => {
      isSpeaking = true;
      voiceStatus = "speaking";
      voiceError = null;
      console.log('[Mobile Voice Integration] Speaking:', text);
    };

    utterance.onend = () => {
      isSpeaking = false;
      voiceStatus = "ready";
    };

    utterance.onerror = (event) => {
      isSpeaking = false;
      voiceStatus = "error";
      voiceError = `Speech synthesis error: ${event.error}`;
      console.error('[Mobile Voice Integration] Speech error:', event);
    };

    // Start speaking
    synthesis.speak(utterance);
  }

  function stopSpeaking() {
    if (synthesis.speaking) {
      synthesis.cancel();
    }
    isSpeaking = false;
    voiceStatus = "ready";
  }

  function getVoiceByName(name) {
    const voices = synthesis.getVoices();
    return voices.find(voice => voice.name === name) || voices[0];
  }

  function applyPersonaSpeechPatterns(utterance, persona) {
    switch (persona) {
      case "mia":
        // Warm, affectionate patterns
        utterance.pitch *= 1.1;
        utterance.rate *= 0.9;
        break;
      case "solene":
        // Sophisticated, passionate patterns
        utterance.pitch *= 0.95;
        utterance.rate *= 1.1;
        break;
      case "lyra":
        // Mystical, ethereal patterns
        utterance.pitch *= 1.2;
        utterance.rate *= 0.8;
        break;
      case "doc":
        // Professional, analytical patterns
        utterance.pitch *= 1.0;
        utterance.rate *= 1.2;
        break;
    }
  }

  function cleanupVoiceIntegration() {
    stopListening();
    stopSpeaking();
    
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
    }
    
    if (audioContext) {
      audioContext.close();
    }
  }

  function resetVoiceError() {
    voiceError = null;
    if (!isListening && !isSpeaking) {
      voiceStatus = "ready";
    }
  }

  // Handle voice button click
  function toggleVoice() {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }

  // Handle test speech
  function testSpeech() {
    const testText = `Hello, I'm ${$currentPersonaConfig?.name || 'your companion'}. How can I help you today?`;
    speak(testText);
  }
</script>

<div class="mobile-voice-integration">
  <!-- Error Display -->
  {#if voiceError}
    <div class="voice-error">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{voiceError}</span>
      <button class="error-close" on:click={resetVoiceError}>×</button>
    </div>
  {/if}

  <!-- Voice Controls -->
  <div class="voice-controls">
    <!-- Main Voice Button -->
    <button 
      class="voice-button {isListening ? 'listening' : ''} {isSpeaking ? 'speaking' : ''}"
      on:click={toggleVoice}
      disabled={!isSupported || isSpeaking}
      title={isListening ? 'Stop Listening' : 'Start Listening'}
    >
      {#if isListening}
        <span class="voice-icon listening">🎤</span>
        <span class="voice-text">Listening...</span>
      {:else if isSpeaking}
        <span class="voice-icon speaking">🔊</span>
        <span class="voice-text">Speaking...</span>
      {:else}
        <span class="voice-icon">🎤</span>
        <span class="voice-text">Voice</span>
      {/if}
    </button>

    <!-- Test Speech Button -->
    <button 
      class="test-button"
      on:click={testSpeech}
      disabled={!isSupported || isSpeaking || isListening}
      title="Test Speech"
    >
      🔊 Test
    </button>
  </div>

  <!-- Recognition Display -->
  {#if isListening && recognizedText}
    <div class="recognition-display">
      <div class="recognition-label">Recognizing:</div>
      <div class="recognition-text">{recognizedText}</div>
    </div>
  {/if}

  <!-- Status Display -->
  <div class="voice-status">
    <span class="status-label">Status:</span>
    <span class="status-value {voiceStatus}">{voiceStatus}</span>
  </div>

  <!-- Support Warning -->
  {#if !isSupported}
    <div class="support-warning">
      <span class="warning-icon">⚠️</span>
      <span class="warning-text">
        Voice features require a modern browser with microphone access.
        Please use Safari on iOS or Chrome on Android.
      </span>
    </div>
  {/if}
</div>

<style>
  .mobile-voice-integration {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 12px;
    margin: 1rem 0;
  }

  .voice-error {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 8px;
    padding: 0.75rem;
    margin-bottom: 1rem;
  }

  .error-icon {
    font-size: 1.2rem;
  }

  .error-text {
    color: #721c24;
    font-size: 0.875rem;
    flex: 1;
  }

  .error-close {
    background: none;
    border: none;
    color: #721c24;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
  }

  .voice-controls {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .voice-button {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 1rem;
    border: 2px solid #007bff;
    border-radius: 12px;
    background: white;
    cursor: pointer;
    transition: all 0.3s ease;
    min-height: 80px;
  }

  .voice-button:hover:not(:disabled) {
    background: #e3f2fd;
    transform: translateY(-2px);
  }

  .voice-button.listening {
    border-color: #dc3545;
    background: #f8d7da;
    animation: pulse 1.5s infinite;
  }

  .voice-button.speaking {
    border-color: #28a745;
    background: #d4edda;
  }

  .voice-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .voice-icon {
    font-size: 2rem;
  }

  .voice-icon.listening {
    animation: pulse 1.5s infinite;
  }

  .voice-icon.speaking {
    animation: wave 1s infinite;
  }

  .voice-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: #495057;
  }

  .test-button {
    padding: 0.5rem 1rem;
    border: 1px solid #6c757d;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 0.875rem;
    transition: all 0.2s ease;
  }

  .test-button:hover:not(:disabled) {
    background: #f8f9fa;
  }

  .test-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .recognition-display {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .recognition-label {
    font-size: 0.875rem;
    color: #6c757d;
    margin-bottom: 0.5rem;
  }

  .recognition-text {
    font-size: 1rem;
    color: #495057;
    line-height: 1.4;
  }

  .voice-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
  }

  .status-label {
    color: #6c757d;
  }

  .status-value {
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    text-transform: uppercase;
  }

  .status-value.ready {
    background: #d4edda;
    color: #155724;
  }

  .status-value.listening {
    background: #f8d7da;
    color: #721c24;
  }

  .status-value.speaking {
    background: #d1ecf1;
    color: #0c5460;
  }

  .status-value.error {
    background: #f8d7da;
    color: #721c24;
  }

  .status-value.unauthorized {
    background: #fff3cd;
    color: #856404;
  }

  .support-warning {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 8px;
    padding: 0.75rem;
    margin-top: 1rem;
  }

  .warning-icon {
    font-size: 1.2rem;
  }

  .warning-text {
    color: #856404;
    font-size: 0.875rem;
    line-height: 1.4;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  @keyframes wave {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }

  /* Mobile Optimizations */
  @media (max-width: 768px) {
    .voice-controls {
      flex-direction: column;
    }

    .voice-button {
      min-height: 60px;
    }

    .voice-icon {
      font-size: 1.5rem;
    }
  }
</style> 