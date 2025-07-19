<!-- PersonaSelector.svelte -->
<!-- Persona Selection Component for 4-Persona EmotionalAI System -->

<script>
  import { onMount } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig, 
    isSwitchingPersona, 
    AVAILABLE_PERSONAS,
    personaActions 
  } from '$lib/stores/personaStore.js';
  import { 
    currentUIMode, 
    isCompanionMode, 
    uiModeActions 
  } from '$lib/stores/uiModeStore.js';

  // Component state
  let showPersonaMenu = false;
  let selectedPersona = null;

  // Initialize selected persona
  $: selectedPersona = $currentPersona;

  // Handle persona selection
  async function selectPersona(personaId) {
    if (personaId === $currentPersona) return;
    
    try {
      await personaActions.switchPersona(personaId);
      showPersonaMenu = false;
    } catch (error) {
      console.error('Failed to switch persona:', error);
    }
  }

  // Toggle persona menu
  function togglePersonaMenu() {
    showPersonaMenu = !showPersonaMenu;
  }

  // Close menu when clicking outside
  function handleClickOutside(event) {
    if (!event.target.closest('.persona-selector')) {
      showPersonaMenu = false;
    }
  }

  // Handle UI mode toggle
  async function toggleUIMode() {
    try {
      await uiModeActions.toggleMode();
    } catch (error) {
      console.error('Failed to toggle UI mode:', error);
    }
  }

  onMount(() => {
    // Add click outside listener
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
</script>

<div class="persona-selector relative">
  <!-- Current Persona Display -->
  <button
    class="current-persona-btn flex items-center gap-2 px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors duration-200 border border-white/20"
    on:click={togglePersonaMenu}
    disabled={$isSwitchingPersona}
  >
    {#if $isSwitchingPersona}
      <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
    {:else}
      <span class="text-2xl">{$currentPersonaConfig?.icon || '👤'}</span>
    {/if}
    
    <div class="flex flex-col items-start">
      <span class="text-sm font-medium text-white">
        {$currentPersonaConfig?.name || 'Unknown'}
      </span>
      <span class="text-xs text-white/70">
        {$currentPersonaConfig?.type || 'Unknown Type'}
      </span>
    </div>
    
    <svg class="w-4 h-4 text-white/70 transition-transform duration-200 {showPersonaMenu ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
    </svg>
  </button>

  <!-- Persona Selection Menu -->
  {#if showPersonaMenu}
    <div class="persona-menu absolute top-full left-0 mt-2 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50">
      <div class="p-4">
        <h3 class="text-sm font-medium text-white mb-3">Choose Your Companion</h3>
        
        <div class="space-y-2">
          {#each Object.values(AVAILABLE_PERSONAS) as persona}
            <button
              class="persona-option w-full flex items-center gap-3 p-3 rounded-lg hover:bg-gray-700 transition-colors duration-200 {persona.id === $currentPersona ? 'bg-gray-700 border border-gray-600' : ''}"
              on:click={() => selectPersona(persona.id)}
            >
              <div class="flex-shrink-0">
                <span class="text-2xl">{persona.icon}</span>
              </div>
              
              <div class="flex-1 text-left">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-white">{persona.name}</span>
                  {#if persona.id === $currentPersona}
                    <span class="text-xs bg-green-500 text-white px-2 py-1 rounded-full">Active</span>
                  {/if}
                </div>
                <p class="text-xs text-gray-400 mt-1">{persona.description}</p>
                <div class="flex items-center gap-2 mt-2">
                  <span class="text-xs text-gray-500">Model: {persona.llm_model}</span>
                  <span class="text-xs text-gray-500">•</span>
                  <span class="text-xs text-gray-500">{persona.type}</span>
                </div>
              </div>
            </button>
          {/each}
        </div>
      </div>
    </div>
  {/if}

  <!-- UI Mode Toggle -->
  <div class="ui-mode-toggle mt-3">
    <button
      class="mode-toggle-btn w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors duration-200 border border-white/20"
      on:click={toggleUIMode}
    >
      <span class="text-lg">
        {$currentUIMode === 'companion' ? '💕' : '💻'}
      </span>
      <span class="text-sm font-medium text-white">
        {$currentUIMode === 'companion' ? 'Companion Mode' : 'Dev Mode'}
      </span>
      <svg class="w-4 h-4 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
      </svg>
    </button>
  </div>

  <!-- Persona Status Indicator -->
  {#if $currentPersonaConfig}
    <div class="persona-status mt-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full" style="background-color: {$currentPersonaConfig.color}"></div>
          <span class="text-xs text-gray-400">Status</span>
        </div>
        <span class="text-xs text-green-400">Online</span>
      </div>
      
      <div class="mt-2 space-y-1">
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-400">Avatar</span>
          <span class="text-xs {#if $currentPersonaConfig.avatar_enabled && $isCompanionMode}text-green-400{:else}text-gray-500{/if}">
            {#if $currentPersonaConfig.avatar_enabled && $isCompanionMode}Enabled{:else}Disabled{/if}
          </span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-400">Emotional Hooks</span>
          <span class="text-xs {#if $currentPersonaConfig.emotional_hooks && $isCompanionMode}text-green-400{:else}text-gray-500{/if}">
            {#if $currentPersonaConfig.emotional_hooks && $isCompanionMode}Enabled{:else}Disabled{/if}
          </span>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .persona-selector {
    font-family: inherit;
  }
  
  .current-persona-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .persona-menu {
    backdrop-filter: blur(10px);
  }
  
  .persona-option {
    position: relative;
  }
  
  .persona-option:hover {
    transform: translateY(-1px);
  }
  
  .mode-toggle-btn:hover {
    transform: translateY(-1px);
  }
  
  /* Animation for menu appearance */
  .persona-menu {
    animation: slideDown 0.2s ease-out;
  }
  
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style> 