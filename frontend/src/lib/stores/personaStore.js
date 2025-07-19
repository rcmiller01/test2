// personaStore.js
// Persona Management Store for 4-Persona EmotionalAI System

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Available personas configuration
export const AVAILABLE_PERSONAS = {
  mia: {
    id: 'mia',
    name: 'Mia',
    type: 'romantic_companion',
    llm_model: 'mythomax',
    description: 'Warm, affectionate romantic companion',
    avatar_enabled: true,
    emotional_hooks: true,
    color: '#FF6B9D', // Warm pink
    icon: '💕',
    characteristics: {
      personality: 'warm_affectionate',
      style: 'romantic_casual',
      hair_color: 'warm_brown',
      eye_color: 'deep_green'
    }
  },
  solene: {
    id: 'solene',
    name: 'Solene',
    type: 'romantic_companion',
    llm_model: 'openchat',
    description: 'Sophisticated, mysterious romantic companion',
    avatar_enabled: true,
    emotional_hooks: true,
    color: '#8B5CF6', // Purple
    icon: '🌹',
    characteristics: {
      personality: 'sophisticated_mysterious',
      style: 'sophisticated_elegant',
      hair_color: 'rich_black',
      eye_color: 'deep_blue'
    }
  },
  lyra: {
    id: 'lyra',
    name: 'Lyra',
    type: 'mystical_entity',
    llm_model: 'qwen2',
    description: 'Mystical, ethereal entity with curious nature',
    avatar_enabled: true,
    emotional_hooks: true,
    color: '#06B6D4', // Cyan
    icon: '✨',
    characteristics: {
      personality: 'curious_mysterious',
      style: 'mystical_flowing',
      hair_color: 'ethereal_silver',
      eye_color: 'mystical_violet'
    }
  },
  doc: {
    id: 'doc',
    name: 'Doc',
    type: 'coding_assistant',
    llm_model: 'kimik2',
    description: 'Professional coding assistant without emotional hooks',
    avatar_enabled: false,
    emotional_hooks: false,
    color: '#3B82F6', // Blue
    icon: '💻',
    characteristics: {
      personality: 'analytical_focused',
      style: 'professional_clean',
      hair_color: 'professional_dark',
      eye_color: 'sharp_blue'
    }
  }
};

// Current persona state
export const currentPersona = writable('mia');

// UI mode state (companion/dev)
export const uiMode = writable('companion');

// Persona switching state
export const isSwitchingPersona = writable(false);

// Persona response state
export const personaResponse = writable(null);
export const personaError = writable(null);

// Persona chat history
export const personaChatHistory = writable({});

// Initialize from localStorage if available
if (browser) {
  const savedPersona = localStorage.getItem('currentPersona');
  const savedUIMode = localStorage.getItem('uiMode');
  
  if (savedPersona && AVAILABLE_PERSONAS[savedPersona]) {
    currentPersona.set(savedPersona);
  }
  
  if (savedUIMode && ['companion', 'dev'].includes(savedUIMode)) {
    uiMode.set(savedUIMode);
  }
}

// Subscribe to changes and save to localStorage
if (browser) {
  currentPersona.subscribe(value => {
    localStorage.setItem('currentPersona', value);
  });
  
  uiMode.subscribe(value => {
    localStorage.setItem('uiMode', value);
  });
}

// Derived stores
export const currentPersonaConfig = derived(
  currentPersona,
  $currentPersona => AVAILABLE_PERSONAS[$currentPersona]
);

export const isCompanionMode = derived(
  uiMode,
  $uiMode => $uiMode === 'companion'
);

export const isDevMode = derived(
  uiMode,
  $uiMode => $uiMode === 'dev'
);

export const currentPersonaAvatarEnabled = derived(
  [currentPersonaConfig, isCompanionMode],
  ([$config, $isCompanion]) => $config?.avatar_enabled && $isCompanion
);

