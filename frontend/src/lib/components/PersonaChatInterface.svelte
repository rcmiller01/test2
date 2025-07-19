<!-- PersonaChatInterface.svelte -->
<!-- Enhanced Chat Interface for 4-Persona EmotionalAI System -->

<script>
  import { onMount, onDestroy } from 'svelte';
  import { 
    currentPersona, 
    currentPersonaConfig, 
    personaResponse, 
    personaError, 
    personaChatHistory,
    personaActions 
  } from '$lib/stores/personaStore.js';
  import { 
    isCompanionMode, 
    currentFeatures 
  } from '$lib/stores/uiModeStore.js';

  // Component state
  let messageInput = '';
  let isSending = false;
  let chatContainer;
  let inputElement;

  // Reactive variables
  $: currentHistory = $personaChatHistory[$currentPersona] || [];
  $: personaConfig = $currentPersonaConfig;

  // Handle message submission
  async function handleSubmit(event) {
    event.preventDefault();
    
    if (!messageInput.trim() || isSending) return;
    
    const message = messageInput.trim();
    messageInput = '';
    isSending = true;
    
    try {
      // Analyze mood if emotional hooks are enabled
      let mood = null;
      if ($currentFeatures.emotional_hooks) {
        mood = await personaActions.analyzeMood(message);
      }
      
      // Send message to persona
      await personaActions.sendMessage(message, mood);
      
      // Scroll to bottom after response
      setTimeout(() => {
        scrollToBottom();
      }, 100);
      
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      isSending = false;
    }
  }

  // Scroll chat to bottom
  function scrollToBottom() {
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  // Handle key press in input
  function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(event);
    }
  }

  // Clear chat history
  function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
      personaActions.clearChatHistory();
    }
  }

  // Get persona gesture for mood
  async function getPersonaGesture(mood) {
    if ($currentFeatures.emotional_hooks) {
      return await personaActions.getPersonaGesture(mood);
    }
    return null;
  }

  // Auto-scroll on new messages
  $: if (currentHistory.length > 0) {
    setTimeout(scrollToBottom, 50);
  }

  onMount(() => {
    // Focus input on mount
    if (inputElement) {
      inputElement.focus();
    }
    
    // Scroll to bottom initially
    scrollToBottom();
  });

  onDestroy(() => {
    // Cleanup if needed
  });
</script>

