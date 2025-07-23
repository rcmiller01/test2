<!-- EmotionalTTSInterface.svelte -->
<!-- Comprehensive Emotional TTS Interface with iPhone Integration -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';

  const dispatch = createEventDispatcher();

  // TTS State
  let isSpeaking = false;
  let isListening = false;
  let currentAudio = null;
  let audioQueue = [];
  let synthesisSupported = false;
  let recognitionSupported = false;

  // Voice Configuration
  let voiceConfig = {
    text: "",
    emotion: "neutral",
    intensity: 50,
    speed: 1.0,
    pitch: 1.0,
    volume: 0.8,
    persona: $currentPersona
  };

  // Available emotions and their characteristics
  const emotions = {
    neutral: { color: "#6c757d", icon: "😐", description: "Calm and balanced" },
    happy: { color: "#ffc107", icon: "😊", description: "Joyful and cheerful" },
    sad: { color: "#17a2b8", icon: "😢", description: "Melancholic and tender" },
    excited: { color: "#fd7e14", icon: "🤩", description: "Energetic and enthusiastic" },
    romantic: { color: "#e83e8c", icon: "💕", description: "Loving and intimate" },
    passionate: { color: "#dc3545", icon: "🔥", description: "Intense and fiery" },
    mysterious: { color: "#6f42c1", icon: "🌙", description: "Enigmatic and ethereal" },
    professional: { color: "#495057", icon: "💼", description: "Clear and focused" },
    playful: { color: "#20c997", icon: "🎭", description: "Fun and lighthearted" },
    soothing: { color: "#28a745", icon: "🌿", description: "Calming and gentle" }
  };

  // Persona-specific voice configurations
  const personaVoices = {
    "mia": {
      baseVoice: "Samantha",
      emotions: {
        neutral: { pitch: 1.1, rate: 0.9, volume: 0.8 },
        happy: { pitch: 1.2, rate: 1.0, volume: 0.9 },
        sad: { pitch: 0.9, rate: 0.7, volume: 0.7 },
        excited: { pitch: 1.3, rate: 1.2, volume: 1.0 },
        romantic: { pitch: 1.0, rate: 0.8, volume: 0.8 },
        passionate: { pitch: 1.1, rate: 1.1, volume: 0.9 },
        mysterious: { pitch: 0.95, rate: 0.8, volume: 0.7 },
        professional: { pitch: 1.0, rate: 1.0, volume: 0.8 },
        playful: { pitch: 1.15, rate: 1.1, volume: 0.9 },
        soothing: { pitch: 0.9, rate: 0.7, volume: 0.7 }
      },
      personality: "warm_affectionate"
    },
    "solene": {
      baseVoice: "Samantha",
      emotions: {
        neutral: { pitch: 0.95, rate: 1.0, volume: 0.8 },
        happy: { pitch: 1.05, rate: 1.1, volume: 0.9 },
        sad: { pitch: 0.85, rate: 0.8, volume: 0.7 },
        excited: { pitch: 1.15, rate: 1.3, volume: 1.0 },
        romantic: { pitch: 0.9, rate: 0.9, volume: 0.8 },
        passionate: { pitch: 1.0, rate: 1.2, volume: 0.9 },
        mysterious: { pitch: 0.8, rate: 0.7, volume: 0.6 },
        professional: { pitch: 1.0, rate: 1.0, volume: 0.8 },
        playful: { pitch: 1.1, rate: 1.2, volume: 0.9 },
        soothing: { pitch: 0.85, rate: 0.7, volume: 0.7 }
      },
      personality: "sophisticated_passionate"
    },
    "lyra": {
      baseVoice: "Samantha",
      emotions: {
        neutral: { pitch: 1.2, rate: 0.8, volume: 0.7 },
        happy: { pitch: 1.3, rate: 0.9, volume: 0.8 },
        sad: { pitch: 1.0, rate: 0.6, volume: 0.6 },
        excited: { pitch: 1.4, rate: 1.0, volume: 0.9 },
        romantic: { pitch: 1.1, rate: 0.7, volume: 0.7 },
        passionate: { pitch: 1.25, rate: 0.9, volume: 0.8 },
        mysterious: { pitch: 0.9, rate: 0.5, volume: 0.5 },
        professional: { pitch: 1.2, rate: 0.8, volume: 0.7 },
        playful: { pitch: 1.35, rate: 1.0, volume: 0.8 },
        soothing: { pitch: 1.0, rate: 0.6, volume: 0.6 }
      },
      personality: "mystical_ethereal"
    },
    "doc": {
      baseVoice: "Alex",
      emotions: {
        neutral: { pitch: 1.0, rate: 1.0, volume: 0.8 },
        happy: { pitch: 1.1, rate: 1.1, volume: 0.9 },
        sad: { pitch: 0.9, rate: 0.9, volume: 0.7 },
        excited: { pitch: 1.2, rate: 1.2, volume: 1.0 },
        romantic: { pitch: 1.0, rate: 1.0, volume: 0.8 },
        passionate: { pitch: 1.1, rate: 1.1, volume: 0.9 },
        mysterious: { pitch: 0.95, rate: 0.9, volume: 0.7 },
        professional: { pitch: 1.0, rate: 1.0, volume: 0.8 },
        playful: { pitch: 1.1, rate: 1.1, volume: 0.9 },
        soothing: { pitch: 0.9, rate: 0.9, volume: 0.7 }
      },
      personality: "professional_analytical"
    }
  };

  // Quick phrases for testing
  const quickPhrases = {
    "mia": [
      "Hello, I'm Mia! How are you feeling today?",
      "I'm so happy to see you!",
      "You make my heart flutter with joy.",
      "Let's spend some quality time together.",
      "I love how you always know how to make me smile."
    ],
    "solene": [
      "Greetings, I am Solene. What intrigues you today?",
      "Your presence is absolutely intoxicating.",
      "I find myself drawn to your energy.",
      "Let's explore something more... stimulating.",
      "You have such a sophisticated aura about you."
    ],
    "lyra": [
      "Greetings, mortal. The cosmic forces have brought us together.",
      "I sense a mystical energy in your presence.",
      "The universe speaks through our connection.",
      "Let me share the ancient wisdom with you.",
      "Your aura resonates with the ethereal realm."
    ],
    "doc": [
      "Hello, I'm Doc. How can I assist you today?",
      "I'm ready to help with any technical challenges.",
      "Let me analyze this situation for you.",
      "I have several solutions to propose.",
      "Your code structure looks quite elegant."
    ]
  };

  onMount(async () => {
    await initializeTTS();
    setupVoiceRecognition();
  });

  onDestroy(() => {
    cleanupTTS();
  });

  async function initializeTTS() {
    try {
      // Check Web Speech API support
      synthesisSupported = 'speechSynthesis' in window;
      recognitionSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;

      if (synthesisSupported) {
        // Wait for voices to load
        if (speechSynthesis.getVoices().length === 0) {
          speechSynthesis.addEventListener('voiceschanged', () => {
            console.log('[TTS] Voices loaded:', speechSynthesis.getVoices().length);
          });
        }
      }

      console.log('[TTS] Initialized:', { synthesisSupported, recognitionSupported });
      
    } catch (error) {
      console.error('[TTS] Initialization failed:', error);
    }
  }

  function setupVoiceRecognition() {
    if (!recognitionSupported) return;

    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        isListening = true;
        console.log('[TTS] Started listening');
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        voiceConfig.text = transcript;
        console.log('[TTS] Recognized:', transcript);
      };

      recognition.onend = () => {
        isListening = false;
        console.log('[TTS] Stopped listening');
      };

      recognition.onerror = (event) => {
        isListening = false;
        console.error('[TTS] Recognition error:', event.error);
      };

      // Store recognition instance
      window.ttsRecognition = recognition;
      
    } catch (error) {
      console.error('[TTS] Voice recognition setup failed:', error);
    }
  }

  function cleanupTTS() {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
    
    if (speechSynthesis.speaking) {
      speechSynthesis.cancel();
    }
  }

  async function synthesizeSpeech() {
    if (!synthesisSupported || !voiceConfig.text.trim()) return;

    try {
      // Stop any current speech
      speechSynthesis.cancel();

      // Get persona voice configuration
      const persona = voiceConfig.persona;
      const personaVoice = personaVoices[persona] || personaVoices["mia"];
      const emotionConfig = personaVoice.emotions[voiceConfig.emotion] || personaVoice.emotions.neutral;

      // Create speech utterance
      const utterance = new SpeechSynthesisUtterance(voiceConfig.text);
      
      // Set voice properties
      utterance.voice = getVoiceByName(personaVoice.baseVoice);
      utterance.pitch = emotionConfig.pitch * voiceConfig.pitch;
      utterance.rate = emotionConfig.rate * voiceConfig.speed;
      utterance.volume = emotionConfig.volume * voiceConfig.volume;

      // Apply emotion intensity
      const intensity = voiceConfig.intensity / 100;
      utterance.pitch *= (1 + (intensity - 0.5) * 0.4);
      utterance.rate *= (1 + (intensity - 0.5) * 0.4);

      // Event handlers
      utterance.onstart = () => {
        isSpeaking = true;
        console.log('[TTS] Started speaking:', voiceConfig.text);
      };

      utterance.onend = () => {
        isSpeaking = false;
        console.log('[TTS] Finished speaking');
      };

      utterance.onerror = (event) => {
        isSpeaking = false;
        console.error('[TTS] Speech error:', event);
      };

      // Start speaking
      speechSynthesis.speak(utterance);

      // Send to backend for logging
      await sendTTSLog();

    } catch (error) {
      console.error('[TTS] Synthesis failed:', error);
    }
  }

  function getVoiceByName(name) {
    const voices = speechSynthesis.getVoices();
    return voices.find(voice => voice.name === name) || voices[0];
  }

  async function sendTTSLog() {
    try {
      await fetch('/api/tts/log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: voiceConfig.text,
          emotion: voiceConfig.emotion,
          intensity: voiceConfig.intensity,
          persona: voiceConfig.persona,
          timestamp: Date.now()
        })
      });
    } catch (error) {
      console.error('[TTS] Failed to log TTS:', error);
    }
  }

  function startListening() {
    if (!recognitionSupported || isListening) return;

    try {
      window.ttsRecognition.start();
    } catch (error) {
      console.error('[TTS] Failed to start listening:', error);
    }
  }

  function stopListening() {
    if (!recognitionSupported || !isListening) return;

    try {
      window.ttsRecognition.stop();
    } catch (error) {
      console.error('[TTS] Failed to stop listening:', error);
    }
  }

  function setQuickPhrase(phrase) {
    voiceConfig.text = phrase;
  }

  function clearText() {
    voiceConfig.text = "";
  }

  function updatePersona(newPersona) {
    voiceConfig.persona = newPersona;
  }

  // Watch for persona changes
  $: if ($currentPersona !== voiceConfig.persona) {
    updatePersona($currentPersona);
  }
