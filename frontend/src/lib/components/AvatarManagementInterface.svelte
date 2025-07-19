<!-- AvatarManagementInterface.svelte -->
<!-- Real-time Avatar Management with Mood-Driven Animations -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';
  import { realtimeAvatar, realtimeActions } from '$lib/stores/realtimeStore.js';
  import realtimeService from '$lib/services/realtimeService.js';

  const dispatch = createEventDispatcher();

  // Avatar State
  let avatarState = {
    isVisible: true,
    currentMood: "neutral",
    currentGesture: "idle",
    currentExpression: "neutral",
    isAnimating: false,
    animationProgress: 0,
    lastUpdate: Date.now()
  };

  // Avatar Configuration
  let avatarConfig = {
    persona: $currentPersona,
    appearance: {
      face: "default",
      body: "default", 
      hair: "default",
      eyes: "default",
      clothing: "default",
      background: "default"
    },
    animation: {
      method: "realtime", // realtime, prerendered, motion_capture
      speed: 1.0,
      loop: true,
      autoPlay: true
    },
    mood: {
      sensitivity: 50,
      transitionSpeed: 0.5,
      autoAdjust: true
    }
  };

  // Available moods and their visual characteristics
  const moods = {
    neutral: { 
      color: "#6c757d", 
      icon: "😐", 
      description: "Calm and balanced",
      expressions: ["neutral", "calm", "thoughtful"],
      gestures: ["idle", "gentle_breathing", "subtle_movement"]
    },
    happy: { 
      color: "#ffc107", 
      icon: "😊", 
      description: "Joyful and cheerful",
      expressions: ["smile", "grin", "laugh"],
      gestures: ["wave", "clap", "jump", "dance"]
    },
    sad: { 
      color: "#17a2b8", 
      icon: "😢", 
      description: "Melancholic and tender",
      expressions: ["sad", "tearful", "longing"],
      gestures: ["head_down", "hug_self", "gentle_sigh"]
    },
    excited: { 
      color: "#fd7e14", 
      icon: "🤩", 
      description: "Energetic and enthusiastic",
      expressions: ["excited", "surprised", "amazed"],
      gestures: ["jump", "wave_arms", "spin", "bounce"]
    },
    romantic: { 
      color: "#e83e8c", 
      icon: "💕", 
      description: "Loving and intimate",
      expressions: ["loving", "tender", "passionate"],
      gestures: ["blow_kiss", "heart_hands", "gentle_touch"]
    },
    passionate: { 
      color: "#dc3545", 
      icon: "🔥", 
      description: "Intense and fiery",
      expressions: ["intense", "determined", "fierce"],
      gestures: ["fist_pump", "power_pose", "dramatic_gesture"]
    },
    mysterious: { 
      color: "#6f42c1", 
      icon: "🌙", 
      description: "Enigmatic and ethereal",
      expressions: ["mysterious", "enigmatic", "ethereal"],
      gestures: ["floating", "mystical_gesture", "sparkle_effect"]
    },
    professional: { 
      color: "#495057", 
      icon: "💼", 
      description: "Clear and focused",
      expressions: ["focused", "serious", "confident"],
      gestures: ["nod", "point", "handshake"]
    },
    playful: { 
      color: "#20c997", 
      icon: "🎭", 
      description: "Fun and lighthearted",
      expressions: ["wink", "grin", "playful"],
      gestures: ["dance", "spin", "playful_wave"]
    },
    soothing: { 
      color: "#28a745", 
      icon: "🌿", 
      description: "Calming and gentle",
      expressions: ["peaceful", "serene", "gentle"],
      gestures: ["gentle_breathing", "calm_movement", "healing_pose"]
    }
  };

  // Available gestures
  const gestures = [
    "idle", "wave", "clap", "jump", "dance", "blow_kiss", "heart_hands",
    "gentle_touch", "fist_pump", "power_pose", "dramatic_gesture",
    "floating", "mystical_gesture", "sparkle_effect", "nod", "point",
    "handshake", "spin", "playful_wave", "gentle_breathing", "calm_movement",
    "healing_pose", "head_down", "hug_self", "gentle_sigh", "wave_arms",
    "bounce", "gentle_movement", "subtle_movement"
  ];

  // Available expressions
  const expressions = [
    "neutral", "smile", "grin", "laugh", "sad", "tearful", "longing",
    "excited", "surprised", "amazed", "loving", "tender", "passionate",
    "intense", "determined", "fierce", "mysterious", "enigmatic", "ethereal",
    "focused", "serious", "confident", "wink", "playful", "peaceful",
    "serene", "gentle", "calm", "thoughtful"
  ];

  // Persona-specific avatar configurations
  const personaAvatars = {
    "mia": {
      baseAppearance: {
        face: "warm_friendly",
        body: "elegant_feminine",
        hair: "soft_waves",
        eyes: "bright_warm",
        clothing: "romantic_dress",
        background: "romantic_garden"
      },
      moodModifiers: {
        happy: { brightness: 1.2, saturation: 1.1 },
        romantic: { brightness: 1.1, saturation: 1.2 },
        sad: { brightness: 0.9, saturation: 0.8 }
      },
      personality: "warm_affectionate"
    },
    "solene": {
      baseAppearance: {
        face: "sophisticated_elegant",
        body: "graceful_feminine", 
        hair: "elegant_updo",
        eyes: "mysterious_deep",
        clothing: "sophisticated_outfit",
        background: "luxury_interior"
      },
      moodModifiers: {
        passionate: { brightness: 1.3, saturation: 1.3 },
        mysterious: { brightness: 0.8, saturation: 1.4 },
        excited: { brightness: 1.2, saturation: 1.2 }
      },
      personality: "sophisticated_passionate"
    },
    "lyra": {
      baseAppearance: {
        face: "ethereal_mystical",
        body: "otherworldly",
        hair: "flowing_ethereal",
        eyes: "cosmic_glow",
        clothing: "mystical_robes",
        background: "cosmic_realm"
      },
      moodModifiers: {
        mysterious: { brightness: 0.7, saturation: 1.5 },
        ethereal: { brightness: 1.1, saturation: 1.3 },
        soothing: { brightness: 0.9, saturation: 0.9 }
      },
      personality: "mystical_ethereal"
    },
    "doc": {
      baseAppearance: {
        face: "professional_analytical",
        body: "business_casual",
        hair: "neat_professional",
        eyes: "focused_analytical",
        clothing: "business_attire",
        background: "modern_office"
      },
      moodModifiers: {
        professional: { brightness: 1.0, saturation: 1.0 },
        focused: { brightness: 1.1, saturation: 0.9 },
        confident: { brightness: 1.2, saturation: 1.1 }
      },
      personality: "professional_analytical"
    }
  };

  // Animation state
  let animationInterval = null;
  let currentAnimation = null;

  onMount(async () => {
    await initializeAvatar();
    setupAnimationLoop();
  });

  onDestroy(() => {
    cleanupAnimation();
  });

  async function initializeAvatar() {
    try {
      // Load persona-specific avatar configuration
      const persona = $currentPersona;
      const personaConfig = personaAvatars[persona];
      
      if (personaConfig) {
        avatarConfig.appearance = { ...personaConfig.baseAppearance };
        avatarConfig.persona = persona;
      }

      // Set initial mood based on persona
      avatarState.currentMood = getInitialMood(persona);
      avatarState.currentExpression = moods[avatarState.currentMood].expressions[0];
      avatarState.currentGesture = moods[avatarState.currentMood].gestures[0];

      console.log('[Avatar] Initialized for persona:', persona);
      
    } catch (error) {
      console.error('[Avatar] Initialization failed:', error);
    }
  }

  function getInitialMood(persona) {
    const initialMoods = {
      "mia": "happy",
      "solene": "mysterious", 
      "lyra": "ethereal",
      "doc": "professional"
    };
    return initialMoods[persona] || "neutral";
  }

  function setupAnimationLoop() {
    if (avatarConfig.animation.autoPlay) {
      animationInterval = setInterval(() => {
        updateAvatarAnimation();
      }, 100); // 10 FPS animation loop
    }
  }

  function cleanupAnimation() {
    if (animationInterval) {
      clearInterval(animationInterval);
      animationInterval = null;
    }
  }

  function updateAvatarAnimation() {
    if (!avatarState.isVisible || avatarState.isAnimating) return;

    // Update animation progress
    avatarState.animationProgress += avatarConfig.animation.speed * 0.1;
    if (avatarState.animationProgress >= 1) {
      avatarState.animationProgress = 0;
    }

    // Trigger mood-based animations
    if (avatarConfig.mood.autoAdjust) {
      triggerMoodBasedAnimation();
    }

    avatarState.lastUpdate = Date.now();
  }

  function triggerMoodBasedAnimation() {
    const currentMood = moods[avatarState.currentMood];
    const availableGestures = currentMood.gestures;
    const availableExpressions = currentMood.expressions;

    // Randomly change gesture and expression based on mood
    if (Math.random() < 0.01) { // 1% chance per frame
      const newGesture = availableGestures[Math.floor(Math.random() * availableGestures.length)];
      const newExpression = availableExpressions[Math.floor(Math.random() * availableExpressions.length)];
      
      setGesture(newGesture);
      setExpression(newExpression);
    }
  }

  async function setMood(newMood) {
    if (!moods[newMood]) return;

    avatarState.currentMood = newMood;
    const moodConfig = moods[newMood];
    
    // Set default expression and gesture for this mood
    avatarState.currentExpression = moodConfig.expressions[0];
    avatarState.currentGesture = moodConfig.gestures[0];

    // Trigger mood change animation
    triggerMoodChangeAnimation(newMood);

    // Send real-time update
    try {
      await realtimeService.updateAvatarMood(newMood);
      await realtimeService.updateAvatarExpression(avatarState.currentExpression);
      await realtimeService.triggerAvatarGesture(avatarState.currentGesture);
    } catch (error) {
      console.error('[Avatar] Real-time update failed:', error);
    }

    console.log('[Avatar] Mood changed to:', newMood);
  }

  async function setGesture(newGesture) {
    if (!gestures.includes(newGesture)) return;

    avatarState.currentGesture = newGesture;
    avatarState.isAnimating = true;

    // Send real-time update
    try {
      await realtimeService.triggerAvatarGesture(newGesture);
    } catch (error) {
      console.error('[Avatar] Real-time gesture update failed:', error);
    }

    // Simulate gesture animation duration
    setTimeout(() => {
      avatarState.isAnimating = false;
    }, 2000);

    console.log('[Avatar] Gesture changed to:', newGesture);
  }

  async function setExpression(newExpression) {
    if (!expressions.includes(newExpression)) return;

    avatarState.currentExpression = newExpression;
    
    // Send real-time update
    try {
      await realtimeService.updateAvatarExpression(newExpression);
    } catch (error) {
      console.error('[Avatar] Real-time expression update failed:', error);
    }
    
    console.log('[Avatar] Expression changed to:', newExpression);
  }

  function triggerMoodChangeAnimation(newMood) {
    avatarState.isAnimating = true;
    
    // Simulate mood transition animation
    setTimeout(() => {
      avatarState.isAnimating = false;
    }, 1500);
  }

  function toggleAvatarVisibility() {
    avatarState.isVisible = !avatarState.isVisible;
    console.log('[Avatar] Visibility toggled:', avatarState.isVisible);
  }

  function changeAnimationMethod(method) {
    avatarConfig.animation.method = method;
    console.log('[Avatar] Animation method changed to:', method);
  }

  function updateAppearance(aspect, value) {
    avatarConfig.appearance[aspect] = value;
    console.log('[Avatar] Appearance updated:', aspect, value);
  }

  // Watch for persona changes
  $: if ($currentPersona !== avatarConfig.persona) {
    avatarConfig.persona = $currentPersona;
    initializeAvatar();
  }

  // Export functions for external use
  export { 
    avatarState, 
    avatarConfig, 
    setMood, 
    setGesture, 
    setExpression,
    toggleAvatarVisibility 
  };
