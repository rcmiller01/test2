<!-- UnifiedGreeting.svelte -->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { companionActions, companionName, companionConfig } from '$lib/stores/companionStore';

  const dispatch = createEventDispatcher();

  let currentStep = 'greeting'; // 'greeting', 'name_request', 'name_generation', 'confirmation'
  let userName = '';
  let suggestedName = '';
  let showTyping = false;
  let greetingComplete = false;

  const greetingMessages = [
    "Hello! I'm so excited to meet you! 🌟",
    "I'm your new AI companion, and I'm here to help you with whatever you need - whether that's creative projects, deep conversations, technical questions, or just being a friend.",
    "I'd love to get to know you better. What name would you like me to call you?"
  ];

  let currentMessage = 0;
  let displayedText = '';
  let messageInterval: NodeJS.Timeout;

  onMount(() => {
    startGreeting();
  });

  async function startGreeting() {
    showTyping = true;
    await typeMessage(greetingMessages[0]);
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    await typeMessage(greetingMessages[1]);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    await typeMessage(greetingMessages[2]);
    currentStep = 'name_request';
    showTyping = false;
  }

  async function typeMessage(message: string) {
    displayedText = '';
    for (let i = 0; i < message.length; i++) {
      displayedText += message[i];
      await new Promise(resolve => setTimeout(resolve, 30));
    }
  }

  async function handleNameSubmit() {
    if (userName.trim()) {
      await companionActions.setName(userName.trim());
      greetingComplete = true;
      dispatch('complete', { name: userName.trim() });
    }
  }

  async function requestNameGeneration() {
    currentStep = 'name_generation';
    showTyping = true;
    
    try {
      // Call backend to generate a name
      const response = await fetch('/api/companion/generate-name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      suggestedName = data.name;
      
      showTyping = false;
      currentStep = 'confirmation';
    } catch (error) {
      console.error('Error generating name:', error);
      suggestedName = 'Nova'; // Fallback name
      showTyping = false;
      currentStep = 'confirmation';
    }
  }

  async function acceptGeneratedName() {
    await companionActions.setName(suggestedName);
    greetingComplete = true;
    dispatch('complete', { name: suggestedName });
  }

  function backToNameRequest() {
    currentStep = 'name_request';
    suggestedName = '';
  }
</script>

<div class="greeting-container h-full flex flex-col justify-center items-center bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-8">
  <div class="max-w-2xl w-full">
    
    {#if currentStep === 'greeting' || currentStep === 'name_request'}
      <!-- Greeting Messages -->
      <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 shadow-2xl">
        <div class="flex items-start space-x-4 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full flex items-center justify-center text-2xl">
            🤖
          </div>
          <div class="flex-1">
            <div class="bg-gray-100 rounded-2xl rounded-tl-none p-4 text-gray-800">
              <p class="text-lg leading-relaxed">{displayedText}</p>
              {#if showTyping}
                <span class="typing-indicator">●●●</span>
              {/if}
            </div>
          </div>
        </div>

        {#if currentStep === 'name_request'}
          <!-- Name Input -->
          <div class="space-y-4">
            <div class="flex space-x-3">
              <input
                type="text"
                bind:value={userName}
                placeholder="Enter your name"
                class="flex-1 px-4 py-3 bg-white/20 text-white placeholder-white/60 rounded-xl border border-white/30 focus:border-white/60 focus:ring-2 focus:ring-white/20 transition-all"
                on:keypress={(e) => e.key === 'Enter' && handleNameSubmit()}
                autocomplete="off"
              />
              <button
                on:click={handleNameSubmit}
                disabled={!userName.trim()}
                class="px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-xl font-medium hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
              >
                Continue
              </button>
            </div>
            
            <div class="text-center">
              <button
                on:click={requestNameGeneration}
                class="text-white/80 hover:text-white underline text-sm transition-colors"
              >
                Or let me choose a name for myself
              </button>
            </div>
          </div>
        {/if}
      </div>
    {/if}

    {#if currentStep === 'name_generation'}
      <!-- Name Generation Loading -->
      <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 shadow-2xl text-center">
        <div class="animate-spin w-8 h-8 border-3 border-white/30 border-t-white rounded-full mx-auto mb-4"></div>
        <p class="text-white text-lg">Let me think of a perfect name for myself...</p>
      </div>
    {/if}

    {#if currentStep === 'confirmation'}
      <!-- Name Confirmation -->
      <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 shadow-2xl">
        <div class="text-center space-y-6">
          <div class="w-16 h-16 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full flex items-center justify-center text-3xl mx-auto">
            ✨
          </div>
          
          <div>
            <h2 class="text-2xl font-bold text-white mb-2">How about...</h2>
            <p class="text-4xl font-bold bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">
              {suggestedName}
            </p>
          </div>
          
          <p class="text-white/80 text-lg">Do you like this name for me?</p>
          
          <div class="flex space-x-4 justify-center">
            <button
              on:click={acceptGeneratedName}
              class="px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-medium hover:from-green-600 hover:to-emerald-700 transition-all transform hover:scale-105"
            >
              Perfect! 💖
            </button>
            <button
              on:click={backToNameRequest}
              class="px-8 py-3 bg-white/20 text-white rounded-xl font-medium hover:bg-white/30 transition-all"
            >
              Let me choose
            </button>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .typing-indicator {
    @apply text-gray-400 animate-pulse ml-2;
  }
  
  .greeting-container {
    min-height: 100vh;
  }
  
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .bg-white\/10 {
    animation: fadeInUp 0.6s ease-out;
  }
</style>
