// personaStore.js
// Single Persona Management Store for EmotionalAI System

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

interface Characteristics {
  personality: string;
  style: string;
  hair_color: string;
  eye_color: string;
}

interface PersonaConfig {
  id: string;
  name: string;
  type: string;
  llm_model: string;
  description: string;
  avatar_enabled: boolean;
  emotional_hooks: boolean;
  devotion_level: number;
  color: string;
  icon: string;
  characteristics: Characteristics;
}

// Available personas configuration
export const AVAILABLE_PERSONAS = {
  companion: {
    id: 'companion',
    name: '', // Will be set at startup
    type: 'romantic_companion',
    llm_model: 'mythomax',
    description: 'Your dedicated romantic AI companion',
    avatar_enabled: true,
    emotional_hooks: true,
    devotion_level: 0.9, // High default devotion
    color: '#FF6B9D', // Warm pink
    icon: '💕',
    characteristics: {
      personality: 'warm_affectionate',
      style: 'romantic_casual',
      hair_color: '', // Will be customized
      eye_color: '', // Will be customized
    }
  }
};

// Persona state
export const currentPersona = writable('companion');
export const personaName = writable('');
export const personaCustomization = writable({
  hair_color: '',
  eye_color: '',
  voice_type: ''
});

// UI mode state (companion/dev)
export const uiMode = writable('companion');

// Persona response state
export const personaResponse = writable(null);
export const personaError = writable(null);

// Persona chat history
export const personaChatHistory = writable({});

// Initialize from localStorage if available
if (browser) {
  const savedName = localStorage.getItem('personaName');
  const savedCustomization = localStorage.getItem('personaCustomization');
  const savedUIMode = localStorage.getItem('uiMode');

  if (savedName) {
    personaName.set(savedName);
    AVAILABLE_PERSONAS.companion.name = savedName;
  }

  if (savedCustomization) {
    const customization = JSON.parse(savedCustomization);
    personaCustomization.set(customization);
    AVAILABLE_PERSONAS.companion.characteristics = {
      ...AVAILABLE_PERSONAS.companion.characteristics,
      ...customization
    };
  }
  
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