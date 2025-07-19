<!-- persona/+page.svelte -->
<!-- Persona System Route for OpenWebUI -->

<script>
  import { onMount } from 'svelte';
  import PersonaSystem from '$lib/components/PersonaSystem.svelte';
  import { 
    currentPersona, 
    currentPersonaConfig,
    personaActions 
  } from '$lib/stores/personaStore.js';
  import { 
    currentUIMode, 
    uiModeActions 
  } from '$lib/stores/uiModeStore.js';

  // Page metadata
  $: pageTitle = $currentPersonaConfig?.name || 'EmotionalAI';
  $: pageDescription = $currentPersonaConfig?.description || 'AI Companion System';

  // Update page title and meta
  $: if (typeof document !== 'undefined') {
    document.title = `${pageTitle} - EmotionalAI`;
    
    // Update meta description
    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute('content', pageDescription);
    }
  }

  onMount(() => {
    // Initialize persona system
    console.log('Persona System initialized');
    
    // Set default persona if none selected
    if (!$currentPersona) {
      personaActions.switchPersona('mia');
    }
    
    // Set default UI mode if none selected
    if (!$currentUIMode) {
      uiModeActions.switchMode('companion');
    }
  });
</script>

<svelte:head>
  <title>{pageTitle} - EmotionalAI</title>
  <meta name="description" content={pageDescription} />
  <meta name="keywords" content="AI companion, emotional AI, persona system, romantic AI" />
  
  <!-- Open Graph Meta Tags -->
  <meta property="og:title" content="{pageTitle} - EmotionalAI" />
  <meta property="og:description" content={pageDescription} />
  <meta property="og:type" content="website" />
  <meta property="og:image" content="/static/og-image.jpg" />
  
  <!-- Twitter Card Meta Tags -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{pageTitle} - EmotionalAI" />
  <meta name="twitter:description" content={pageDescription} />
  <meta name="twitter:image" content="/static/og-image.jpg" />
</svelte:head>

<!-- Persona System Container -->
<div class="persona-page h-full w-full">
  <PersonaSystem />
</div>

<style>
  .persona-page {
    font-family: inherit;
  }
</style> 