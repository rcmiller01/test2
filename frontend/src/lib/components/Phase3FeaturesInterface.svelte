<!-- Phase3FeaturesInterface.svelte -->
<!-- Advanced Phase 3 Features: Haptic, Biometric, VR, and Relationship AI -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';

  const dispatch = createEventDispatcher();

  // Phase 3 State
  let phase3State = {
    hapticEnabled: false,
    biometricEnabled: false,
    vrEnabled: false,
    relationshipAIEnabled: false,
    isConnected: false,
    lastUpdate: Date.now()
  };

  // Haptic System
  let hapticState = {
    isActive: false,
    currentPattern: "gentle",
    intensity: 50,
    duration: 2000,
    patterns: []
  };

  // Biometric System
  let biometricState = {
    isMonitoring: false,
    heartRate: 72,
    heartRateHistory: [],
    romanticSync: 85,
    stressLevel: 25,
    energyLevel: 80,
    lastReading: Date.now()
  };

  // VR System
  let vrState = {
    isActive: false,
    currentScene: "romantic_garden",
    sceneProgress: 0,
    interactionMode: "passive",
    availableScenes: []
  };

  // Relationship AI
  let relationshipAIState = {
    isActive: false,
    healthScore: 85,
    recentInsights: [],
    recommendations: [],
    conflictAlerts: [],
    growthOpportunities: []
  };

  // Available haptic patterns
  const hapticPatterns = {
    gentle: { 
      name: "Gentle Touch", 
      icon: "🤲", 
      color: "#28a745",
      description: "Soft, gentle vibrations",
      intensity: 30,
      duration: 1500
    },
    heartbeat: { 
      name: "Heartbeat", 
      icon: "💓", 
      color: "#e83e8c",
      description: "Rhythmic heartbeat pattern",
      intensity: 60,
      duration: 3000
    },
    passionate: { 
      name: "Passionate", 
      icon: "🔥", 
      color: "#dc3545",
      description: "Intense, passionate vibrations",
      intensity: 90,
      duration: 2500
    },
    soothing: { 
      name: "Soothing", 
      icon: "🌿", 
      color: "#20c997",
      description: "Calming, healing vibrations",
      intensity: 40,
      duration: 4000
    },
    playful: { 
      name: "Playful", 
      icon: "🎭", 
      color: "#ffc107",
      description: "Fun, energetic vibrations",
      intensity: 70,
      duration: 2000
    },
    mysterious: { 
      name: "Mysterious", 
      icon: "🌙", 
      color: "#6f42c1",
      description: "Enigmatic, ethereal vibrations",
      intensity: 50,
      duration: 3500
    },
    professional: { 
      name: "Professional", 
      icon: "💼", 
      color: "#495057",
      description: "Subtle, focused vibrations",
      intensity: 35,
      duration: 1500
    },
    romantic: { 
      name: "Romantic", 
      icon: "💕", 
      color: "#e83e8c",
      description: "Loving, intimate vibrations",
      intensity: 65,
      duration: 3000
    },
    exciting: { 
      name: "Exciting", 
      icon: "🤩", 
      color: "#fd7e14",
      description: "Thrilling, exciting vibrations",
      intensity: 80,
      duration: 2500
    },
    healing: { 
      name: "Healing", 
      icon: "✨", 
      color: "#17a2b8",
      description: "Therapeutic, healing vibrations",
      intensity: 45,
      duration: 5000
    }
  };

  // Available VR scenes
  const vrScenes = {
    romantic_garden: {
      name: "Romantic Garden",
      icon: "🌹",
      color: "#e83e8c",
      description: "A beautiful garden filled with roses and candlelight",
      duration: 300000, // 5 minutes
      interactions: ["walk", "sit", "embrace", "kiss"]
    },
    cosmic_realm: {
      name: "Cosmic Realm",
      icon: "🌌",
      color: "#6f42c1",
      description: "An ethereal realm among the stars",
      duration: 240000, // 4 minutes
      interactions: ["float", "meditate", "connect", "dream"]
    },
    luxury_penthouse: {
      name: "Luxury Penthouse",
      icon: "🏢",
      color: "#fd7e14",
      description: "A sophisticated penthouse with city views",
      duration: 360000, // 6 minutes
      interactions: ["dance", "dine", "relax", "intimate"]
    },
    mystical_forest: {
      name: "Mystical Forest",
      icon: "🌲",
      color: "#28a745",
      description: "An enchanted forest with magical creatures",
      duration: 300000, // 5 minutes
      interactions: ["explore", "discover", "wonder", "connect"]
    },
    beach_sunset: {
      name: "Beach Sunset",
      icon: "🌅",
      color: "#ffc107",
      description: "A peaceful beach during golden hour",
      duration: 240000, // 4 minutes
      interactions: ["walk", "swim", "watch", "embrace"]
    },
    mountain_retreat: {
      name: "Mountain Retreat",
      icon: "🏔️",
      color: "#17a2b8",
      description: "A cozy cabin in the mountains",
      duration: 360000, // 6 minutes
      interactions: ["hike", "warm", "talk", "bond"]
    },
    urban_adventure: {
      name: "Urban Adventure",
      icon: "🏙️",
      color: "#495057",
      description: "An exciting city exploration",
      duration: 300000, // 5 minutes
      interactions: ["explore", "discover", "excite", "share"]
    },
    underwater_world: {
      name: "Underwater World",
      icon: "🐠",
      color: "#20c997",
      description: "A magical underwater realm",
      duration: 240000, // 4 minutes
      interactions: ["swim", "discover", "wonder", "connect"]
    },
    space_station: {
      name: "Space Station",
      icon: "🚀",
      color: "#6c757d",
      description: "A futuristic space station",
      duration: 360000, // 6 minutes
      interactions: ["explore", "learn", "bond", "dream"]
    },
    enchanted_castle: {
      name: "Enchanted Castle",
      icon: "🏰",
      color: "#e83e8c",
      description: "A magical castle with enchanted gardens",
      duration: 300000, // 5 minutes
      interactions: ["explore", "dance", "romance", "dream"]
    }
  };

  // Monitoring intervals
  let biometricInterval = null;
  let hapticInterval = null;
  let vrInterval = null;

  onMount(async () => {
    await initializePhase3();
    setupMonitoring();
  });

  onDestroy(() => {
    cleanupMonitoring();
  });

  async function initializePhase3() {
    try {
      // Check device capabilities
      phase3State.hapticEnabled = 'vibrate' in navigator;
      phase3State.biometricEnabled = 'getBattery' in navigator || 'bluetooth' in navigator;
      phase3State.vrEnabled = 'getVRDisplays' in navigator;
      phase3State.relationshipAIEnabled = true; // Always available

      // Initialize biometric history
      biometricState.heartRateHistory = generateHeartRateHistory();
      
      // Load VR scenes
      vrState.availableScenes = Object.keys(vrScenes);

      console.log('[Phase3] Initialized with capabilities:', {
        haptic: phase3State.hapticEnabled,
        biometric: phase3State.biometricEnabled,
        vr: phase3State.vrEnabled,
        ai: phase3State.relationshipAIEnabled
      });

    } catch (error) {
      console.error('[Phase3] Initialization failed:', error);
    }
  }

  function generateHeartRateHistory() {
    const history = [];
    const now = Date.now();
    for (let i = 0; i < 24; i++) {
      history.push({
        timestamp: now - (23 - i) * 3600000, // Last 24 hours
        value: 65 + Math.random() * 30 // 65-95 BPM
      });
    }
    return history;
  }

  function setupMonitoring() {
    // Biometric monitoring
    if (phase3State.biometricEnabled) {
      biometricInterval = setInterval(() => {
        updateBiometrics();
      }, 5000); // Update every 5 seconds
    }

    // Haptic pattern updates
    hapticInterval = setInterval(() => {
      updateHapticPatterns();
    }, 10000); // Update every 10 seconds

    // VR scene progress
    vrInterval = setInterval(() => {
      updateVRProgress();
    }, 1000); // Update every second
  }

  function cleanupMonitoring() {
    if (biometricInterval) clearInterval(biometricInterval);
    if (hapticInterval) clearInterval(hapticInterval);
    if (vrInterval) clearInterval(vrInterval);
  }

  function updateBiometrics() {
    // Simulate biometric readings
    biometricState.heartRate = 65 + Math.random() * 30;
    biometricState.stressLevel = Math.max(0, Math.min(100, biometricState.stressLevel + (Math.random() - 0.5) * 10));
    biometricState.energyLevel = Math.max(0, Math.min(100, biometricState.energyLevel + (Math.random() - 0.5) * 5));
    biometricState.romanticSync = Math.max(0, Math.min(100, biometricState.romanticSync + (Math.random() - 0.5) * 3));
    biometricState.lastReading = Date.now();

    // Update heart rate history
    biometricState.heartRateHistory.push({
      timestamp: Date.now(),
      value: biometricState.heartRate
    });

    // Keep only last 24 hours
    if (biometricState.heartRateHistory.length > 24) {
      biometricState.heartRateHistory.shift();
    }
  }

  function updateHapticPatterns() {
    // Update haptic patterns based on persona and mood
    const persona = $currentPersona;
    const patterns = Object.keys(hapticPatterns);
    
    // Persona-specific pattern preferences
    const personaPatterns = {
      "mia": ["gentle", "heartbeat", "romantic", "soothing"],
      "solene": ["passionate", "mysterious", "exciting", "romantic"],
      "lyra": ["mysterious", "healing", "soothing", "ethereal"],
      "doc": ["professional", "gentle", "focused", "calm"]
    };

    const preferredPatterns = personaPatterns[persona] || patterns;
    hapticState.patterns = preferredPatterns;
  }

  function updateVRProgress() {
    if (vrState.isActive) {
      vrState.sceneProgress += 1;
      const currentScene = vrScenes[vrState.currentScene];
      
      if (vrState.sceneProgress >= currentScene.duration) {
        // Scene completed
        vrState.sceneProgress = 0;
        completeVRScene();
      }
    }
  }

  function completeVRScene() {
    console.log('[VR] Scene completed:', vrState.currentScene);
    // Trigger scene completion effects
    triggerHapticFeedback("gentle");
    updateRelationshipAI("vr_experience_completed");
  }

  async function triggerHapticFeedback(pattern) {
    if (!phase3State.hapticEnabled || !hapticState.isActive) return;

    try {
      const patternConfig = hapticPatterns[pattern];
      if (!patternConfig) return;

      // Use Web Vibration API
      if ('vibrate' in navigator) {
        const intensity = (patternConfig.intensity / 100) * 200; // Convert to milliseconds
        navigator.vibrate(intensity);
      }

      // Send to backend for logging
      await fetch('/api/phase3/haptic/trigger', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pattern: pattern,
          intensity: patternConfig.intensity,
          duration: patternConfig.duration,
          persona: $currentPersona,
          timestamp: Date.now()
        })
      });

      console.log('[Haptic] Triggered pattern:', pattern);

    } catch (error) {
      console.error('[Haptic] Failed to trigger feedback:', error);
    }
  }

  async function startVRScene(sceneName) {
    if (!phase3State.vrEnabled) return;

    try {
      vrState.isActive = true;
      vrState.currentScene = sceneName;
      vrState.sceneProgress = 0;

      // Send to backend
      await fetch('/api/phase3/vr/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scene: sceneName,
          persona: $currentPersona,
          timestamp: Date.now()
        })
      });

      console.log('[VR] Started scene:', sceneName);

    } catch (error) {
      console.error('[VR] Failed to start scene:', error);
    }
  }

  function stopVRScene() {
    vrState.isActive = false;
    vrState.sceneProgress = 0;
    console.log('[VR] Stopped scene');
  }

  async function updateRelationshipAI(event) {
    if (!phase3State.relationshipAIEnabled) return;

    try {
      const response = await fetch('/api/phase3/relationship/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event: event,
          biometrics: biometricState,
          persona: $currentPersona,
          timestamp: Date.now()
        })
      });

      if (response.ok) {
        const data = await response.json();
        relationshipAIState.healthScore = data.healthScore || relationshipAIState.healthScore;
        relationshipAIState.recentInsights = data.insights || [];
        relationshipAIState.recommendations = data.recommendations || [];
        relationshipAIState.conflictAlerts = data.conflicts || [];
        relationshipAIState.growthOpportunities = data.growth || [];
      }

    } catch (error) {
      console.error('[RelationshipAI] Failed to update:', error);
    }
  }

  function toggleHaptic() {
    hapticState.isActive = !hapticState.isActive;
    console.log('[Haptic] Toggled:', hapticState.isActive);
  }

  function toggleBiometric() {
    biometricState.isMonitoring = !biometricState.isMonitoring;
    console.log('[Biometric] Toggled:', biometricState.isMonitoring);
  }

  function toggleVR() {
    if (vrState.isActive) {
      stopVRScene();
    } else {
      startVRScene(vrState.currentScene);
    }
  }

  function toggleRelationshipAI() {
    relationshipAIState.isActive = !relationshipAIState.isActive;
    console.log('[RelationshipAI] Toggled:', relationshipAIState.isActive);
  }

  function formatDuration(ms) {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

  function getHealthColor(score) {
    if (score >= 80) return "#28a745";
    if (score >= 60) return "#ffc107";
    return "#dc3545";
  }

  // Watch for persona changes
  $: if ($currentPersona) {
    updateHapticPatterns();
  }
</script>

<div class="phase3-features-interface">
  <!-- Header -->
  <div class="phase3-header">
    <h2>Phase 3 Advanced Features</h2>
    <p>Haptic feedback, biometric monitoring, VR experiences, and relationship AI</p>
  </div>

  <!-- Main Interface -->
  <div class="phase3-main">
    <!-- Haptic Feedback Section -->
    <div class="feature-section haptic-section">
      <div class="section-header">
        <h3>Haptic Feedback System</h3>
        <div class="status-indicator {phase3State.hapticEnabled ? 'enabled' : 'disabled'}">
          {phase3State.hapticEnabled ? '✅' : '❌'}
          {phase3State.hapticEnabled ? 'Available' : 'Unavailable'}
        </div>
      </div>

      <div class="haptic-controls">
        <div class="control-group">
          <label class="toggle-label">
            <input 
              type="checkbox" 
              bind:checked={hapticState.isActive}
              disabled={!phase3State.hapticEnabled}
            />
            Enable Haptic Feedback
          </label>
        </div>

        <div class="pattern-grid">
          {#each Object.entries(hapticPatterns) as [pattern, config]}
            <button 
              class="pattern-button {hapticState.currentPattern === pattern ? 'active' : ''}"
              on:click={() => {
                hapticState.currentPattern = pattern;
                triggerHapticFeedback(pattern);
              }}
              disabled={!hapticState.isActive}
              style="--pattern-color: {config.color}"
            >
              <span class="pattern-icon">{config.icon}</span>
              <span class="pattern-name">{config.name}</span>
              <span class="pattern-desc">{config.description}</span>
            </button>
          {/each}
        </div>

        <div class="intensity-control">
          <label for="haptic-intensity">Intensity: {hapticState.intensity}%</label>
          <input 
            type="range" 
            id="haptic-intensity"
            bind:value={hapticState.intensity}
            min="10" 
            max="100" 
            class="intensity-slider"
          />
        </div>
      </div>
    </div>

    <!-- Biometric Monitoring Section -->
    <div class="feature-section biometric-section">
      <div class="section-header">
        <h3>Biometric Monitoring</h3>
        <div class="status-indicator {phase3State.biometricEnabled ? 'enabled' : 'disabled'}">
          {phase3State.biometricEnabled ? '✅' : '❌'}
          {phase3State.biometricEnabled ? 'Available' : 'Unavailable'}
        </div>
      </div>

      <div class="biometric-dashboard">
        <div class="metric-grid">
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-icon">💓</span>
              <span class="metric-name">Heart Rate</span>
            </div>
            <div class="metric-value">{biometricState.heartRate} BPM</div>
            <div class="metric-trend">
              {biometricState.heartRate > 80 ? '↗️' : biometricState.heartRate < 60 ? '↘️' : '→'}
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-icon">💕</span>
              <span class="metric-name">Romantic Sync</span>
            </div>
            <div class="metric-value">{biometricState.romanticSync}%</div>
            <div class="metric-trend">
              {biometricState.romanticSync > 90 ? '💕' : biometricState.romanticSync > 70 ? '💖' : '💔'}
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-icon">😰</span>
              <span class="metric-name">Stress Level</span>
            </div>
            <div class="metric-value">{biometricState.stressLevel}%</div>
            <div class="metric-trend">
              {biometricState.stressLevel < 30 ? '😌' : biometricState.stressLevel < 60 ? '😐' : '😰'}
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-icon">⚡</span>
              <span class="metric-name">Energy Level</span>
            </div>
            <div class="metric-value">{biometricState.energyLevel}%</div>
            <div class="metric-trend">
              {biometricState.energyLevel > 80 ? '⚡' : biometricState.energyLevel > 50 ? '🔋' : '😴'}
            </div>
          </div>
        </div>

        <div class="heart-rate-chart">
          <h4>Heart Rate History (24h)</h4>
          <div class="chart-container">
            {#each biometricState.heartRateHistory as reading, i}
              <div 
                class="chart-bar"
                style="height: {(reading.value - 60) / 40 * 100}%; background: {reading.value > 80 ? '#dc3545' : reading.value > 70 ? '#ffc107' : '#28a745'}"
                title="{reading.value} BPM at {new Date(reading.timestamp).toLocaleTimeString()}"
              ></div>
            {/each}
          </div>
        </div>
      </div>
    </div>

    <!-- VR Experiences Section -->
    <div class="feature-section vr-section">
      <div class="section-header">
        <h3>Virtual Reality Experiences</h3>
        <div class="status-indicator {phase3State.vrEnabled ? 'enabled' : 'disabled'}">
          {phase3State.vrEnabled ? '✅' : '❌'}
          {phase3State.vrEnabled ? 'Available' : 'Unavailable'}
        </div>
      </div>

      <div class="vr-dashboard">
        {#if vrState.isActive}
          <div class="active-scene">
            <div class="scene-info">
              <span class="scene-icon">{vrScenes[vrState.currentScene].icon}</span>
              <div class="scene-details">
                <h4>{vrScenes[vrState.currentScene].name}</h4>
                <p>{vrScenes[vrState.currentScene].description}</p>
              </div>
            </div>
            
            <div class="scene-progress">
              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  style="width: {(vrState.sceneProgress / vrScenes[vrState.currentScene].duration) * 100}%"
                ></div>
              </div>
              <span class="progress-text">
                {formatDuration(vrState.sceneProgress)} / {formatDuration(vrScenes[vrState.currentScene].duration)}
              </span>
            </div>

            <button class="stop-scene-button" on:click={stopVRScene}>
              🛑 Stop Scene
            </button>
          </div>
        {:else}
          <div class="scene-grid">
            {#each Object.entries(vrScenes) as [sceneId, scene]}
              <button 
                class="scene-button"
                on:click={() => startVRScene(sceneId)}
                style="--scene-color: {scene.color}"
              >
                <span class="scene-icon">{scene.icon}</span>
                <span class="scene-name">{scene.name}</span>
                <span class="scene-duration">{formatDuration(scene.duration)}</span>
                <span class="scene-desc">{scene.description}</span>
              </button>
            {/each}
          </div>
        {/if}
      </div>
    </div>

    <!-- Relationship AI Section -->
    <div class="feature-section relationship-section">
      <div class="section-header">
        <h3>Relationship AI</h3>
        <div class="status-indicator enabled">
          ✅ Available
        </div>
      </div>

      <div class="relationship-dashboard">
        <div class="health-score">
          <div class="score-circle" style="--health-color: {getHealthColor(relationshipAIState.healthScore)}">
            <span class="score-value">{relationshipAIState.healthScore}%</span>
            <span class="score-label">Health Score</span>
          </div>
        </div>

        <div class="ai-insights">
          <div class="insights-section">
            <h4>Recent Insights</h4>
            <div class="insights-list">
              {#each relationshipAIState.recentInsights.slice(0, 3) as insight}
                <div class="insight-item">
                  <span class="insight-icon">💡</span>
                  <span class="insight-text">{insight}</span>
                </div>
              {/each}
            </div>
          </div>

          <div class="insights-section">
            <h4>Recommendations</h4>
            <div class="insights-list">
              {#each relationshipAIState.recommendations.slice(0, 3) as recommendation}
                <div class="insight-item">
                  <span class="insight-icon">🎯</span>
                  <span class="insight-text">{recommendation}</span>
                </div>
              {/each}
            </div>
          </div>

          <div class="insights-section">
            <h4>Growth Opportunities</h4>
            <div class="insights-list">
              {#each relationshipAIState.growthOpportunities.slice(0, 3) as opportunity}
                <div class="insight-item">
                  <span class="insight-icon">🌱</span>
                  <span class="insight-text">{opportunity}</span>
                </div>
              {/each}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Status Bar -->
  <div class="status-bar">
    <div class="status-item">
      <span class="status-icon {phase3State.hapticEnabled ? 'success' : 'error'}">
        {phase3State.hapticEnabled ? '📳' : '❌'}
      </span>
      <span class="status-text">Haptic</span>
    </div>

    <div class="status-item">
      <span class="status-icon {phase3State.biometricEnabled ? 'success' : 'error'}">
        {phase3State.biometricEnabled ? '💓' : '❌'}
      </span>
      <span class="status-text">Biometric</span>
    </div>

    <div class="status-item">
      <span class="status-icon {phase3State.vrEnabled ? 'success' : 'error'}">
        {phase3State.vrEnabled ? '🥽' : '❌'}
      </span>
      <span class="status-text">VR</span>
    </div>

    <div class="status-item">
      <span class="status-icon {relationshipAIState.isActive ? 'active' : 'inactive'}">
        {relationshipAIState.isActive ? '🤖' : '⏸️'}
      </span>
      <span class="status-text">AI</span>
    </div>

    <div class="status-item">
      <span class="status-icon {hapticState.isActive ? 'active' : 'inactive'}">
        {hapticState.isActive ? '📳' : '🔇'}
      </span>
      <span class="status-text">{hapticState.isActive ? 'Active' : 'Inactive'}</span>
    </div>

    <div class="status-item">
      <span class="status-icon {vrState.isActive ? 'active' : 'inactive'}">
        {vrState.isActive ? '🥽' : '🔇'}
      </span>
      <span class="status-text">{vrState.isActive ? 'VR Active' : 'VR Ready'}</span>
    </div>
  </div>
</div>

<style>
  .phase3-features-interface {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }

  .phase3-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .phase3-header h2 {
    color: #2c3e50;
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
  }

  .phase3-header p {
    color: #6c757d;
    margin: 0;
    font-size: 1.1rem;
  }

  .phase3-main {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .feature-section {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1.5rem;
    border: 2px solid #e9ecef;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .section-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.3rem;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .status-indicator.enabled {
    background: #d4edda;
    color: #155724;
  }

  .status-indicator.disabled {
    background: #f8d7da;
    color: #721c24;
  }

  /* Haptic Section */
  .haptic-controls {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .control-group {
    display: flex;
    align-items: center;
  }

  .toggle-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
    color: #495057;
    cursor: pointer;
  }

  .pattern-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .pattern-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .pattern-button:hover:not(:disabled) {
    border-color: var(--pattern-color);
    background: #fff;
  }

  .pattern-button.active {
    border-color: var(--pattern-color);
    background: var(--pattern-color);
    color: white;
  }

  .pattern-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .pattern-icon {
    font-size: 1.5rem;
  }

  .pattern-name {
    font-weight: 600;
    font-size: 0.875rem;
  }

  .pattern-desc {
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

  .intensity-slider {
    width: 100%;
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
    outline: none;
    -webkit-appearance: none;
  }

  .intensity-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    background: #007bff;
    border-radius: 50%;
    cursor: pointer;
  }

  /* Biometric Section */
  .biometric-dashboard {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .metric-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    border: 1px solid #e9ecef;
  }

  .metric-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .metric-icon {
    font-size: 1.2rem;
  }

  .metric-name {
    font-size: 0.875rem;
    color: #6c757d;
  }

  .metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 0.25rem;
  }

  .metric-trend {
    font-size: 1.2rem;
  }

  .heart-rate-chart {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e9ecef;
  }

  .heart-rate-chart h4 {
    margin: 0 0 1rem 0;
    color: #2c3e50;
    font-size: 1rem;
  }

  .chart-container {
    display: flex;
    align-items: end;
    gap: 2px;
    height: 100px;
  }

  .chart-bar {
    flex: 1;
    min-width: 4px;
    border-radius: 2px 2px 0 0;
    transition: height 0.3s ease;
  }

  /* VR Section */
  .vr-dashboard {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .active-scene {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e9ecef;
  }

  .scene-info {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .scene-icon {
    font-size: 2rem;
  }

  .scene-details h4 {
    margin: 0 0 0.25rem 0;
    color: #2c3e50;
  }

  .scene-details p {
    margin: 0;
    color: #6c757d;
    font-size: 0.875rem;
  }

  .scene-progress {
    margin-bottom: 1rem;
  }

  .progress-bar {
    width: 100%;
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #007bff, #28a745);
    transition: width 0.3s ease;
  }

  .progress-text {
    font-size: 0.875rem;
    color: #6c757d;
  }

  .stop-scene-button {
    width: 100%;
    padding: 0.75rem;
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
  }

  .scene-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .scene-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .scene-button:hover {
    border-color: var(--scene-color);
    background: #fff;
  }

  .scene-button .scene-icon {
    font-size: 2rem;
  }

  .scene-button .scene-name {
    font-weight: 600;
    color: #2c3e50;
  }

  .scene-button .scene-duration {
    font-size: 0.875rem;
    color: #6c757d;
  }

  .scene-button .scene-desc {
    font-size: 0.75rem;
    color: #6c757d;
    text-align: center;
  }

  /* Relationship AI Section */
  .relationship-dashboard {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .health-score {
    display: flex;
    justify-content: center;
  }

  .score-circle {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 120px;
    height: 120px;
    border: 4px solid var(--health-color);
    border-radius: 50%;
    background: white;
  }

  .score-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--health-color);
  }

  .score-label {
    font-size: 0.75rem;
    color: #6c757d;
    text-align: center;
  }

  .ai-insights {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .insights-section {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e9ecef;
  }

  .insights-section h4 {
    margin: 0 0 0.75rem 0;
    color: #2c3e50;
    font-size: 1rem;
  }

  .insights-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .insight-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 4px;
  }

  .insight-icon {
    font-size: 1rem;
  }

  .insight-text {
    font-size: 0.875rem;
    color: #495057;
  }

  /* Status Bar */
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

  /* Mobile Responsive */
  @media (max-width: 768px) {
    .phase3-features-interface {
      padding: 1rem;
    }

    .phase3-main {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .metric-grid {
      grid-template-columns: 1fr;
    }

    .pattern-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    .scene-grid {
      grid-template-columns: 1fr;
    }

    .status-bar {
      flex-direction: column;
      gap: 0.5rem;
    }
  }
</style> 