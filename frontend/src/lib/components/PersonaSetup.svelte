<!-- PersonaSetup.svelte -->
<script lang="ts">
  import { personaActions, personaConfig, type PersonaCustomization } from '$lib/stores/personaStore';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let name = '';
  let customization: PersonaCustomization = {
    hair_color: '',
    eye_color: '',
    voice_type: ''
  };

  const hairColors = [
    { id: 'warm_brown', label: 'Warm Brown', value: '#8B4513' },
    { id: 'rich_black', label: 'Rich Black', value: '#090909' },
    { id: 'golden_blonde', label: 'Golden Blonde', value: '#FFD700' },
    { id: 'auburn_red', label: 'Auburn Red', value: '#A52A2A' }
  ];

  const eyeColors = [
    { id: 'deep_green', label: 'Deep Green', value: '#006400' },
    { id: 'deep_blue', label: 'Deep Blue', value: '#00008B' },
    { id: 'warm_brown', label: 'Warm Brown', value: '#8B4513' },
    { id: 'hazel', label: 'Hazel', value: '#8E7618' }
  ];

  const voiceTypes = [
    { id: 'warm', label: 'Warm & Gentle' },
    { id: 'clear', label: 'Clear & Bright' },
    { id: 'soft', label: 'Soft & Soothing' },
    { id: 'melodic', label: 'Melodic & Sweet' }
  ];

  function handleSubmit() {
    if (!name) return;

    personaActions.setName(name);
    personaActions.updateCustomization(customization);
    dispatch('complete');
  }
</script>

<div class="setup-container bg-gray-900 p-8 rounded-lg max-w-2xl mx-auto">
  <h2 class="text-2xl font-bold text-white mb-6">Customize Your AI Companion</h2>

  <form on:submit|preventDefault={handleSubmit} class="space-y-8">
    <!-- Name Input -->
    <div class="space-y-2">
      <label for="name" class="block text-sm font-medium text-white">
        What would you like to name your companion?
      </label>
      <input
        type="text"
        id="name"
        bind:value={name}
        class="w-full px-4 py-2 bg-gray-800 text-white rounded-md border border-gray-700 focus:border-pink-500 focus:ring-1 focus:ring-pink-500"
        placeholder="Enter a name"
        required
      />
    </div>

    <!-- Appearance -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-white">Appearance</h3>

      <!-- Hair Color -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-white">Hair Color</label>
        <div class="grid grid-cols-2 gap-2">
          {#each hairColors as color}
            <button
              type="button"
              class="flex items-center p-3 rounded-md border transition-colors"
              class:border-pink-500={customization.hair_color === color.id}
              class:border-gray-700={customization.hair_color !== color.id}
              class:bg-gray-800={customization.hair_color !== color.id}
              class:bg-gray-700={customization.hair_color === color.id}
              on:click={() => customization.hair_color = color.id}
            >
              <div 
                class="w-4 h-4 rounded-full mr-2" 
                style="background-color: {color.value};"
              />
              <span class="text-sm text-white">{color.label}</span>
            </button>
          {/each}
        </div>
      </div>

      <!-- Eye Color -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-white">Eye Color</label>
        <div class="grid grid-cols-2 gap-2">
          {#each eyeColors as color}
            <button
              type="button"
              class="flex items-center p-3 rounded-md border transition-colors"
              class:border-pink-500={customization.eye_color === color.id}
              class:border-gray-700={customization.eye_color !== color.id}
              class:bg-gray-800={customization.eye_color !== color.id}
              class:bg-gray-700={customization.eye_color === color.id}
              on:click={() => customization.eye_color = color.id}
            >
              <div 
                class="w-4 h-4 rounded-full mr-2" 
                style="background-color: {color.value};"
              />
              <span class="text-sm text-white">{color.label}</span>
            </button>
          {/each}
        </div>
      </div>
    </div>

    <!-- Voice -->
    <div class="space-y-2">
      <label class="block text-sm font-medium text-white">Voice Type</label>
      <div class="grid grid-cols-2 gap-2">
        {#each voiceTypes as voice}
          <button
            type="button"
            class="p-3 rounded-md border transition-colors text-left"
            class:border-pink-500={customization.voice_type === voice.id}
            class:border-gray-700={customization.voice_type !== voice.id}
            class:bg-gray-800={customization.voice_type !== voice.id}
            class:bg-gray-700={customization.voice_type === voice.id}
            on:click={() => customization.voice_type = voice.id}
          >
            <span class="text-sm text-white">{voice.label}</span>
          </button>
        {/each}
      </div>
    </div>

    <!-- Submit Button -->
    <button
      type="submit"
      class="w-full py-3 px-4 bg-pink-600 hover:bg-pink-700 text-white font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      disabled={!name || !customization.hair_color || !customization.eye_color || !customization.voice_type}
    >
      Create Your Companion
    </button>
  </form>
</div>

<style>
  .setup-container {
    min-height: 600px;
  }

  button {
    outline: none;
  }

  button:focus-visible {
    ring: 2px;
    ring-offset: 2px;
    ring-pink-500;
  }
</style>
