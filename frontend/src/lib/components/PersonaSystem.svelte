<!-- PersonaSystem.svelte -->
<!-- Main Integration Component for 4-Persona EmotionalAI System -->

<script>
  import { onMount } from 'svelte';
  import PersonaSelector from './PersonaSelector.svelte';
  import PersonaChatInterface from './PersonaChatInterface.svelte';
  import CharacterGenerator from './CharacterGenerator.svelte';
  import { 
    currentPersona, 
    currentPersonaConfig, 
    isSwitchingPersona 
  } from '$lib/stores/personaStore.js';
  import { 
    currentUIMode, 
    isCompanionMode, 
    isDevMode 
  } from '$lib/stores/uiModeStore.js';

  // Component state
  let showSidebar = false;
  let sidebarWidth = 320;

  // Toggle sidebar visibility
  function toggleSidebar() {
    showSidebar = !showSidebar;
  }

  // Handle window resize
  function handleResize() {
    if (window.innerWidth < 768) {
      showSidebar = false;
    }
  }

  onMount(() => {
    // Add resize listener
    window.addEventListener('resize', handleResize);
    
    // Initialize sidebar state based on screen size
    handleResize();
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  });
</script>

<div class="persona-system h-full flex">
  <!-- Sidebar -->
  <div 
    class="persona-sidebar bg-gray-900 border-r border-gray-700 transition-all duration-300 ease-in-out {showSidebar ? 'w-80' : 'w-0'} overflow-hidden"
    style="min-width: {showSidebar ? sidebarWidth + 'px' : '0px'}"
  >
    <div class="sidebar-content h-full flex flex-col p-4">
      <!-- Sidebar Header -->
      <div class="sidebar-header flex items-center justify-between mb-6">
        <div class="flex items-center gap-2">
          <span class="text-2xl">💕</span>
          <h1 class="text-lg font-semibold text-white">EmotionalAI</h1>
        </div>
        
        <button
          class="close-sidebar-btn p-2 text-gray-400 hover:text-white transition-colors duration-200"
          on:click={toggleSidebar}
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Persona Selector -->
      <div class="persona-selector-section mb-6">
        <PersonaSelector />
      </div>

      <!-- Character Generator (Companion Mode Only) -->
      {#if $isCompanionMode}
        <div class="character-generator-section mb-6">
          <CharacterGenerator />
        </div>
      {/if}

      <!-- Mode Information -->
      <div class="mode-info bg-gray-800/50 rounded-lg p-4 mb-6">
        <h3 class="text-sm font-medium text-white mb-2">Current Mode</h3>
        <div class="flex items-center gap-2 mb-2">
          <span class="text-lg">
            {$currentUIMode === 'companion' ? '💕' : '💻'}
          </span>
          <span class="text-sm font-medium text-white">
            {$currentUIMode === 'companion' ? 'Companion Mode' : 'Dev Mode'}
          </span>
        </div>
        <p class="text-xs text-gray-400">
          {#if $isCompanionMode}
            Romantic AI companion experience with avatars and emotional intelligence
          {:else}
            Professional development interface for technical discussions
          {/if}
        </p>
      </div>

      <!-- Persona Status -->
      {#if $currentPersonaConfig}
        <div class="persona-status bg-gray-800/50 rounded-lg p-4 mb-6">
          <h3 class="text-sm font-medium text-white mb-2">Active Persona</h3>
          <div class="flex items-center gap-3 mb-2">
            <span class="text-2xl">{$currentPersonaConfig.icon}</span>
            <div>
              <div class="text-sm font-medium text-white">{$currentPersonaConfig.name}</div>
              <div class="text-xs text-gray-400">{$currentPersonaConfig.type}</div>
            </div>
          </div>
          
          <div class="space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-400">Model</span>
              <span class="text-xs text-white font-medium">{$currentPersonaConfig.llm_model}</span>
            </div>
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

      <!-- Quick Actions -->
      <div class="quick-actions space-y-2">
        <button
          class="quick-action-btn w-full flex items-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors duration-200"
          on:click={() => window.open('/api/docs', '_blank')}
        >
          <span class="text-lg">📚</span>
          <span class="text-sm">API Documentation</span>
        </button>
        
        <button
          class="quick-action-btn w-full flex items-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors duration-200"
          on:click={() => window.open('/settings', '_blank')}
        >
          <span class="text-lg">⚙️</span>
          <span class="text-sm">Settings</span>
        </button>
      </div>

      <!-- Spacer -->
      <div class="flex-1"></div>

      <!-- Footer -->
      <div class="sidebar-footer text-center py-4 border-t border-gray-700">
        <p class="text-xs text-gray-500">
          EmotionalAI v1.0 • 4-Persona System
        </p>
        <p class="text-xs text-gray-600 mt-1">
          Powered by OpenWebUI + SvelteKit
        </p>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div class="main-content flex-1 flex flex-col">
    <!-- Top Bar -->
    <div class="top-bar bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <!-- Sidebar Toggle -->
        <button
          class="sidebar-toggle-btn p-2 text-gray-400 hover:text-white transition-colors duration-200"
          on:click={toggleSidebar}
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>

        <!-- Current Persona Display -->
        <div class="current-persona-display flex items-center gap-3">
          {#if $isSwitchingPersona}
            <div class="w-8 h-8 border-2 border-gray-400 border-t-white rounded-full animate-spin"></div>
          {:else}
            <span class="text-2xl">{$currentPersonaConfig?.icon || '👤'}</span>
          {/if}
          
          <div>
            <h2 class="text-lg font-semibold text-white">{$currentPersonaConfig?.name || 'Unknown'}</h2>
            <p class="text-sm text-gray-400">{$currentPersonaConfig?.description || 'AI Companion'}</p>
          </div>
        </div>
      </div>

      <!-- Mode Indicator -->
      <div class="mode-indicator flex items-center gap-2">
        <span class="text-lg">
          {$currentUIMode === 'companion' ? '💕' : '💻'}
        </span>
        <span class="text-sm font-medium text-white">
          {$currentUIMode === 'companion' ? 'Companion' : 'Dev'}
        </span>
      </div>
    </div>

    <!-- Chat Interface -->
    <div class="chat-container flex-1">
      <PersonaChatInterface />
    </div>
  </div>
</div>

<!-- Mobile Overlay -->
{#if showSidebar && window.innerWidth < 768}
  <div 
    class="mobile-overlay fixed inset-0 bg-black/50 z-40"
    on:click={toggleSidebar}
  ></div>
{/if}

<style>
  .persona-system {
    font-family: inherit;
  }
  
  .persona-sidebar {
    z-index: 50;
  }
  
  .sidebar-content {
    width: 320px;
  }
  
  .quick-action-btn {
    position: relative;
    overflow: hidden;
  }
  
  .quick-action-btn:hover {
    transform: translateY(-1px);
  }
  
  .quick-action-btn:active {
    transform: translateY(0);
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    .persona-sidebar {
      position: fixed;
      left: 0;
      top: 0;
      height: 100vh;
      z-index: 50;
    }
    
    .sidebar-content {
      width: 100%;
    }
  }
  
  /* Smooth transitions */
  .persona-sidebar {
    transition: width 0.3s ease-in-out, min-width 0.3s ease-in-out;
  }
  
  /* Animation for sidebar content */
  .sidebar-content {
    animation: slideIn 0.3s ease-out;
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
</style> 