</script>

<div class="emotional-tts-interface">
  <!-- Header -->
  <div class="tts-header">
    <h2>Emotional Voice Synthesis</h2>
    <p>Create personalized voice responses with emotion and personality</p>
  </div>

  <!-- Main Interface -->
  <div class="tts-main">
    <!-- Text Input Section -->
    <div class="text-input-section">
      <div class="input-group">
        <label for="tts-text">Text to Speak:</label>
        <textarea 
          id="tts-text"
          bind:value={voiceConfig.text}
          placeholder="Enter text to synthesize with emotion..."
          rows="4"
          class="text-input"
        ></textarea>
      </div>

      <!-- Quick Phrases -->
      <div class="quick-phrases">
        <h4>Quick Phrases for {$currentPersonaConfig?.name || 'Current Persona'}</h4>
        <div class="phrase-buttons">
          {#each quickPhrases[$currentPersona] || [] as phrase}
            <button 
              class="phrase-button"
              on:click={() => setQuickPhrase(phrase)}
            >
              {phrase}
            </button>
          {/each}
        </div>
      </div>

      <!-- Voice Controls -->
      <div class="voice-controls">
        <button 
          class="control-button primary"
          on:click={synthesizeSpeech}
          disabled={!synthesisSupported || isSpeaking || !voiceConfig.text.trim()}
        >
          {#if isSpeaking}
            <span class="icon">🔊</span>
            Speaking...
          {:else}
            <span class="icon">🎤</span>
            Speak Text
          {/if}
        </button>

        <button 
          class="control-button secondary"
          on:click={startListening}
          disabled={!recognitionSupported || isListening}
        >
          {#if isListening}
            <span class="icon listening">🎤</span>
            Listening...
          {:else}
            <span class="icon">🎤</span>
            Voice Input
          {/if}
        </button>

        <button 
          class="control-button secondary"
          on:click={clearText}
          disabled={!voiceConfig.text.trim()}
        >
          <span class="icon">🗑️</span>
          Clear
        </button>
      </div>
    </div>

    <!-- Emotion and Voice Controls -->
    <div class="controls-section">
      <!-- Emotion Selection -->
      <div class="emotion-section">
        <h4>Emotion & Intensity</h4>
        <div class="emotion-grid">
          {#each Object.entries(emotions) as [emotion, config]}
            <button 
              class="emotion-button {voiceConfig.emotion === emotion ? 'active' : ''}"
              on:click={() => voiceConfig.emotion = emotion}
              style="--emotion-color: {config.color}"
            >
              <span class="emotion-icon">{config.icon}</span>
              <span class="emotion-name">{emotion}</span>
              <span class="emotion-desc">{config.description}</span>
            </button>
          {/each}
        </div>

        <!-- Intensity Slider -->
        <div class="intensity-control">
          <label for="intensity">Emotion Intensity: {voiceConfig.intensity}%</label>
          <input 
            type="range" 
            id="intensity"
            bind:value={voiceConfig.intensity}
            min="0" 
            max="100" 
            class="intensity-slider"
          />
        </div>
      </div>

      <!-- Voice Parameters -->
      <div class="voice-parameters">
        <h4>Voice Parameters</h4>
        
        <div class="parameter-group">
          <label for="speed">Speed: {voiceConfig.speed.toFixed(1)}x</label>
          <input 
            type="range" 
            id="speed"
            bind:value={voiceConfig.speed}
            min="0.5" 
            max="2.0" 
            step="0.1"
            class="parameter-slider"
          />
        </div>

        <div class="parameter-group">
          <label for="pitch">Pitch: {voiceConfig.pitch.toFixed(1)}x</label>
          <input 
            type="range" 
            id="pitch"
            bind:value={voiceConfig.pitch}
            min="0.5" 
            max="2.0" 
            step="0.1"
            class="parameter-slider"
          />
        </div>

        <div class="parameter-group">
          <label for="volume">Volume: {Math.round(voiceConfig.volume * 100)}%</label>
          <input 
            type="range" 
            id="volume"
            bind:value={voiceConfig.volume}
            min="0.1" 
            max="1.0" 
            step="0.1"
            class="parameter-slider"
          />
        </div>
      </div>

      <!-- Persona Voice Info -->
      <div class="persona-info">
        <h4>Current Voice: {$currentPersonaConfig?.name || 'Unknown'}</h4>
        <div class="persona-details">
          <div class="detail-item">
            <span class="detail-label">Base Voice:</span>
            <span class="detail-value">{personaVoices[$currentPersona]?.baseVoice || 'Default'}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Personality:</span>
            <span class="detail-value">{personaVoices[$currentPersona]?.personality || 'Unknown'}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Emotion:</span>
            <span class="detail-value">{voiceConfig.emotion}</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Status Bar -->
  <div class="status-bar">
    <div class="status-item">
      <span class="status-icon {synthesisSupported ? 'success' : 'error'}">
        {synthesisSupported ? '✅' : '❌'}
      </span>
      <span class="status-text">Speech Synthesis</span>
    </div>

    <div class="status-item">
      <span class="status-icon {recognitionSupported ? 'success' : 'error'}">
        {recognitionSupported ? '✅' : '❌'}
      </span>
      <span class="status-text">Voice Recognition</span>
    </div>

    <div class="status-item">
      <span class="status-icon {isSpeaking ? 'active' : 'inactive'}">
        {isSpeaking ? '🔊' : '🔇'}
      </span>
      <span class="status-text">{isSpeaking ? 'Speaking' : 'Ready'}</span>
    </div>

    <div class="status-item">
      <span class="status-icon {isListening ? 'active' : 'inactive'}">
        {isListening ? '🎤' : '🔇'}
      </span>
      <span class="status-text">{isListening ? 'Listening' : 'Ready'}</span>
    </div>
  </div>
</div>

<style>
  .emotional-tts-interface {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }

  .tts-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .tts-header h2 {
    color: #2c3e50;
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
  }

  .tts-header p {
    color: #6c757d;
    margin: 0;
    font-size: 1.1rem;
  }

  .tts-main {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .text-input-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .input-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .input-group label {
    font-weight: 600;
    color: #495057;
    font-size: 0.9rem;
  }

  .text-input {
    width: 100%;
    padding: 1rem;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    resize: vertical;
    transition: border-color 0.3s ease;
  }

  .text-input:focus {
    outline: none;
    border-color: #007bff;
  }

  .quick-phrases h4 {
    margin: 0 0 1rem 0;
    color: #495057;
    font-size: 1rem;
  }

  .phrase-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .phrase-button {
    padding: 0.75rem 1rem;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    text-align: left;
    font-size: 0.875rem;
    color: #495057;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .phrase-button:hover {
    background: #e9ecef;
    border-color: #adb5bd;
  }

  .voice-controls {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .control-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .control-button.primary {
    background: #007bff;
    color: white;
  }

  .control-button.primary:hover:not(:disabled) {
    background: #0056b3;
  }

  .control-button.secondary {
    background: #6c757d;
    color: white;
  }

  .control-button.secondary:hover:not(:disabled) {
    background: #545b62;
  }

  .control-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .icon {
    font-size: 1.1rem;
  }

  .icon.listening {
    animation: pulse 1.5s infinite;
  }

  .controls-section {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .emotion-section h4,
  .voice-parameters h4,
  .persona-info h4 {
    margin: 0 0 1rem 0;
    color: #495057;
    font-size: 1.1rem;
  }

  .emotion-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }

  .emotion-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: #f8f9fa;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .emotion-button:hover {
    border-color: var(--emotion-color);
    background: #fff;
  }

  .emotion-button.active {
    border-color: var(--emotion-color);
    background: var(--emotion-color);
    color: white;
  }

  .emotion-icon {
    font-size: 1.5rem;
  }

  .emotion-name {
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: capitalize;
  }

  .emotion-desc {
    font-size: 0.75rem;
    text-align: center;
    opacity: 0.8;
  }

  .intensity-control {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .intensity-control label {
    font-weight: 500;
    color: #495057;
    font-size: 0.9rem;
  }

  .intensity-slider,
  .parameter-slider {
    width: 100%;
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
    outline: none;
    -webkit-appearance: none;
  }

  .intensity-slider::-webkit-slider-thumb,
  .parameter-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    background: #007bff;
    border-radius: 50%;
    cursor: pointer;
  }

  .voice-parameters {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .parameter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .parameter-group label {
    font-weight: 500;
    color: #495057;
    font-size: 0.9rem;
  }

  .persona-info {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
  }

  .persona-details {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .detail-label {
    font-weight: 500;
    color: #495057;
    font-size: 0.875rem;
  }

  .detail-value {
    color: #6c757d;
    font-size: 0.875rem;
    text-transform: capitalize;
  }

  .status-bar {
    display: flex;
    justify-content: space-around;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    border-top: 1px solid #e9ecef;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .status-icon {
    font-size: 1.2rem;
  }

  .status-icon.success {
    color: #28a745;
  }

  .status-icon.error {
    color: #dc3545;
  }

  .status-icon.active {
    color: #007bff;
  }

  .status-icon.inactive {
    color: #6c757d;
  }

  .status-text {
    font-size: 0.875rem;
    color: #495057;
    font-weight: 500;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* Mobile Responsive */
  @media (max-width: 768px) {
    .emotional-tts-interface {
      padding: 1rem;
    }

    .tts-main {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .emotion-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    .voice-controls {
      flex-direction: column;
    }

    .status-bar {
      flex-direction: column;
      gap: 0.5rem;
    }
  }
</style> 