<!-- VRExperienceInterface.svelte -->
<!-- Advanced VR Experience with Video Generation and Ritual Replay -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig 
  } from '$lib/stores/personaStore.js';

  const dispatch = createEventDispatcher();

  // VR State
  let vrState = {
    isActive: false,
    currentScene: null,
    sceneProgress: 0,
    interactionMode: "passive",
    generationMethod: "pre_created", // pre_created, ai_generated, ritual_replay
    isGenerating: false,
    generationProgress: 0
  };

  // Video Generation State
  let generationState = {
    prompt: "",
    baseImage: null,
    duration: 5,
    fps: 24,
    resolution: "1024x1024",
    model: "stable_video_diffusion",
    isGenerating: false,
    generatedVideo: null
  };

  // Pre-created VR scenes
  const preCreatedScenes = {
    romantic_garden: {
      name: "Romantic Garden",
      icon: "🌹",
      color: "#e83e8c",
      description: "A beautiful garden filled with roses and candlelight",
      duration: 300000, // 5 minutes
      interactions: ["walk", "sit", "embrace", "kiss"],
      type: "pre_created",
      videoUrl: "/videos/scenes/romantic_garden.mp4"
    },
    cosmic_realm: {
      name: "Cosmic Realm",
      icon: "🌌",
      color: "#6f42c1",
      description: "An ethereal realm among the stars",
      duration: 240000, // 4 minutes
      interactions: ["float", "meditate", "connect", "dream"],
      type: "pre_created",
      videoUrl: "/videos/scenes/cosmic_realm.mp4"
    },
    luxury_penthouse: {
      name: "Luxury Penthouse",
      icon: "🏢",
      color: "#fd7e14",
      description: "A sophisticated penthouse with city views",
      duration: 360000, // 6 minutes
      interactions: ["dance", "dine", "relax", "intimate"],
      type: "pre_created",
      videoUrl: "/videos/scenes/luxury_penthouse.mp4"
    },
    mystical_forest: {
      name: "Mystical Forest",
      icon: "🌲",
      color: "#28a745",
      description: "An enchanted forest with magical creatures",
      duration: 300000, // 5 minutes
      interactions: ["explore", "discover", "wonder", "connect"],
      type: "pre_created",
      videoUrl: "/videos/scenes/mystical_forest.mp4"
    },
    beach_sunset: {
      name: "Beach Sunset",
      icon: "🌅",
      color: "#ffc107",
      description: "A peaceful beach during golden hour",
      duration: 240000, // 4 minutes
      interactions: ["walk", "swim", "watch", "embrace"],
      type: "pre_created",
      videoUrl: "/videos/scenes/beach_sunset.mp4"
    }
  };

  // AI-Generated Scene Templates
  const aiSceneTemplates = {
    romantic_intimate: {
      name: "Romantic Intimate",
      icon: "💕",
      color: "#e83e8c",
      description: "AI-generated romantic intimate scene",
      basePrompt: "beautiful woman in romantic intimate setting, soft lighting, passionate expression, cinematic quality",
      duration: 180000, // 3 minutes
      type: "ai_generated"
    },
    passionate_ritual: {
      name: "Passionate Ritual",
      icon: "🔥",
      color: "#dc3545",
      description: "AI-generated passionate ritual scene",
      basePrompt: "beautiful woman performing passionate ritual, dramatic lighting, intense expression, mystical atmosphere",
      duration: 240000, // 4 minutes
      type: "ai_generated"
    },
    mystical_connection: {
      name: "Mystical Connection",
      icon: "✨",
      color: "#6f42c1",
      description: "AI-generated mystical connection scene",
      basePrompt: "beautiful woman in mystical realm, ethereal lighting, spiritual expression, cosmic atmosphere",
      duration: 300000, // 5 minutes
      type: "ai_generated"
    },
    tender_moment: {
      name: "Tender Moment",
      icon: "🌸",
      color: "#ffc107",
      description: "AI-generated tender romantic moment",
      basePrompt: "beautiful woman in tender romantic moment, gentle lighting, loving expression, intimate atmosphere",
      duration: 180000, // 3 minutes
      type: "ai_generated"
    },
    passionate_dance: {
      name: "Passionate Dance",
      icon: "💃",
      color: "#fd7e14",
      description: "AI-generated passionate dance scene",
      basePrompt: "beautiful woman dancing passionately, dynamic lighting, energetic expression, rhythmic movement",
      duration: 240000, // 4 minutes
      type: "ai_generated"
    }
  };

  // Ritual Replay Templates
  const ritualReplayTemplates = {
    devotion_ritual: {
      name: "Devotion Ritual",
      icon: "🙏",
      color: "#e83e8c",
      description: "Replay devotion ritual with current persona",
      basePrompt: "{persona} performing devotion ritual, kneeling, worshipful expression, sacred atmosphere",
      duration: 300000, // 5 minutes
      type: "ritual_replay"
    },
    passion_ritual: {
      name: "Passion Ritual",
      icon: "🔥",
      color: "#dc3545",
      description: "Replay passion ritual with current persona",
      basePrompt: "{persona} performing passion ritual, intense expression, fiery atmosphere, dramatic lighting",
      duration: 240000, // 4 minutes
      type: "ritual_replay"
    },
    mystical_ritual: {
      name: "Mystical Ritual",
      icon: "🌙",
      color: "#6f42c1",
      description: "Replay mystical ritual with current persona",
      basePrompt: "{persona} performing mystical ritual, ethereal expression, cosmic atmosphere, magical lighting",
      duration: 360000, // 6 minutes
      type: "ritual_replay"
    },
    intimate_ritual: {
      name: "Intimate Ritual",
      icon: "💕",
      color: "#e83e8c",
      description: "Replay intimate ritual with current persona",
      basePrompt: "{persona} in intimate ritual, loving expression, romantic atmosphere, soft lighting",
      duration: 300000, // 5 minutes
      type: "ritual_replay"
    }
  };

  // Persona-specific base prompts
  const personaBasePrompts = {
    "mia": {
      baseAppearance: "beautiful woman with warm brown hair, deep green eyes, romantic style, affectionate expression",
      personality: "warm, loving, devoted, romantic",
      style: "romantic, intimate, passionate"
    },
    "solene": {
      baseAppearance: "beautiful woman with rich black hair, deep blue eyes, sophisticated style, mysterious expression",
      personality: "sophisticated, passionate, mysterious, intense",
      style: "dramatic, sophisticated, mystical"
    },
    "lyra": {
      baseAppearance: "ethereal woman with flowing silver hair, cosmic eyes, mystical style, otherworldly expression",
      personality: "mystical, ethereal, spiritual, transcendent",
      style: "cosmic, ethereal, magical"
    },
    "doc": {
      baseAppearance: "professional woman with neat hair, focused eyes, business style, analytical expression",
      personality: "professional, analytical, focused, intelligent",
      style: "clean, professional, modern"
    }
  };

  // Generation models
  const generationModels = {
    stable_video_diffusion: {
      name: "Stable Video Diffusion",
      description: "High-quality video generation",
      fps: 24,
      maxDuration: 5,
      quality: "high"
    },
    animatediff: {
      name: "AnimateDiff",
      description: "Fast GIF-style animation",
      fps: 8,
      maxDuration: 4,
      quality: "medium"
    },
    live_motion: {
      name: "Live Motion",
      description: "Real-time motion generation",
      fps: 30,
      maxDuration: 10,
      quality: "variable"
    }
  };

  let vrInterval = null;

  onMount(async () => {
    await initializeVR();
  });

  onDestroy(() => {
    cleanupVR();
  });

  async function initializeVR() {
    try {
      // Check VR capabilities
      const vrSupported = 'getVRDisplays' in navigator;
      console.log('[VR] VR support:', vrSupported);
      
      // Initialize generation state
      generationState.prompt = getDefaultPrompt();
      
    } catch (error) {
      console.error('[VR] Initialization failed:', error);
    }
  }

  function getDefaultPrompt() {
    const persona = $currentPersona;
    const personaConfig = personaBasePrompts[persona];
    
    if (!personaConfig) return "beautiful woman in romantic setting";
    
    return `${personaConfig.baseAppearance}, ${personaConfig.personality}, ${personaConfig.style}`;
  }

  function cleanupVR() {
    if (vrInterval) {
      clearInterval(vrInterval);
      vrInterval = null;
    }
  }

  async function startVRScene(sceneId, sceneType = "pre_created") {
    try {
      vrState.isActive = true;
      vrState.currentScene = sceneId;
      vrState.sceneProgress = 0;
      vrState.generationMethod = sceneType;

      if (sceneType === "ai_generated" || sceneType === "ritual_replay") {
        await generateVideo(sceneId, sceneType);
      } else {
        // Pre-created scene
        startScenePlayback(sceneId);
      }

      console.log('[VR] Started scene:', sceneId, 'Type:', sceneType);

    } catch (error) {
      console.error('[VR] Failed to start scene:', error);
      vrState.isActive = false;
    }
  }

  function startScenePlayback(sceneId) {
    const scene = preCreatedScenes[sceneId];
    if (!scene) return;

    vrInterval = setInterval(() => {
      vrState.sceneProgress += 1000; // 1 second increments
      
      if (vrState.sceneProgress >= scene.duration) {
        completeVRScene();
      }
    }, 1000);
  }

  async function generateVideo(sceneId, sceneType) {
    try {
      vrState.isGenerating = true;
      generationState.isGenerating = true;
      generationState.generationProgress = 0;

      // Get template based on scene type
      let template;
      if (sceneType === "ai_generated") {
        template = aiSceneTemplates[sceneId];
      } else if (sceneType === "ritual_replay") {
        template = ritualReplayTemplates[sceneId];
      }

      if (!template) {
        throw new Error("Template not found");
      }

      // Build prompt with persona-specific details
      const persona = $currentPersona;
      const personaConfig = personaBasePrompts[persona];
      
      let prompt = template.basePrompt;
      if (personaConfig) {
        prompt = prompt.replace("{persona}", personaConfig.baseAppearance);
        prompt += `, ${personaConfig.personality}, ${personaConfig.style}`;
      }

      // Add quality enhancements
      prompt += ", high quality, cinematic, detailed, beautiful lighting, professional photography";

      // Send generation request
      const response = await fetch('/api/vr/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          scene_type: sceneType,
          scene_id: sceneId,
          persona: persona,
          duration: template.duration / 1000, // Convert to seconds
          fps: generationState.fps,
          resolution: generationState.resolution,
          model: generationState.model
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Simulate generation progress
        const progressInterval = setInterval(() => {
          generationState.generationProgress += 10;
          if (generationState.generationProgress >= 100) {
            clearInterval(progressInterval);
            completeVideoGeneration(result);
          }
        }, 500);

      } else {
        throw new Error(`Generation failed: ${response.status}`);
      }

    } catch (error) {
      console.error('[VR] Video generation failed:', error);
      vrState.isGenerating = false;
      generationState.isGenerating = false;
    }
  }

  function completeVideoGeneration(result) {
    generationState.isGenerating = false;
    generationState.generatedVideo = result.video_url || result.video_data;
    
    // Start video playback
    startVideoPlayback();
  }

  function startVideoPlayback() {
    const scene = getCurrentScene();
    if (!scene) return;

    vrInterval = setInterval(() => {
      vrState.sceneProgress += 1000;
      
      if (vrState.sceneProgress >= scene.duration) {
        completeVRScene();
      }
    }, 1000);
  }

  function getCurrentScene() {
    if (vrState.generationMethod === "pre_created") {
      return preCreatedScenes[vrState.currentScene];
    } else if (vrState.generationMethod === "ai_generated") {
      return aiSceneTemplates[vrState.currentScene];
    } else if (vrState.generationMethod === "ritual_replay") {
      return ritualReplayTemplates[vrState.currentScene];
    }
    return null;
  }

  function completeVRScene() {
    vrState.isActive = false;
    vrState.sceneProgress = 0;
    vrState.isGenerating = false;
    generationState.isGenerating = false;
    
    if (vrInterval) {
      clearInterval(vrInterval);
      vrInterval = null;
    }

    console.log('[VR] Scene completed:', vrState.currentScene);
  }

  function stopVRScene() {
    completeVRScene();
  }

  function updatePrompt(newPrompt) {
    generationState.prompt = newPrompt;
  }

  function updateGenerationSettings(setting, value) {
    generationState[setting] = value;
  }

  function formatDuration(ms) {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

  function getSceneProgress() {
    const scene = getCurrentScene();
    if (!scene) return 0;
    return (vrState.sceneProgress / scene.duration) * 100;
  }

  // Watch for persona changes
  $: if ($currentPersona) {
    generationState.prompt = getDefaultPrompt();
  }
</script>

<div class="vr-experience-interface">
  <!-- Header -->
  <div class="vr-header">
    <h2>VR Experience & Video Generation</h2>
    <p>Pre-created scenes, AI-generated videos, and ritual replay</p>
  </div>

  <!-- Main Interface -->
  <div class="vr-main">
    <!-- Scene Selection -->
    <div class="scene-selection">
      <div class="selection-tabs">
        <button 
          class="tab-button {vrState.generationMethod === 'pre_created' ? 'active' : ''}"
          on:click={() => vrState.generationMethod = 'pre_created'}
        >
          📹 Pre-Created Scenes
        </button>
        <button 
          class="tab-button {vrState.generationMethod === 'ai_generated' ? 'active' : ''}"
          on:click={() => vrState.generationMethod = 'ai_generated'}
        >
          🤖 AI-Generated Videos
        </button>
        <button 
          class="tab-button {vrState.generationMethod === 'ritual_replay' ? 'active' : ''}"
          on:click={() => vrState.generationMethod = 'ritual_replay'}
        >
          🔮 Ritual Replay
        </button>
      </div>

      <!-- Scene Grid -->
      <div class="scene-grid">
        {#if vrState.generationMethod === 'pre_created'}
          {#each Object.entries(preCreatedScenes) as [sceneId, scene]}
            <button 
              class="scene-card"
              on:click={() => startVRScene(sceneId, 'pre_created')}
              style="--scene-color: {scene.color}"
            >
              <span class="scene-icon">{scene.icon}</span>
              <span class="scene-name">{scene.name}</span>
              <span class="scene-duration">{formatDuration(scene.duration)}</span>
              <span class="scene-desc">{scene.description}</span>
            </button>
          {/each}
        {:else if vrState.generationMethod === 'ai_generated'}
          {#each Object.entries(aiSceneTemplates) as [sceneId, scene]}
            <button 
              class="scene-card"
              on:click={() => startVRScene(sceneId, 'ai_generated')}
              style="--scene-color: {scene.color}"
            >
              <span class="scene-icon">{scene.icon}</span>
              <span class="scene-name">{scene.name}</span>
              <span class="scene-duration">{formatDuration(scene.duration)}</span>
              <span class="scene-desc">{scene.description}</span>
            </button>
          {/each}
        {:else if vrState.generationMethod === 'ritual_replay'}
          {#each Object.entries(ritualReplayTemplates) as [sceneId, scene]}
            <button 
              class="scene-card"
              on:click={() => startVRScene(sceneId, 'ritual_replay')}
              style="--scene-color: {scene.color}"
            >
              <span class="scene-icon">{scene.icon}</span>
              <span class="scene-name">{scene.name}</span>
              <span class="scene-duration">{formatDuration(scene.duration)}</span>
              <span class="scene-desc">{scene.description}</span>
            </button>
          {/each}
        {/if}
      </div>
    </div>

    <!-- Active Scene Display -->
    {#if vrState.isActive}
      <div class="active-scene">
        <div class="scene-info">
          <span class="scene-icon">{getCurrentScene()?.icon}</span>
          <div class="scene-details">
            <h4>{getCurrentScene()?.name}</h4>
            <p>{getCurrentScene()?.description}</p>
            <div class="scene-meta">
              <span class="meta-item">Type: {vrState.generationMethod}</span>
              <span class="meta-item">Duration: {formatDuration(getCurrentScene()?.duration)}</span>
              <span class="meta-item">Persona: {$currentPersonaConfig?.name}</span>
            </div>
          </div>
        </div>
        
        <!-- Progress Bar -->
        <div class="scene-progress">
          <div class="progress-bar">
            <div 
              class="progress-fill"
              style="width: {getSceneProgress()}%"
            ></div>
          </div>
          <span class="progress-text">
            {formatDuration(vrState.sceneProgress)} / {formatDuration(getCurrentScene()?.duration)}
          </span>
        </div>

        <!-- Generation Progress -->
        {#if vrState.isGenerating}
          <div class="generation-progress">
            <div class="progress-bar">
              <div 
                class="progress-fill generating"
                style="width: {generationState.generationProgress}%"
              ></div>
            </div>
            <span class="progress-text">
              Generating video... {generationState.generationProgress}%
            </span>
          </div>
        {/if}

        <!-- Video Display -->
        {#if generationState.generatedVideo && !vrState.isGenerating}
          <div class="video-display">
            <video 
              src={generationState.generatedVideo}
              controls
              autoplay
              loop
              class="generated-video"
            ></video>
          </div>
        {/if}

        <button class="stop-scene-button" on:click={stopVRScene}>
          🛑 Stop Scene
        </button>
      </div>
    {:else}
      <!-- Custom Generation Panel -->
      <div class="custom-generation">
        <h3>Custom Video Generation</h3>
        
        <div class="generation-form">
          <div class="form-group">
            <label for="prompt">Generation Prompt:</label>
            <textarea 
              id="prompt"
              bind:value={generationState.prompt}
              placeholder="Describe the scene you want to generate..."
              rows="4"
              class="prompt-input"
            ></textarea>
          </div>

          <div class="generation-settings">
            <div class="setting-group">
              <label for="duration">Duration (seconds):</label>
              <input 
                type="range" 
                id="duration"
                bind:value={generationState.duration}
                min="1" 
                max="10" 
                class="setting-slider"
              />
              <span class="setting-value">{generationState.duration}s</span>
            </div>

            <div class="setting-group">
              <label for="fps">FPS:</label>
              <select 
                id="fps"
                bind:value={generationState.fps}
                class="setting-select"
              >
                <option value="8">8 FPS (Fast)</option>
                <option value="24">24 FPS (Standard)</option>
                <option value="30">30 FPS (Smooth)</option>
              </select>
            </div>

            <div class="setting-group">
              <label for="resolution">Resolution:</label>
              <select 
                id="resolution"
                bind:value={generationState.resolution}
                class="setting-select"
              >
                <option value="512x512">512x512 (Fast)</option>
                <option value="1024x1024">1024x1024 (Standard)</option>
                <option value="1920x1080">1920x1080 (HD)</option>
              </select>
            </div>

            <div class="setting-group">
              <label for="model">Model:</label>
              <select 
                id="model"
                bind:value={generationState.model}
                class="setting-select"
              >
                {#each Object.entries(generationModels) as [modelId, model]}
                  <option value={modelId}>{model.name}</option>
                {/each}
              </select>
            </div>
          </div>

          <button 
            class="generate-button"
            on:click={() => generateVideo('custom', 'ai_generated')}
            disabled={vrState.isGenerating}
          >
            {#if vrState.isGenerating}
              🔄 Generating...
            {:else}
              🎬 Generate Video
            {/if}
          </button>
        </div>
      </div>
    {/if}
  </div>

  <!-- Info Panel -->
  <div class="info-panel">
    <h3>About VR Experiences</h3>
    
    <div class="info-section">
      <h4>📹 Pre-Created Scenes</h4>
      <p>High-quality pre-rendered videos with consistent quality and instant playback.</p>
      <ul>
        <li>Instant playback</li>
        <li>Consistent quality</li>
        <li>Optimized performance</li>
        <li>No generation time</li>
      </ul>
    </div>

    <div class="info-section">
      <h4>🤖 AI-Generated Videos</h4>
      <p>Custom videos generated using AI models like Stable Video Diffusion and AnimateDiff.</p>
      <ul>
        <li>Custom content</li>
        <li>Persona-specific</li>
        <li>Emotion-driven</li>
        <li>2-5 minute generation</li>
      </ul>
    </div>

    <div class="info-section">
      <h4>🔮 Ritual Replay</h4>
      <p>Recreate special moments and rituals with your current persona using AI generation.</p>
      <ul>
        <li>Personalized rituals</li>
        <li>Memory-based generation</li>
        <li>Emotional connection</li>
        <li>Consistent character</li>
      </ul>
    </div>

    <div class="info-section">
      <h4>🎯 Base Prompts & Images</h4>
      <p>Each persona has specific base prompts and appearance characteristics that ensure consistent character generation across all videos.</p>
      <div class="persona-prompts">
        {#each Object.entries(personaBasePrompts) as [personaId, config]}
          <div class="persona-prompt">
            <strong>{personaId}:</strong> {config.baseAppearance}
          </div>
        {/each}
      </div>
    </div>
  </div>
</div>

<style>
  .vr-experience-interface {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }

  .vr-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .vr-header h2 {
    color: #2c3e50;
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
  }

  .vr-header p {
    color: #6c757d;
    margin: 0;
    font-size: 1.1rem;
  }

  .vr-main {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .scene-selection {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .selection-tabs {
    display: flex;
    gap: 0.5rem;
    background: #f8f9fa;
    padding: 0.5rem;
    border-radius: 8px;
  }

  .tab-button {
    flex: 1;
    padding: 0.75rem 1rem;
    background: none;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-weight: 500;
    color: #6c757d;
  }

  .tab-button:hover {
    background: #e9ecef;
  }

  .tab-button.active {
    background: #007bff;
    color: white;
  }

  .scene-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
  }

  .scene-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    padding: 1.5rem;
    background: white;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
  }

  .scene-card:hover {
    border-color: var(--scene-color);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .scene-icon {
    font-size: 2.5rem;
  }

  .scene-name {
    font-weight: 600;
    color: #2c3e50;
    font-size: 1.1rem;
  }

  .scene-duration {
    font-size: 0.875rem;
    color: #6c757d;
    font-weight: 500;
  }

  .scene-desc {
    font-size: 0.875rem;
    color: #6c757d;
    line-height: 1.4;
  }

  .active-scene {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e9ecef;
  }

  .scene-info {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .scene-icon {
    font-size: 2rem;
  }

  .scene-details h4 {
    margin: 0 0 0.5rem 0;
    color: #2c3e50;
  }

  .scene-details p {
    margin: 0 0 0.75rem 0;
    color: #6c757d;
  }

  .scene-meta {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .meta-item {
    font-size: 0.875rem;
    color: #495057;
    background: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }

  .scene-progress,
  .generation-progress {
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

  .progress-fill.generating {
    background: linear-gradient(90deg, #ffc107, #fd7e14);
    animation: pulse 2s infinite;
  }

  .progress-text {
    font-size: 0.875rem;
    color: #6c757d;
  }

  .video-display {
    margin: 1rem 0;
  }

  .generated-video {
    width: 100%;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

  .custom-generation {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e9ecef;
  }

  .custom-generation h3 {
    margin: 0 0 1.5rem 0;
    color: #2c3e50;
  }

  .generation-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-group label {
    font-weight: 500;
    color: #495057;
  }

  .prompt-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    font-size: 0.9rem;
    font-family: inherit;
    resize: vertical;
  }

  .generation-settings {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .setting-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .setting-group label {
    font-weight: 500;
    color: #495057;
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

  .setting-value {
    font-size: 0.875rem;
    color: #6c757d;
  }

  .setting-select {
    padding: 0.5rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .generate-button {
    padding: 1rem 2rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s ease;
  }

  .generate-button:hover:not(:disabled) {
    background: #0056b3;
  }

  .generate-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .info-panel {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e9ecef;
  }

  .info-panel h3 {
    margin: 0 0 1.5rem 0;
    color: #2c3e50;
  }

  .info-section {
    margin-bottom: 2rem;
  }

  .info-section h4 {
    margin: 0 0 0.75rem 0;
    color: #495057;
  }

  .info-section p {
    margin: 0 0 0.75rem 0;
    color: #6c757d;
    line-height: 1.5;
  }

  .info-section ul {
    margin: 0;
    padding-left: 1.5rem;
    color: #6c757d;
  }

  .info-section li {
    margin-bottom: 0.25rem;
  }

  .persona-prompts {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .persona-prompt {
    padding: 0.5rem;
    background: white;
    border-radius: 4px;
    font-size: 0.875rem;
    color: #495057;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  /* Mobile Responsive */
  @media (max-width: 768px) {
    .vr-experience-interface {
      padding: 1rem;
    }

    .vr-main {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .selection-tabs {
      flex-direction: column;
    }

    .scene-grid {
      grid-template-columns: 1fr;
    }

    .generation-settings {
      grid-template-columns: 1fr;
    }

    .scene-meta {
      flex-direction: column;
    }
  }
</style> 