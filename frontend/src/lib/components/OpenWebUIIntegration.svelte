<!-- OpenWebUIIntegration.svelte -->
<!-- Final Integration Component for OpenWebUI Persona Toggle Patch -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { getContext } from 'svelte';
  import PersonaSystem from './PersonaSystem.svelte';
  import { 
    currentPersona, 
    currentPersonaConfig, 
    isSwitchingPersona,
    personaActions 
  } from '$lib/stores/personaStore.js';
  import { 
    currentUIMode, 
    isCompanionMode, 
    uiModeActions 
  } from '$lib/stores/uiModeStore.js';

  // OpenWebUI context
  const i18n = getContext('i18n');
  const page = getContext('page');
  const showSidebar = getContext('showSidebar');

  // Component state
  let isInitialized = false;
  let integrationError = null;
  let showPersonaOverlay = false;

  // Integration with OpenWebUI's existing stores
  let originalShowSidebar = false;
  let originalPageTitle = '';

  // Initialize integration
  async function initializeIntegration() {
    try {
      // Set default persona if none selected
      if (!$currentPersona) {
        await personaActions.switchPersona('mia');
      }
      
      // Set default UI mode if none selected
      if (!$currentUIMode) {
        await uiModeActions.switchMode('companion');
      }
      
      // Store original OpenWebUI state
      originalShowSidebar = $showSidebar;
      originalPageTitle = document.title;
      
      // Update page metadata
      updatePageMetadata();
      
      isInitialized = true;
      console.log('[OpenWebUI Integration] Initialized successfully');
      
    } catch (error) {
      integrationError = error.message;
      console.error('[OpenWebUI Integration] Initialization failed:', error);
    }
  }

  // Update page metadata based on current persona
  function updatePageMetadata() {
    if ($currentPersonaConfig) {
      const pageTitle = `${$currentPersonaConfig.name} - EmotionalAI`;
      const pageDescription = $currentPersonaConfig.description;
      
      // Update document title
      document.title = pageTitle;
      
      // Update meta description
      const metaDescription = document.querySelector('meta[name="description"]');
      if (metaDescription) {
        metaDescription.setAttribute('content', pageDescription);
      }
      
      // Update OpenGraph tags
      updateOpenGraphTags(pageTitle, pageDescription);
    }
  }

  // Update OpenGraph tags for social sharing
  function updateOpenGraphTags(title, description) {
    const ogTitle = document.querySelector('meta[property="og:title"]');
    const ogDescription = document.querySelector('meta[property="og:description"]');
    const ogImage = document.querySelector('meta[property="og:image"]');
    
    if (ogTitle) ogTitle.setAttribute('content', title);
    if (ogDescription) ogDescription.setAttribute('content', description);
    if (ogImage) {
      // Set persona-specific image
      const personaImage = $currentPersonaConfig?.characteristics?.avatar_url || '/static/persona-default.jpg';
      ogImage.setAttribute('content', personaImage);
    }
  }

  // Handle persona switching
  async function handlePersonaSwitch(newPersona) {
    try {
      await personaActions.switchPersona(newPersona);
      updatePageMetadata();
      
      // Show success notification
      showNotification(`Switched to ${$currentPersonaConfig?.name}`, 'success');
      
    } catch (error) {
      showNotification('Failed to switch persona', 'error');
      console.error('Persona switch error:', error);
    }
  }

  // Handle UI mode switching
  async function handleUIModeSwitch(newMode) {
    try {
      await uiModeActions.switchMode(newMode);
      
      // Update interface based on mode
      if (newMode === 'companion') {
        showPersonaOverlay = true;
        document.body.classList.add('companion-mode');
        document.body.classList.remove('dev-mode');
      } else {
        showPersonaOverlay = false;
        document.body.classList.add('dev-mode');
        document.body.classList.remove('companion-mode');
      }
      
      showNotification(`Switched to ${newMode} mode`, 'success');
      
    } catch (error) {
      showNotification('Failed to switch UI mode', 'error');
      console.error('UI mode switch error:', error);
    }
  }

  // Show notification (integrate with OpenWebUI's notification system)
  function showNotification(message, type = 'info') {
    // Use OpenWebUI's existing notification system if available
    if (typeof window !== 'undefined' && window.showNotification) {
      window.showNotification(message, type);
    } else {
      // Fallback to console
      console.log(`[${type.toUpperCase()}] ${message}`);
    }
  }

  // Handle keyboard shortcuts
  function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + 1-4 for persona switching
    if ((event.ctrlKey || event.metaKey) && event.key >= '1' && event.key <= '4') {
      event.preventDefault();
      const personas = ['mia', 'solene', 'lyra', 'doc'];
      const personaIndex = parseInt(event.key) - 1;
      if (personaIndex < personas.length) {
        handlePersonaSwitch(personas[personaIndex]);
      }
    }
    
    // Ctrl/Cmd + M for mode switching
    if ((event.ctrlKey || event.metaKey) && event.key === 'm') {
      event.preventDefault();
      const newMode = $currentUIMode === 'companion' ? 'dev' : 'companion';
      handleUIModeSwitch(newMode);
    }
  }

  // Cleanup function
  function cleanup() {
    // Restore original OpenWebUI state
    if (originalPageTitle) {
      document.title = originalPageTitle;
    }
    
    // Remove mode classes
    document.body.classList.remove('companion-mode', 'dev-mode');
    
    // Remove event listeners
    document.removeEventListener('keydown', handleKeyboardShortcuts);
  }

  // Reactive statements
  $: if ($currentPersonaConfig && isInitialized) {
    updatePageMetadata();
  }

  $: if ($currentUIMode && isInitialized) {
    // Update interface based on current mode
    if ($currentUIMode === 'companion') {
      document.body.classList.add('companion-mode');
      document.body.classList.remove('dev-mode');
    } else {
      document.body.classList.add('dev-mode');
      document.body.classList.remove('companion-mode');
    }
  }

  onMount(() => {
    // Initialize integration
    initializeIntegration();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Add CSS for mode-specific styling
    addModeStyles();
  });

  onDestroy(() => {
    cleanup();
  });

  // Add CSS styles for companion/dev modes
  function addModeStyles() {
    const styleId = 'emotionalai-mode-styles';
    if (!document.getElementById(styleId)) {
      const style = document.createElement('style');
      style.id = styleId;
      style.textContent = `
        /* Companion Mode Styles */
        .companion-mode {
          --primary-color: #FF6B9D;
          --secondary-color: #FFB3D1;
          --background-color: #FFF5F7;
          --text-color: #2D3748;
        }
        
        .companion-mode .persona-avatar {
          border: 2px solid var(--primary-color);
          box-shadow: 0 0 20px rgba(255, 107, 157, 0.3);
        }
        
        .companion-mode .chat-message {
          background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
          color: white;
        }
        
        /* Dev Mode Styles */
        .dev-mode {
          --primary-color: #3B82F6;
          --secondary-color: #93C5FD;
          --background-color: #F8FAFC;
          --text-color: #1F2937;
        }
        
        .dev-mode .persona-avatar {
          border: 2px solid var(--primary-color);
          box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
        }
        
        .dev-mode .chat-message {
          background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
          color: white;
        }
        
        /* Persona Overlay */
        .persona-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
          backdrop-filter: blur(10px);
        }
        
        .persona-overlay-content {
          background: white;
          border-radius: 20px;
          padding: 2rem;
          max-width: 90vw;
          max-height: 90vh;
          overflow: auto;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
          .persona-overlay-content {
            margin: 1rem;
            padding: 1rem;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }
</script>

<!-- Main Integration Component -->
<div class="openwebui-integration">
  <!-- Error Display -->
  {#if integrationError}
    <div class="integration-error">
      <div class="error-message">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{integrationError}</span>
        <button class="retry-button" on:click={initializeIntegration}>
          Retry
        </button>
      </div>
    </div>
  {/if}

  <!-- Loading State -->
  {#if !isInitialized && !integrationError}
    <div class="integration-loading">
      <div class="loading-spinner"></div>
      <span class="loading-text">Initializing EmotionalAI...</span>
    </div>
  {/if}

  <!-- Main Persona System -->
  {#if isInitialized}
    <PersonaSystem />
  {/if}

  <!-- Persona Overlay for Companion Mode -->
  {#if showPersonaOverlay && $isCompanionMode}
    <div class="persona-overlay" on:click={() => showPersonaOverlay = false}>
      <div class="persona-overlay-content" on:click|stopPropagation>
        <PersonaSystem />
      </div>
    </div>
  {/if}
</div>

<style>
  .openwebui-integration {
    width: 100%;
    height: 100%;
  }

  .integration-error {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #FEE2E2;
    border: 1px solid #FCA5A5;
    border-radius: 8px;
    padding: 1rem;
    z-index: 1001;
    max-width: 400px;
  }

  .error-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .error-icon {
    font-size: 1.2rem;
  }

  .error-text {
    color: #DC2626;
    font-size: 0.9rem;
  }

  .retry-button {
    background: #DC2626;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
    cursor: pointer;
    margin-left: auto;
  }

  .retry-button:hover {
    background: #B91C1C;
  }

  .integration-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    gap: 1rem;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #E5E7EB;
    border-top: 4px solid #FF6B9D;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .loading-text {
    color: #6B7280;
    font-size: 1rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .integration-error {
      top: 10px;
      right: 10px;
      left: 10px;
      max-width: none;
    }
  }
</style> 