<div class="persona-chat-interface h-full flex flex-col">
  <!-- Chat Header -->
  <div class="chat-header flex items-center justify-between p-4 border-b border-gray-700 bg-gray-800/50">
    <div class="flex items-center gap-3">
      <span class="text-2xl">{personaConfig?.icon || '👤'}</span>
      <div>
        <h2 class="text-lg font-semibold text-white">{personaConfig?.name || 'Unknown'}</h2>
        <p class="text-sm text-gray-400">{personaConfig?.description || 'AI Companion'}</p>
      </div>
    </div>
    
    <div class="flex items-center gap-2">
      <button
        class="clear-chat-btn px-3 py-1 text-xs bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-md transition-colors duration-200"
        on:click={clearChat}
        title="Clear chat history"
      >
        Clear Chat
      </button>
    </div>
  </div>

  <!-- Chat Messages -->
  <div 
    bind:this={chatContainer}
    class="chat-messages flex-1 overflow-y-auto p-4 space-y-4"
  >
    {#if currentHistory.length === 0}
      <!-- Welcome Message -->
      <div class="welcome-message text-center py-8">
        <div class="welcome-icon text-6xl mb-4">{personaConfig?.icon || '👤'}</div>
        <h3 class="text-xl font-semibold text-white mb-2">
          Welcome to {personaConfig?.name || 'Your AI Companion'}!
        </h3>
        <p class="text-gray-400 max-w-md mx-auto">
          {personaConfig?.description || 'Start a conversation to begin your journey together.'}
        </p>
        {#if $isCompanionMode && personaConfig?.emotional_hooks}
          <p class="text-sm text-gray-500 mt-2">
            💕 Emotional intelligence enabled • 🎭 Avatar animations available
          </p>
        {/if}
      </div>
    {:else}
      <!-- Chat Messages -->
      {#each currentHistory as message (message.id)}
        <div class="message-container {message.type === 'user' ? 'user-message' : 'persona-message'}">
          {#if message.type === 'user'}
            <!-- User Message -->
            <div class="user-message flex justify-end">
              <div class="max-w-xs lg:max-w-md bg-blue-600 text-white p-3 rounded-lg rounded-br-none">
                <p class="text-sm">{message.content}</p>
                <div class="flex items-center justify-between mt-2 text-xs text-blue-200">
                  <span>You</span>
                  <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            </div>
          {:else}
            <!-- Persona Message -->
            <div class="persona-message flex justify-start">
              <div class="flex items-start gap-3 max-w-xs lg:max-w-md">
                <div class="persona-avatar flex-shrink-0">
                  <span class="text-2xl">{personaConfig?.icon || '👤'}</span>
                </div>
                
                <div class="persona-content bg-gray-700 text-white p-3 rounded-lg rounded-bl-none">
                  <p class="text-sm">{message.content}</p>
                  
                  <div class="flex items-center justify-between mt-2 text-xs text-gray-400">
                    <div class="flex items-center gap-2">
                      <span>{personaConfig?.name || 'AI'}</span>
                      {#if message.mood}
                        <span class="px-2 py-1 bg-gray-600 rounded-full text-xs">
                          {message.mood}
                        </span>
                      {/if}
                    </div>
                    <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                  </div>
                  
                  {#if message.llm_model}
                    <div class="mt-1 text-xs text-gray-500">
                      Powered by {message.llm_model}
                    </div>
                  {/if}
                </div>
              </div>
            </div>
          {/if}
        </div>
      {/each}
    {/if}

    <!-- Loading Indicator -->
    {#if isSending}
      <div class="persona-message flex justify-start">
        <div class="flex items-start gap-3">
          <div class="persona-avatar flex-shrink-0">
            <span class="text-2xl">{personaConfig?.icon || '👤'}</span>
          </div>
          
          <div class="persona-content bg-gray-700 p-3 rounded-lg rounded-bl-none">
            <div class="flex items-center gap-2">
              <div class="typing-indicator flex gap-1">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
              <span class="text-xs text-gray-400">Thinking...</span>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Error Display -->
  {#if $personaError}
    <div class="error-message bg-red-500/20 border border-red-500/30 text-red-400 p-3 mx-4 mb-4 rounded-lg">
      <div class="flex items-center gap-2">
        <span class="text-red-400">⚠️</span>
        <span class="text-sm">{$personaError}</span>
      </div>
    </div>
  {/if}

  <!-- Message Input -->
  <div class="message-input-container p-4 border-t border-gray-700 bg-gray-800/50">
    <form on:submit={handleSubmit} class="flex gap-3">
      <div class="flex-1 relative">
        <textarea
          bind:this={inputElement}
          bind:value={messageInput}
          on:keypress={handleKeyPress}
          placeholder="Type your message..."
          class="w-full p-3 pr-12 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 resize-none focus:outline-none focus:border-blue-500 transition-colors duration-200"
          rows="1"
          disabled={isSending}
        ></textarea>
        
        <button
          type="submit"
          class="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          disabled={!messageInput.trim() || isSending}
        >
          {#if isSending}
            <div class="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
          {:else}
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
          {/if}
        </button>
      </div>
    </form>
    
    <!-- Input Hints -->
    <div class="input-hints mt-2 text-xs text-gray-500">
      <span>Press Enter to send • Shift+Enter for new line</span>
      {#if $isCompanionMode && personaConfig?.emotional_hooks}
        <span class="ml-4">💕 Emotional intelligence active</span>
      {/if}
    </div>
  </div>
</div>

<style>
  .persona-chat-interface {
    font-family: inherit;
  }
  
  .chat-messages {
    scrollbar-width: thin;
    scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
  }
  
  .chat-messages::-webkit-scrollbar {
    width: 6px;
  }
  
  .chat-messages::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .chat-messages::-webkit-scrollbar-thumb {
    background-color: rgba(156, 163, 175, 0.5);
    border-radius: 3px;
  }
  
  .chat-messages::-webkit-scrollbar-thumb:hover {
    background-color: rgba(156, 163, 175, 0.7);
  }
  
  .message-container {
    animation: fadeIn 0.3s ease-out;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .typing-indicator {
    animation: pulse 1.5s ease-in-out infinite;
  }
  
  @keyframes pulse {
    0%, 100% {
      opacity: 0.4;
    }
    50% {
      opacity: 1;
    }
  }
  
  .welcome-message {
    animation: slideIn 0.5s ease-out;
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style> 