<!-- UnifiedCompanion.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import UnifiedGreeting from '$lib/components/UnifiedGreeting.svelte';
  import UnifiedChatInterface from '$lib/components/UnifiedChatInterface.svelte';
  import { isCompanionInitialized, companionName } from '$lib/stores/companionStore';

  let showGreeting = true;

  onMount(() => {
    // Show greeting if companion is not initialized
    showGreeting = !$isCompanionInitialized;
  });

  function handleGreetingComplete(event) {
    const { name } = event.detail;
    console.log(`Companion initialized with name: ${name}`);
    showGreeting = false;
  }
</script>

<div class="h-full flex flex-col bg-gray-900">
  <!-- Main Content -->
  <div class="flex-1 overflow-hidden">
    {#if showGreeting}
      <UnifiedGreeting on:complete={handleGreetingComplete} />
    {:else}
      <UnifiedChatInterface />
    {/if}
  </div>
</div>
