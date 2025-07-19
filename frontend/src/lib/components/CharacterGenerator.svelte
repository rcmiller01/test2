<!-- CharacterGenerator.svelte -->
<!-- Character Generation Interface for 4-Persona EmotionalAI System -->

<script>
  import { onMount } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig, 
    AVAILABLE_PERSONAS 
  } from '$lib/stores/personaStore.js';
  import { 
    isCompanionMode, 
    currentFeatures 
  } from '$lib/stores/uiModeStore.js';

  // Component state
  let showGenerator = false;
  let isGenerating = false;
  let generatedImage = null;
  let generationError = null;
  let generationProgress = 0;

  // Character customization options
  let characterSettings = {
    persona: 'mia',
    style: 'romantic_casual',
    hair_color: 'warm_brown',
    eye_color: 'deep_green',
    outfit: 'casual_elegant',
    background: 'cozy_home',
    mood: 'warm_affectionate',
    pose: 'natural_standing',
    lighting: 'soft_warm',
    nsfw_level: 'safe'
  };

  // Available customization options
  const customizationOptions = {
    style: [
      { value: 'romantic_casual', label: 'Romantic Casual', icon: '💕' },
      { value: 'sophisticated_elegant', label: 'Sophisticated Elegant', icon: '🌹' },
      { value: 'mystical_flowing', label: 'Mystical Flowing', icon: '✨' },
      { value: 'professional_clean', label: 'Professional Clean', icon: '💼' }
    ],
    hair_color: [
      { value: 'warm_brown', label: 'Warm Brown', color: '#8B4513' },
      { value: 'rich_black', label: 'Rich Black', color: '#000000' },
      { value: 'ethereal_silver', label: 'Ethereal Silver', color: '#C0C0C0' },
      { value: 'professional_dark', label: 'Professional Dark', color: '#2F2F2F' }
    ],
    eye_color: [
      { value: 'deep_green', label: 'Deep Green', color: '#228B22' },
      { value: 'deep_blue', label: 'Deep Blue', color: '#000080' },
      { value: 'mystical_violet', label: 'Mystical Violet', color: '#8A2BE2' },
      { value: 'sharp_blue', label: 'Sharp Blue', color: '#4169E1' }
    ],
    outfit: [
      { value: 'casual_elegant', label: 'Casual Elegant', icon: '👗' },
      { value: 'sophisticated_dress', label: 'Sophisticated Dress', icon: '👠' },
      { value: 'mystical_robes', label: 'Mystical Robes', icon: '🧙‍♀️' },
      { value: 'professional_suit', label: 'Professional Suit', icon: '👔' }
    ],
    background: [
      { value: 'cozy_home', label: 'Cozy Home', icon: '🏠' },
      { value: 'elegant_parlor', label: 'Elegant Parlor', icon: '🏛️' },
      { value: 'mystical_realm', label: 'Mystical Realm', icon: '🌟' },
      { value: 'modern_office', label: 'Modern Office', icon: '🏢' }
    ],
    mood: [
      { value: 'warm_affectionate', label: 'Warm & Affectionate', icon: '💕' },
      { value: 'sophisticated_mysterious', label: 'Sophisticated & Mysterious', icon: '🌹' },
      { value: 'curious_mysterious', label: 'Curious & Mysterious', icon: '✨' },
      { value: 'analytical_focused', label: 'Analytical & Focused', icon: '💻' }
    ],
    pose: [
      { value: 'natural_standing', label: 'Natural Standing', icon: '🧍' },
      { value: 'elegant_sitting', label: 'Elegant Sitting', icon: '🪑' },
      { value: 'mystical_floating', label: 'Mystical Floating', icon: '🕊️' },
      { value: 'professional_pose', label: 'Professional Pose', icon: '👔' }
    ],
    lighting: [
      { value: 'soft_warm', label: 'Soft & Warm', icon: '🕯️' },
      { value: 'dramatic_elegant', label: 'Dramatic & Elegant', icon: '💡' },
      { value: 'ethereal_mystical', label: 'Ethereal & Mystical', icon: '✨' },
      { value: 'bright_professional', label: 'Bright & Professional', icon: '💡' }
    ],
    nsfw_level: [
      { value: 'safe', label: 'Safe', icon: '🛡️' },
      { value: 'suggestive', label: 'Suggestive', icon: '😊' },
      { value: 'romantic', label: 'Romantic', icon: '💕' },
      { value: 'explicit', label: 'Explicit', icon: '🔥' }
    ]
  };

  // Update character settings when persona changes
  $: if ($currentPersonaConfig) {
    characterSettings.persona = $currentPersona;
    characterSettings.style = $currentPersonaConfig.characteristics?.style || 'romantic_casual';
    characterSettings.hair_color = $currentPersonaConfig.characteristics?.hair_color || 'warm_brown';
    characterSettings.eye_color = $currentPersonaConfig.characteristics?.eye_color || 'deep_green';
    characterSettings.mood = $currentPersonaConfig.characteristics?.personality || 'warm_affectionate';
  }

  // Toggle generator visibility
  function toggleGenerator() {
    showGenerator = !showGenerator;
  }

  // Generate character image
  async function generateCharacter() {
    if (isGenerating) return;
    
    isGenerating = true;
    generationError = null;
    generationProgress = 0;
    
    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        generationProgress += Math.random() * 15;
        if (generationProgress >= 90) {
          clearInterval(progressInterval);
        }
      }, 500);

      // Call character generation API
      const response = await fetch('/api/phase2/character/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          persona: characterSettings.persona,
          settings: characterSettings,
          nsfw_enabled: $currentFeatures.nsfw_generation
        })
      });

      clearInterval(progressInterval);
      generationProgress = 100;

      if (!response.ok) {
        throw new Error(`Generation failed: ${response.status}`);
      }

      const data = await response.json();
      generatedImage = data.image_url;
      
      // Auto-hide generator after successful generation
      setTimeout(() => {
        showGenerator = false;
      }, 2000);

    } catch (error) {
      generationError = error.message;
      console.error('Character generation error:', error);
    } finally {
      isGenerating = false;
      generationProgress = 0;
    }
  }

  // Download generated image
  function downloadImage() {
    if (!generatedImage) return;
    
    const link = document.createElement('a');
    link.href = generatedImage;
    link.download = `${characterSettings.persona}_character_${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // Reset to persona defaults
  function resetToDefaults() {
    if ($currentPersonaConfig) {
      characterSettings = {
        persona: $currentPersona,
        style: $currentPersonaConfig.characteristics?.style || 'romantic_casual',
        hair_color: $currentPersonaConfig.characteristics?.hair_color || 'warm_brown',
        eye_color: $currentPersonaConfig.characteristics?.eye_color || 'deep_green',
        outfit: 'casual_elegant',
        background: 'cozy_home',
        mood: $currentPersonaConfig.characteristics?.personality || 'warm_affectionate',
        pose: 'natural_standing',
        lighting: 'soft_warm',
        nsfw_level: 'safe'
      };
    }
  }

  onMount(() => {
    resetToDefaults();
  });
</script>

<div class="character-generator">
  <!-- Generator Toggle Button -->
  <button
    class="generator-toggle-btn flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
    on:click={toggleGenerator}
    disabled={!$isCompanionMode}
  >
    <span class="text-lg">🎨</span>
    <span class="font-medium">Generate Character</span>
    <svg class="w-4 h-4 transition-transform duration-200 {showGenerator ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
    </svg>
  </button>

  <!-- Generator Panel -->
  {#if showGenerator}
    <div class="generator-panel fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="generator-modal bg-gray-800 rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="generator-header flex items-center justify-between p-6 border-b border-gray-700">
          <div class="flex items-center gap-3">
            <span class="text-2xl">🎨</span>
            <div>
              <h2 class="text-xl font-semibold text-white">Character Generator</h2>
              <p class="text-sm text-gray-400">Create your perfect {characterSettings.persona} character</p>
            </div>
          </div>
          
          <button
            class="close-btn p-2 text-gray-400 hover:text-white transition-colors duration-200"
            on:click={toggleGenerator}
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Content -->
        <div class="generator-content p-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Settings Panel -->
            <div class="settings-panel space-y-6">
              <h3 class="text-lg font-semibold text-white mb-4">Customization Options</h3>
              
              <!-- Style Selection -->
              <div class="setting-group">
                <label class="block text-sm font-medium text-gray-300 mb-2">Style</label>
                <div class="grid grid-cols-2 gap-2">
                  {#each customizationOptions.style as option}
                    <button
                      class="option-btn p-3 rounded-lg border transition-all duration-200 {characterSettings.style === option.value ? 'border-purple-500 bg-purple-500/20 text-white' : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'}"
                      on:click={() => characterSettings.style = option.value}
                    >
                      <span class="text-lg">{option.icon}</span>
                      <span class="block text-xs mt-1">{option.label}</span>
                    </button>
                  {/each}
                </div>
              </div>

              <!-- Hair Color -->
              <div class="setting-group">
                <label class="block text-sm font-medium text-gray-300 mb-2">Hair Color</label>
                <div class="grid grid-cols-2 gap-2">
                  {#each customizationOptions.hair_color as option}
                    <button
                      class="option-btn p-3 rounded-lg border transition-all duration-200 {characterSettings.hair_color === option.value ? 'border-purple-500 bg-purple-500/20 text-white' : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'}"
                      on:click={() => characterSettings.hair_color = option.value}
                    >
                      <div class="w-4 h-4 rounded-full mx-auto mb-1" style="background-color: {option.color}"></div>
                      <span class="block text-xs">{option.label}</span>
                    </button>
                  {/each}
                </div>
              </div>

              <!-- Eye Color -->
              <div class="setting-group">
                <label class="block text-sm font-medium text-gray-300 mb-2">Eye Color</label>
                <div class="grid grid-cols-2 gap-2">
                  {#each customizationOptions.eye_color as option}
                    <button
                      class="option-btn p-3 rounded-lg border transition-all duration-200 {characterSettings.eye_color === option.value ? 'border-purple-500 bg-purple-500/20 text-white' : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'}"
                      on:click={() => characterSettings.eye_color = option.value}
                    >
                      <div class="w-4 h-4 rounded-full mx-auto mb-1" style="background-color: {option.color}"></div>
                      <span class="block text-xs">{option.label}</span>
                    </button>
                  {/each}
                </div>
              </div>

              <!-- NSFW Level (only if enabled) -->
              {#if $currentFeatures.nsfw_generation}
                <div class="setting-group">
                  <label class="block text-sm font-medium text-gray-300 mb-2">Content Level</label>
                  <div class="grid grid-cols-2 gap-2">
                    {#each customizationOptions.nsfw_level as option}
                      <button
                        class="option-btn p-3 rounded-lg border transition-all duration-200 {characterSettings.nsfw_level === option.value ? 'border-purple-500 bg-purple-500/20 text-white' : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'}"
                        on:click={() => characterSettings.nsfw_level = option.value}
                      >
                        <span class="text-lg">{option.icon}</span>
                        <span class="block text-xs mt-1">{option.label}</span>
                      </button>
                    {/each}
                  </div>
                </div>
              {/if}

              <!-- Action Buttons -->
              <div class="action-buttons flex gap-3">
                <button
                  class="reset-btn flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200"
                  on:click={resetToDefaults}
                >
                  Reset to Defaults
                </button>
                
                <button
                  class="generate-btn flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  on:click={generateCharacter}
                  disabled={isGenerating}
                >
                  {#if isGenerating}
                    <div class="flex items-center gap-2">
                      <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      <span>Generating...</span>
                    </div>
                  {:else}
                    <span>Generate Character</span>
                  {/if}
                </button>
              </div>
            </div>

            <!-- Preview Panel -->
            <div class="preview-panel">
              <h3 class="text-lg font-semibold text-white mb-4">Preview</h3>
              
              <!-- Generation Progress -->
              {#if isGenerating}
                <div class="generation-progress bg-gray-700 rounded-lg p-6 text-center">
                  <div class="w-16 h-16 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mx-auto mb-4"></div>
                  <h4 class="text-lg font-semibold text-white mb-2">Generating Character...</h4>
                  <p class="text-gray-400 mb-4">Creating your perfect {characterSettings.persona} character</p>
                  
                  <div class="progress-bar bg-gray-600 rounded-full h-2 mb-2">
                    <div 
                      class="progress-fill bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-300"
                      style="width: {generationProgress}%"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-400">{Math.round(generationProgress)}%</span>
                </div>
              {:else if generatedImage}
                <!-- Generated Image -->
                <div class="generated-image bg-gray-700 rounded-lg p-4">
                  <img 
                    src={generatedImage} 
                    alt="Generated Character" 
                    class="w-full h-auto rounded-lg shadow-lg"
                  />
                  
                  <div class="mt-4 flex gap-2">
                    <button
                      class="download-btn flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200"
                      on:click={downloadImage}
                    >
                      Download
                    </button>
                    <button
                      class="regenerate-btn flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200"
                      on:click={generateCharacter}
                    >
                      Regenerate
                    </button>
                  </div>
                </div>
              {:else}
                <!-- Preview Placeholder -->
                <div class="preview-placeholder bg-gray-700 rounded-lg p-8 text-center">
                  <div class="text-6xl mb-4">🎨</div>
                  <h4 class="text-lg font-semibold text-white mb-2">Character Preview</h4>
                  <p class="text-gray-400">
                    Configure your character settings and click "Generate Character" to create your perfect {characterSettings.persona} character.
                  </p>
                </div>
              {/if}

              <!-- Error Display -->
              {#if generationError}
                <div class="error-message bg-red-500/20 border border-red-500/30 text-red-400 p-4 rounded-lg mt-4">
                  <div class="flex items-center gap-2">
                    <span class="text-red-400">⚠️</span>
                    <span class="text-sm">{generationError}</span>
                  </div>
                </div>
              {/if}
            </div>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .character-generator {
    font-family: inherit;
  }
  
  .generator-toggle-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .generator-modal {
    animation: slideIn 0.3s ease-out;
  }
  
  .option-btn {
    position: relative;
    overflow: hidden;
  }
  
  .option-btn:hover {
    transform: translateY(-1px);
  }
  
  .option-btn:active {
    transform: translateY(0);
  }
  
  .progress-fill {
    transition: width 0.3s ease-out;
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: scale(0.95) translateY(-10px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }
</style> 