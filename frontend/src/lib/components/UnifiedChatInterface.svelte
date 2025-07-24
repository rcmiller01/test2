<!-- UnifiedChatInterface.svelte -->
<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { 
    companionName, 
    conversationHistory, 
    currentResponse, 
    isThinking,
    companionActions,
    currentInteractionMode,
    preferredResponseStyle,
    activeCreativeProject 
  } from '$lib/stores/companionStore';

  let messageInput = '';
  let chatContainer: HTMLElement;
  let isVoiceMode = false;
  let showSettings = false;

  // Auto-scroll to bottom when new messages arrive
  $: if ($conversationHistory && chatContainer) {
    tick().then(() => {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    });
  }

  async function sendMessage() {
    if (!messageInput.trim() || $isThinking) return;

    const message = messageInput.trim();
    messageInput = '';

    try {
      await companionActions.sendMessage(message);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  async function startCreativeProject(type: string) {
    try {
      await companionActions.startCreativeProject(type);
      messageInput = `I'd like to work on ${type}`;
      sendMessage();
    } catch (error) {
      console.error('Failed to start creative project:', error);
    }
  }

  function toggleVoiceMode() {
    isVoiceMode = !isVoiceMode;
    companionActions.updatePreferences({
      interactionMode: isVoiceMode ? 'voice' : 'text'
    });
  }

  function updateResponseStyle(style: string) {
    companionActions.updatePreferences({ responseStyle: style });
    showSettings = false;
  }

  onMount(() => {
    // Focus input on mount
    const input = document.querySelector('#message-input') as HTMLElement;
    if (input) input.focus();
  });
</script>

<div class="chat-interface h-full flex flex-col bg-gray-900">
  <!-- Header -->
  <div class="bg-gray-800 border-b border-gray-700 p-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center text-xl">
          🤖
        </div>
        <div>
          <h1 class="text-lg font-semibold text-white">{$companionName || 'Your AI Companion'}</h1>
          <p class="text-sm text-gray-400">
            {#if $isThinking}
              Thinking...
            {:else if $activeCreativeProject}
              Working on: {$activeCreativeProject.type}
            {:else}
              Ready to help
            {/if}
          </p>
        </div>
      </div>
      
      <div class="flex items-center space-x-2">
        <!-- Voice Mode Toggle -->
        <button
          on:click={toggleVoiceMode}
          class="p-2 rounded-lg transition-colors"
          class:bg-purple-600={$currentInteractionMode === 'voice'}
          class:bg-gray-700={$currentInteractionMode !== 'voice'}
          class:text-white={true}
          title="Toggle voice mode"
        >
          {$currentInteractionMode === 'voice' ? '🎤' : '💬'}
        </button>
        
        <!-- Settings -->
        <button
          on:click={() => showSettings = !showSettings}
          class="p-2 rounded-lg bg-gray-700 text-white hover:bg-gray-600 transition-colors"
          title="Settings"
        >
          ⚙️
        </button>
      </div>
    </div>

    <!-- Settings Panel -->
    {#if showSettings}
      <div class="mt-4 p-4 bg-gray-700 rounded-lg">
        <h3 class="text-white font-medium mb-3">Response Style</h3>
        <div class="grid grid-cols-2 gap-2">
          {#each ['balanced', 'creative', 'technical', 'emotional'] as style}
            <button
              on:click={() => updateResponseStyle(style)}
              class="px-3 py-2 rounded text-sm transition-colors"
              class:bg-purple-600={$preferredResponseStyle === style}
              class:bg-gray-600={$preferredResponseStyle !== style}
              class:text-white={true}
            >
              {style.charAt(0).toUpperCase() + style.slice(1)}
            </button>
          {/each}
        </div>
      </div>
    {/if}
  </div>

  <!-- Chat Messages -->
  <div class="flex-1 overflow-y-auto p-4 space-y-4" bind:this={chatContainer}>
    {#if $conversationHistory.length === 0}
      <!-- Welcome Message -->
      <div class="text-center py-8">
        <div class="w-16 h-16 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">
          ✨
        </div>
        <h2 class="text-xl font-semibold text-white mb-2">
          Hi! I'm {$companionName}
        </h2>
        <p class="text-gray-400 mb-6">
          I'm here to help you with whatever you need - creative projects, deep conversations, technical questions, or just being a friend.
        </p>
        
        <!-- Quick Actions -->
        <div class="grid grid-cols-2 gap-3 max-w-md mx-auto">
          <button
            on:click={() => startCreativeProject('music')}
            class="p-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
          >
            🎵 Create Music
          </button>
          <button
            on:click={() => startCreativeProject('art')}
            class="p-3 bg-pink-600 hover:bg-pink-700 text-white rounded-lg transition-colors"
          >
            🎨 Create Art
          </button>
          <button
            on:click={() => messageInput = "Can you help me with some code?"}
            class="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            💻 Code Help
          </button>
          <button
            on:click={() => messageInput = "I'd like to have a deep conversation"}
            class="p-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
          >
            💭 Deep Chat
          </button>
        </div>
      </div>
    {/if}

    {#each $conversationHistory as message (message.id)}
      <!-- User Message -->
      <div class="flex justify-end">
        <div class="max-w-xs lg:max-w-md bg-purple-600 text-white rounded-2xl rounded-br-none px-4 py-2">
          <p>{message.user_message}</p>
          <span class="text-xs opacity-75 block mt-1">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>

      <!-- Companion Response -->
      <div class="flex items-start space-x-3">
        <div class="w-8 h-8 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center text-sm flex-shrink-0">
          🤖
        </div>
        <div class="flex-1">
          <div class="bg-gray-700 text-white rounded-2xl rounded-tl-none px-4 py-3">
            <p class="whitespace-pre-wrap">{message.companion_response}</p>
            {#if message.emotion}
              <div class="flex items-center space-x-1 mt-2 text-xs opacity-75">
                <span>Emotion: {message.emotion}</span>
              </div>
            {/if}
            <span class="text-xs opacity-75 block mt-1">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>
    {/each}

    <!-- Thinking Indicator -->
    {#if $isThinking}
      <div class="flex items-start space-x-3">
        <div class="w-8 h-8 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center text-sm flex-shrink-0">
          🤖
        </div>
        <div class="bg-gray-700 text-white rounded-2xl rounded-tl-none px-4 py-3">
          <div class="flex items-center space-x-1">
            <span class="text-sm">Thinking</span>
            <div class="flex space-x-1">
              <div class="w-1 h-1 bg-white rounded-full animate-bounce"></div>
              <div class="w-1 h-1 bg-white rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-1 h-1 bg-white rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Message Input -->
  <div class="border-t border-gray-700 p-4">
    <div class="flex space-x-3">
      <textarea
        id="message-input"
        bind:value={messageInput}
        on:keypress={handleKeyPress}
        placeholder="Type your message..."
        class="flex-1 bg-gray-800 text-white placeholder-gray-400 rounded-xl px-4 py-3 border border-gray-600 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 resize-none"
        rows="1"
        disabled={$isThinking}
      />
      <button
        on:click={sendMessage}
        disabled={!messageInput.trim() || $isThinking}
        class="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl font-medium hover:from-purple-600 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
      >
        Send
      </button>
    </div>
  </div>
</div>

<style>
  .chat-interface {
    height: 100vh;
  }
  
  .animate-bounce {
    animation: bounce 1.4s infinite both;
  }
  
  @keyframes bounce {
    0%, 80%, 100% {
      transform: scale(0);
    }
    40% {
      transform: scale(1);
    }
  }
</style>