</script>

<div class="avatar-management-interface">
  <!-- Header -->
  <div class="avatar-header">
    <h2>Avatar Management</h2>
    <p>Real-time avatar with mood-driven animations and persona customization</p>
  </div>

  <!-- Main Interface -->
  <div class="avatar-main">
    <!-- Avatar Display -->
    <div class="avatar-display-section">
      <div class="avatar-container">
        <div class="avatar-visibility-toggle">
          <button 
            class="visibility-button {avatarState.isVisible ? 'visible' : 'hidden'}"
            on:click={toggleAvatarVisibility}
          >
            {avatarState.isVisible ? '👁️' : '🙈'}
            {avatarState.isVisible ? 'Hide Avatar' : 'Show Avatar'}
          </button>
        </div>

        <!-- Avatar Canvas -->
        <div class="avatar-canvas {avatarState.isVisible ? 'visible' : 'hidden'}">
          <div class="avatar-placeholder">
            <div class="avatar-character">
              <div class="avatar-face">
                <span class="avatar-expression">{moods[avatarState.currentMood].icon}</span>
              </div>
              <div class="avatar-body">
                <span class="avatar-gesture">💃</span>
              </div>
            </div>
            
            <!-- Mood Indicator -->
            <div class="mood-indicator" style="--mood-color: {moods[avatarState.currentMood].color}">
              <span class="mood-icon">{moods[avatarState.currentMood].icon}</span>
              <span class="mood-name">{avatarState.currentMood}</span>
            </div>

            <!-- Animation Status -->
            <div class="animation-status {avatarState.isAnimating ? 'animating' : 'idle'}">
              <span class="status-icon">{avatarState.isAnimating ? '🎬' : '⏸️'}</span>
              <span class="status-text">{avatarState.isAnimating ? 'Animating' : 'Idle'}</span>
            </div>
          </div>
        </div>

        <!-- Avatar Info -->
        <div class="avatar-info">
          <div class="info-item">
            <span class="info-label">Persona:</span>
            <span class="info-value">{$currentPersonaConfig?.name || 'Unknown'}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Expression:</span>
            <span class="info-value">{avatarState.currentExpression}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Gesture:</span>
            <span class="info-value">{avatarState.currentGesture}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Animation:</span>
            <span class="info-value">{avatarConfig.animation.method}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Controls Section -->
    <div class="controls-section">
      <!-- Mood Controls -->
      <div class="mood-controls">
        <h4>Mood & Expression</h4>
        <div class="mood-grid">
          {#each Object.entries(moods) as [mood, config]}
            <button 
              class="mood-button {avatarState.currentMood === mood ? 'active' : ''}"
              on:click={() => setMood(mood)}
              style="--mood-color: {config.color}"
            >
              <span class="mood-icon">{config.icon}</span>
              <span class="mood-name">{mood}</span>
              <span class="mood-desc">{config.description}</span>
            </button>
          {/each}
        </div>
      </div>

      <!-- Gesture Controls -->
      <div class="gesture-controls">
        <h4>Gestures & Movements</h4>
        <div class="gesture-grid">
          {#each gestures.slice(0, 12) as gesture}
            <button 
              class="gesture-button {avatarState.currentGesture === gesture ? 'active' : ''}"
              on:click={() => setGesture(gesture)}
            >
              <span class="gesture-icon">💃</span>
              <span class="gesture-name">{gesture.replace(/_/g, ' ')}</span>
            </button>
          {/each}
        </div>
        
        <div class="gesture-grid">
          {#each gestures.slice(12) as gesture}
            <button 
              class="gesture-button {avatarState.currentGesture === gesture ? 'active' : ''}"
              on:click={() => setGesture(gesture)}
            >
              <span class="gesture-icon">💃</span>
              <span class="gesture-name">{gesture.replace(/_/g, ' ')}</span>
            </button>
          {/each}
        </div>
      </div>

      <!-- Expression Controls -->
      <div class="expression-controls">
        <h4>Facial Expressions</h4>
        <div class="expression-grid">
          {#each expressions.slice(0, 15) as expression}
            <button 
              class="expression-button {avatarState.currentExpression === expression ? 'active' : ''}"
              on:click={() => setExpression(expression)}
            >
              <span class="expression-icon">😊</span>
              <span class="expression-name">{expression}</span>
            </button>
          {/each}
        </div>
        
        <div class="expression-grid">
          {#each expressions.slice(15) as expression}
            <button 
              class="expression-button {avatarState.currentExpression === expression ? 'active' : ''}"
              on:click={() => setExpression(expression)}
            >
              <span class="expression-icon">😊</span>
              <span class="expression-name">{expression}</span>
            </button>
          {/each}
        </div>
      </div>

      <!-- Animation Settings -->
      <div class="animation-settings">
        <h4>Animation Settings</h4>
        
        <div class="setting-group">
          <label for="animation-method">Animation Method:</label>
          <select 
            id="animation-method"
            bind:value={avatarConfig.animation.method}
            on:change={() => changeAnimationMethod(avatarConfig.animation.method)}
          >
            <option value="realtime">Real-time Generation</option>
            <option value="prerendered">Pre-rendered</option>
            <option value="motion_capture">Motion Capture</option>
          </select>
        </div>

        <div class="setting-group">
          <label for="animation-speed">Speed: {avatarConfig.animation.speed.toFixed(1)}x</label>
          <input 
            type="range" 
            id="animation-speed"
            bind:value={avatarConfig.animation.speed}
            min="0.1" 
            max="3.0" 
            step="0.1"
            class="setting-slider"
          />
        </div>

        <div class="setting-group">
          <label for="mood-sensitivity">Mood Sensitivity: {avatarConfig.mood.sensitivity}%</label>
          <input 
            type="range" 
            id="mood-sensitivity"
            bind:value={avatarConfig.mood.sensitivity}
            min="0" 
            max="100" 
            class="setting-slider"
          />
        </div>

        <div class="setting-group">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              bind:checked={avatarConfig.animation.autoPlay}
            />
            Auto-play animations
          </label>
        </div>

        <div class="setting-group">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              bind:checked={avatarConfig.mood.autoAdjust}
            />
            Auto-adjust to mood
          </label>
        </div>
      </div>

      <!-- Appearance Customization -->
      <div class="appearance-customization">
        <h4>Appearance Customization</h4>
        
        <div class="appearance-grid">
          <div class="appearance-item">
            <label for="face-select">Face:</label>
            <select 
              id="face-select"
              bind:value={avatarConfig.appearance.face}
              on:change={() => updateAppearance('face', avatarConfig.appearance.face)}
            >
              <option value="default">Default</option>
              <option value="warm_friendly">Warm & Friendly</option>
              <option value="sophisticated_elegant">Sophisticated</option>
              <option value="ethereal_mystical">Ethereal</option>
              <option value="professional_analytical">Professional</option>
            </select>
          </div>

          <div class="appearance-item">
            <label for="hair-select">Hair:</label>
            <select 
              id="hair-select"
              bind:value={avatarConfig.appearance.hair}
              on:change={() => updateAppearance('hair', avatarConfig.appearance.hair)}
            >
              <option value="default">Default</option>
              <option value="soft_waves">Soft Waves</option>
              <option value="elegant_updo">Elegant Updo</option>
              <option value="flowing_ethereal">Flowing Ethereal</option>
              <option value="neat_professional">Neat Professional</option>
            </select>
          </div>

          <div class="appearance-item">
            <label for="clothing-select">Clothing:</label>
            <select 
              id="clothing-select"
              bind:value={avatarConfig.appearance.clothing}
              on:change={() => updateAppearance('clothing', avatarConfig.appearance.clothing)}
            >
              <option value="default">Default</option>
              <option value="romantic_dress">Romantic Dress</option>
              <option value="sophisticated_outfit">Sophisticated</option>
              <option value="mystical_robes">Mystical Robes</option>
              <option value="business_attire">Business Attire</option>
            </select>
          </div>

          <div class="appearance-item">
            <label for="background-select">Background:</label>
            <select 
              id="background-select"
              bind:value={avatarConfig.appearance.background}
              on:change={() => updateAppearance('background', avatarConfig.appearance.background)}
            >
              <option value="default">Default</option>
              <option value="romantic_garden">Romantic Garden</option>
              <option value="luxury_interior">Luxury Interior</option>
              <option value="cosmic_realm">Cosmic Realm</option>
              <option value="modern_office">Modern Office</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Status Bar -->
  <div class="status-bar">
    <div class="status-item">
      <span class="status-icon {avatarState.isVisible ? 'success' : 'error'}">
        {avatarState.isVisible ? '👁️' : '🙈'}
      </span>
      <span class="status-text">{avatarState.isVisible ? 'Visible' : 'Hidden'}</span>
    </div>

    <div class="status-item">
      <span class="status-icon {avatarState.isAnimating ? 'active' : 'inactive'}">
        {avatarState.isAnimating ? '🎬' : '⏸️'}
      </span>
      <span class="status-text">{avatarState.isAnimating ? 'Animating' : 'Idle'}</span>
    </div>

    <div class="status-item">
      <span class="status-icon" style="color: {moods[avatarState.currentMood].color}">
        {moods[avatarState.currentMood].icon}
      </span>
      <span class="status-text">{avatarState.currentMood}</span>
    </div>

    <div class="status-item">
      <span class="status-icon">💃</span>
      <span class="status-text">{avatarState.currentGesture}</span>
    </div>

    <div class="status-item">
      <span class="status-icon">😊</span>
      <span class="status-text">{avatarState.currentExpression}</span>
    </div>
  </div>
</div>

<style>
  .avatar-management-interface {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }

  .avatar-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .avatar-header h2 {
    color: #2c3e50;
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
  }

  .avatar-header p {
    color: #6c757d;
    margin: 0;
    font-size: 1.1rem;
  }

  .avatar-main {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .avatar-display-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .avatar-container {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1.5rem;
    border: 2px solid #e9ecef;
  }

  .avatar-visibility-toggle {
    margin-bottom: 1rem;
  }

  .visibility-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .visibility-button.visible {
    background: #28a745;
    color: white;
  }

  .visibility-button.hidden {
    background: #dc3545;
    color: white;
  }

  .avatar-canvas {
    aspect-ratio: 1;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    transition: opacity 0.3s ease;
  }

  .avatar-canvas.hidden {
    opacity: 0.3;
  }

  .avatar-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    color: white;
  }

  .avatar-character {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .avatar-face {
    font-size: 4rem;
    animation: float 3s ease-in-out infinite;
  }

  .avatar-body {
    font-size: 2rem;
    animation: {avatarState.isAnimating ? 'dance 1s ease-in-out infinite' : 'none'};
  }

  .mood-indicator {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    backdrop-filter: blur(10px);
  }

  .mood-icon {
    font-size: 1.2rem;
  }

  .mood-name {
    font-weight: 500;
    text-transform: capitalize;
  }

  .animation-status {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    backdrop-filter: blur(10px);
  }

  .animation-status.animating {
    background: rgba(255, 193, 7, 0.3);
  }

  .status-icon {
    font-size: 1.2rem;
  }

  .status-text {
    font-weight: 500;
  }

  .avatar-info {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    background: white;
    border-radius: 6px;
  }

  .info-label {
    font-weight: 500;
    color: #495057;
    font-size: 0.875rem;
  }

  .info-value {
    color: #6c757d;
    font-size: 0.875rem;
    text-transform: capitalize;
  }

  .controls-section {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .mood-controls h4,
  .gesture-controls h4,
  .expression-controls h4,
  .animation-settings h4,
  .appearance-customization h4 {
    margin: 0 0 1rem 0;
    color: #495057;
    font-size: 1.1rem;
  }

  .mood-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.75rem;
  }

  .mood-button {
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

  .mood-button:hover {
    border-color: var(--mood-color);
    background: #fff;
  }

  .mood-button.active {
    border-color: var(--mood-color);
    background: var(--mood-color);
    color: white;
  }

  .mood-icon {
    font-size: 1.5rem;
  }

  .mood-name {
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: capitalize;
  }

  .mood-desc {
    font-size: 0.75rem;
    text-align: center;
    opacity: 0.8;
  }

  .gesture-grid,
  .expression-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .gesture-button,
  .expression-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 0.75rem;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.75rem;
  }

  .gesture-button:hover,
  .expression-button:hover {
    background: #e9ecef;
    border-color: #adb5bd;
  }

  .gesture-button.active,
  .expression-button.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
  }

  .gesture-icon,
  .expression-icon {
    font-size: 1.2rem;
  }

  .gesture-name,
  .expression-name {
    text-align: center;
    text-transform: capitalize;
  }

  .animation-settings {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
  }

  .setting-group {
    margin-bottom: 1rem;
  }

  .setting-group label {
    display: block;
    font-weight: 500;
    color: #495057;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }

  .setting-group select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .setting-slider {
    width: 100%;
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
    outline: none;
    -webkit-appearance: none;
  }

  .setting-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    background: #007bff;
    border-radius: 50%;
    cursor: pointer;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }

  .checkbox-label input[type="checkbox"] {
    width: auto;
  }

  .appearance-customization {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
  }

  .appearance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .appearance-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .appearance-item label {
    font-weight: 500;
    color: #495057;
    font-size: 0.875rem;
  }

  .appearance-item select {
    padding: 0.5rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 0.875rem;
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

  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }

  @keyframes dance {
    0%, 100% { transform: rotate(0deg); }
    25% { transform: rotate(5deg); }
    75% { transform: rotate(-5deg); }
  }

  /* Mobile Responsive */
  @media (max-width: 768px) {
    .avatar-management-interface {
      padding: 1rem;
    }

    .avatar-main {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .mood-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    .gesture-grid,
    .expression-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    .appearance-grid {
      grid-template-columns: 1fr;
    }

    .status-bar {
      flex-direction: column;
      gap: 0.5rem;
    }
  }
</style> 