export const currentPersonaEmotionalHooks = derived(
  [currentPersonaConfig, isCompanionMode],
  ([$config, $isCompanion]) => $config?.emotional_hooks && $isCompanion
);

// Persona management functions
export const personaActions = {
  // Switch to a specific persona
  switchPersona: async (personaId) => {
    if (!AVAILABLE_PERSONAS[personaId]) {
      throw new Error(`Unknown persona: ${personaId}`);
    }
    
    isSwitchingPersona.set(true);
    
    try {
      // Update current persona
      currentPersona.set(personaId);
      
      // Clear any existing response
      personaResponse.set(null);
      personaError.set(null);
      
      // Initialize chat history for persona if not exists
      personaChatHistory.update(history => {
        if (!history[personaId]) {
          history[personaId] = [];
        }
        return history;
      });
      
      console.log(`Switched to persona: ${personaId}`);
    } catch (error) {
      personaError.set(error.message);
      console.error('Persona switch error:', error);
    } finally {
      isSwitchingPersona.set(false);
    }
  },
  
  // Switch UI mode
  switchUIMode: (mode) => {
    if (!['companion', 'dev'].includes(mode)) {
      throw new Error(`Invalid UI mode: ${mode}`);
    }
    
    uiMode.set(mode);
    console.log(`Switched to UI mode: ${mode}`);
  },
  
  // Send message to current persona
  sendMessage: async (message, mood = null) => {
    const personaId = get(currentPersona);
    const config = AVAILABLE_PERSONAS[personaId];
    
    if (!config) {
      throw new Error('No persona selected');
    }
    
    try {
      // Add message to chat history
      personaChatHistory.update(history => {
        if (!history[personaId]) {
          history[personaId] = [];
        }
        
        history[personaId].push({
          id: Date.now(),
          type: 'user',
          content: message,
          timestamp: new Date().toISOString(),
          mood: mood
        });
        
        return history;
      });
      
      // Call persona API
      const response = await fetch(`/api/phase2/${personaId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          mood: mood
        })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Add response to chat history
      personaChatHistory.update(history => {
        history[personaId].push({
          id: Date.now() + 1,
          type: 'persona',
          content: data.response,
          timestamp: new Date().toISOString(),
          persona: personaId,
          mood: data.mood,
          llm_model: data.llm_model
        });
        
        return history;
      });
      
      personaResponse.set(data);
      personaError.set(null);
      
      return data;
    } catch (error) {
      personaError.set(error.message);
      console.error('Message send error:', error);
      throw error;
    }
  },
  
  // Get chat history for current persona
  getChatHistory: (personaId = null) => {
    const currentId = personaId || get(currentPersona);
    return get(personaChatHistory)[currentId] || [];
  },
  
  // Clear chat history for a persona
  clearChatHistory: (personaId = null) => {
    const currentId = personaId || get(currentPersona);
    personaChatHistory.update(history => {
      history[currentId] = [];
      return history;
    });
  },
  
  // Get persona gesture/expression
  getPersonaGesture: async (mood) => {
    const personaId = get(currentPersona);
    
    try {
      const response = await fetch(`/api/phase2/${personaId}/gesture/${mood}`);
      if (!response.ok) {
        throw new Error(`Gesture API error: ${response.status}`);
      }
      
      const data = await response.json();
      return data.gesture;
    } catch (error) {
      console.error('Gesture fetch error:', error);
      return null;
    }
  },
  
  // Analyze mood for current persona
  analyzeMood: async (text) => {
    const personaId = get(currentPersona);
    
    try {
      const response = await fetch(`/api/phase2/${personaId}/mood/analyze?text=${encodeURIComponent(text)}`);
      if (!response.ok) {
        throw new Error(`Mood analysis error: ${response.status}`);
      }
      
      const data = await response.json();
      return data.mood;
    } catch (error) {
      console.error('Mood analysis error:', error);
      return 'neutral';
    }
  }
};

// Helper function to get store value
function get(store) {
  let value;
  store.subscribe(v => value = v)();
  return value;
} 