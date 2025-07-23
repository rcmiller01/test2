<!-- PersonaSystem.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import PersonaSetup from './PersonaSetup.svelte';
  import PersonaChatInterface from './PersonaChatInterface.svelte';
  import { personaConfig, personaName, uiMode, type UIMode } from '$lib/stores/personaStore';

  let showSetup = false;

  onMount(() => {
    // Show setup if no name is set
    showSetup = !$personaConfig.name;
  });

  function handleSetupComplete() {
    showSetup = false;
  }

  function toggleMode() {
    uiMode.set($uiMode === 'companion' ? 'dev' : 'companion');
  }
</script>

<div class="h-full flex flex-col bg-gray-900">
  <!-- Mode Toggle -->
  <div class="flex justify-end p-4">
    <button
      on:click={toggleMode}
      class="flex items-center space-x-2 px-4 py-2 rounded-md transition-colors"
      class:bg-pink-600={$uiMode === 'companion'}
      class:bg-blue-600={$uiMode === 'dev'}
    >
      <span class="text-lg">
        {$uiMode === 'companion' ? '💕' : '💻'}
      </span>
      <span class="text-sm font-medium text-white">
        {$uiMode === 'companion' ? 'Companion' : 'Dev'} Mode
      </span>
    </button>
  </div>

  <!-- Main Content -->
  <div class="flex-1 overflow-hidden">
    {#if showSetup}
      <PersonaSetup on:complete={handleSetupComplete} />
    {:else}
      <PersonaChatInterface />
    {/if}
  </div>
</div>
