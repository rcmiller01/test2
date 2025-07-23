// personaStore.ts
// Single Persona Management Store for EmotionalAI System

import { writable, derived, type Writable } from 'svelte/store';
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

interface PersonaCustomization {
  hair_color: string;
  eye_color: string;
  voice_type: string;
}

interface ChatHistory {
  id: number;
  type: 'user' | 'persona';
  content: string;
  timestamp: string;
  mood?: string;
  persona?: string;
  llm_model?: string;
}

type PersonaResponse = {
  response: string;
  mood: string;
  llm_model: string;
} | null;

type UIMode = 'companion' | 'dev';

// Base persona configuration
const BASE_PERSONA: PersonaConfig = {
  id: 'companion',
  name: '', // Set at startup
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
    hair_color: '', // Customized at startup
    eye_color: '', // Customized at startup
  }
};

// Store for the active persona configuration
export const personaConfig: Writable<PersonaConfig> = writable(BASE_PERSONA);

// UI mode state
export const uiMode: Writable<UIMode> = writable('companion');

// Persona state
export const personaName: Writable<string> = writable('');
export const personaCustomization: Writable<PersonaCustomization> = writable({
  hair_color: '',
  eye_color: '',
  voice_type: ''
});

// Chat state
export const personaResponse: Writable<PersonaResponse> = writable(null);
export const personaError: Writable<string | null> = writable(null);
export const personaChatHistory: Writable<Record<string, ChatHistory[]>> = writable({});

// Initialize from localStorage if available
if (browser) {
  const savedName = localStorage.getItem('personaName');
  const savedCustomization = localStorage.getItem('personaCustomization');
  const savedUIMode = localStorage.getItem('uiMode') as UIMode | null;

  if (savedName) {
    personaName.set(savedName);
    personaConfig.update(config => ({ ...config, name: savedName }));
  }

  if (savedCustomization) {
    const customization = JSON.parse(savedCustomization) as PersonaCustomization;
    personaCustomization.set(customization);
    personaConfig.update(config => ({
      ...config,
      characteristics: {
        ...config.characteristics,
        hair_color: customization.hair_color,
        eye_color: customization.eye_color
      }
    }));
  }
  
  if (savedUIMode && (savedUIMode === 'companion' || savedUIMode === 'dev')) {
    uiMode.set(savedUIMode);
  }
}

// Subscribe to changes and save to localStorage
if (browser) {
  personaName.subscribe((value: string) => {
    localStorage.setItem('personaName', value);
  });

  personaCustomization.subscribe((value: PersonaCustomization) => {
    localStorage.setItem('personaCustomization', JSON.stringify(value));
  });
  
  uiMode.subscribe((value: UIMode) => {
    localStorage.setItem('uiMode', value);
  });
}

// Derived stores
export const isCompanionMode = derived<Writable<UIMode>, boolean>(
  uiMode,
  $uiMode => $uiMode === 'companion'
);

export const isDevMode = derived<Writable<UIMode>, boolean>(
  uiMode,
  $uiMode => $uiMode === 'dev'
);

export const avatarEnabled = derived<[Writable<PersonaConfig>, Writable<UIMode>], boolean>(
  [personaConfig, uiMode],
  ([$config, $uiMode]) => $config.avatar_enabled && $uiMode === 'companion'
);

export const emotionalHooksEnabled = derived<[Writable<PersonaConfig>, Writable<UIMode>], boolean>(
  [personaConfig, uiMode],
  ([$config, $uiMode]) => $config.emotional_hooks && $uiMode === 'companion'
);// Persona management actions
export const personaActions = {
  // Set persona name
  setName: (name: string): void => {
    personaName.set(name);
    personaConfig.update(config => ({ ...config, name }));
  },

  // Update persona customization
  updateCustomization: (customization: Partial<PersonaCustomization>): void => {
    personaCustomization.update(current => ({ ...current, ...customization }));
    personaConfig.update(config => ({
      ...config,
      characteristics: {
        ...config.characteristics,
        hair_color: customization.hair_color || config.characteristics.hair_color,
        eye_color: customization.eye_color || config.characteristics.eye_color
      }
    }));
  },

  // Switch UI mode
  switchUIMode: (mode: UIMode): void => {
    uiMode.set(mode);
    console.log(`Switched to UI mode: ${mode}`);
  },

  // Send message to persona
  sendMessage: async (message: string, mood: string | null = null): Promise<void> => {
    try {
      // Add message to chat history
      personaChatHistory.update(history => ({
        ...history,
        companion: [
          ...(history.companion || []),
          {
            id: Date.now(),
            type: 'user',
            content: message,
            timestamp: new Date().toISOString(),
            mood
          }
        ]
      }));
      
      // Call persona API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, mood })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Add response to chat history
      personaChatHistory.update(history => ({
        ...history,
        companion: [
          ...(history.companion || []),
          {
            id: Date.now() + 1,
            type: 'persona',
            content: data.response,
            timestamp: new Date().toISOString(),
            mood: data.mood,
            llm_model: data.llm_model
          }
        ]
      }));
      
      personaResponse.set(data);
      personaError.set(null);
    } catch (error) {
      if (error instanceof Error) {
        personaError.set(error.message);
        console.error('Message send error:', error);
      }
    }
  },

  // Get chat history
  getChatHistory: (): ChatHistory[] => {
    const history = get(personaChatHistory);
    return history.companion || [];
  },
  
  // Clear chat history
  clearChatHistory: (): void => {
    personaChatHistory.update(history => ({
      ...history,
      companion: []
    }));
  },

  // Get persona gesture/expression
  getPersonaGesture: async (mood: string): Promise<{gesture: string, intensity: number}> => {
    try {
      const response = await fetch(`/api/gesture/${mood}`);
      if (!response.ok) {
        throw new Error(`Gesture API error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        console.error('Gesture error:', error);
        throw error;
      }
      throw new Error('Unknown error occurred');
    }
  },

  // Analyze text mood
  analyzeMood: async (text: string): Promise<{mood: string, confidence: number}> => {
    try {
      const response = await fetch(`/api/analyze/mood?text=${encodeURIComponent(text)}`);
      if (!response.ok) {
        throw new Error(`Mood analysis error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        console.error('Mood analysis error:', error);
        throw error;
      }
      throw new Error('Unknown error occurred');
    }
  }
};
  
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