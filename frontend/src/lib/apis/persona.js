// persona.js
// API Integration for 4-Persona EmotionalAI System

import { currentPersona, currentPersonaConfig } from '$lib/stores/personaStore.js';
import { get } from 'svelte/store';

// Base API configuration
const API_BASE = '/api/phase2';
const DEFAULT_TIMEOUT = 30000;

// Helper function to get store value
function getStoreValue(store) {
  let value;
  store.subscribe(v => value = v)();
  return value;
}

// API request helper
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    timeout: DEFAULT_TIMEOUT,
    ...options
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Request failed for ${endpoint}:`, error);
    throw error;
  }
}

// Persona Chat API
export const personaChatAPI = {
  // Send message to persona
  sendMessage: async (personaId, message, mood = null) => {
    const payload = {
      message: message,
      mood: mood
    };

    return await apiRequest(`/${personaId}/chat`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Analyze mood for text
  analyzeMood: async (personaId, text) => {
    const encodedText = encodeURIComponent(text);
    return await apiRequest(`/${personaId}/mood/analyze?text=${encodedText}`);
  },

  // Get persona gesture/expression
  getGesture: async (personaId, mood) => {
    return await apiRequest(`/${personaId}/gesture/${mood}`);
  }
};

// Character Generation API
export const characterGenerationAPI = {
  // Generate character image
  generateCharacter: async (persona, settings, nsfwEnabled = false) => {
    const payload = {
      persona: persona,
      settings: settings,
      nsfw_enabled: nsfwEnabled
    };

    return await apiRequest('/character/generate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Get character template
  getCharacterTemplate: async (personaId) => {
    return await apiRequest(`/character/template/${personaId}`);
  },

  // List available character styles
  getCharacterStyles: async () => {
    return await apiRequest('/character/styles');
  }
};

// UI Mode API
export const uiModeAPI = {
  // Get UI mode configuration
  getUIModeConfig: async (mode) => {
    return await apiRequest(`/ui/mode/${mode}`);
  },

  // Update UI mode settings
  updateUIModeSettings: async (mode, settings) => {
    return await apiRequest(`/ui/mode/${mode}`, {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }
};

// Persona Management API
export const personaManagementAPI = {
  // Get all available personas
  getPersonas: async () => {
    return await apiRequest('/personas');
  },

  // Get persona details
  getPersonaDetails: async (personaId) => {
    return await apiRequest(`/personas/${personaId}`);
  },

  // Get persona status
  getPersonaStatus: async (personaId) => {
    return await apiRequest(`/personas/${personaId}/status`);
  },

  // Switch to persona
  switchPersona: async (personaId) => {
    return await apiRequest(`/personas/${personaId}/switch`, {
      method: 'POST'
    });
  }
};

// LLM Router API
export const llmRouterAPI = {
  // Get available models
  getModels: async () => {
    return await apiRequest('/llm/models');
  },

  // Get model status
  getModelStatus: async (modelId) => {
    return await apiRequest(`/llm/models/${modelId}/status`);
  },

  // Test model connection
  testModelConnection: async (modelId) => {
    return await apiRequest(`/llm/models/${modelId}/test`, {
      method: 'POST'
    });
  }
};

// Animation System API
export const animationAPI = {
  // Get animation for mood
  getAnimation: async (personaId, mood, animationType = 'idle') => {
    return await apiRequest(`/animation/${personaId}/${mood}/${animationType}`);
  },

  // Get available animations
  getAvailableAnimations: async (personaId) => {
    return await apiRequest(`/animation/${personaId}/list`);
  },

  // Trigger animation
  triggerAnimation: async (personaId, animationId) => {
    return await apiRequest(`/animation/${personaId}/trigger`, {
      method: 'POST',
      body: JSON.stringify({ animation_id: animationId })
    });
  }
};

// Memory System API
export const memoryAPI = {
  // Get persona memories
  getMemories: async (personaId, limit = 50) => {
    return await apiRequest(`/memory/${personaId}?limit=${limit}`);
  },

  // Add memory
  addMemory: async (personaId, memory) => {
    return await apiRequest(`/memory/${personaId}`, {
      method: 'POST',
      body: JSON.stringify(memory)
    });
  },

  // Search memories
  searchMemories: async (personaId, query) => {
    const encodedQuery = encodeURIComponent(query);
    return await apiRequest(`/memory/${personaId}/search?q=${encodedQuery}`);
  }
};

// Settings API
export const settingsAPI = {
  // Get persona settings
  getPersonaSettings: async (personaId) => {
    return await apiRequest(`/settings/${personaId}`);
  },

  // Update persona settings
  updatePersonaSettings: async (personaId, settings) => {
    return await apiRequest(`/settings/${personaId}`, {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  },

  // Get global settings
  getGlobalSettings: async () => {
    return await apiRequest('/settings/global');
  },

  // Update global settings
  updateGlobalSettings: async (settings) => {
    return await apiRequest('/settings/global', {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }
};

// Health Check API
export const healthAPI = {
  // Check API health
  checkHealth: async () => {
    return await apiRequest('/health');
  },

  // Check persona health
  checkPersonaHealth: async (personaId) => {
    return await apiRequest(`/health/${personaId}`);
  },

  // Get system status
  getSystemStatus: async () => {
    return await apiRequest('/health/system');
  }
};

// Convenience functions for current persona
export const currentPersonaAPI = {
  // Send message to current persona
  sendMessage: async (message, mood = null) => {
    const personaId = getStoreValue(currentPersona);
    return await personaChatAPI.sendMessage(personaId, message, mood);
  },

  // Analyze mood for current persona
  analyzeMood: async (text) => {
    const personaId = getStoreValue(currentPersona);
    return await personaChatAPI.analyzeMood(personaId, text);
  },

  // Get gesture for current persona
  getGesture: async (mood) => {
    const personaId = getStoreValue(currentPersona);
    return await personaChatAPI.getGesture(personaId, mood);
  },

  // Get current persona details
  getDetails: async () => {
    const personaId = getStoreValue(currentPersona);
    return await personaManagementAPI.getPersonaDetails(personaId);
  },

  // Get current persona status
  getStatus: async () => {
    const personaId = getStoreValue(currentPersona);
    return await personaManagementAPI.getPersonaStatus(personaId);
  }
};

// Error handling utilities
export const apiUtils = {
  // Handle API errors
  handleError: (error, context = '') => {
    console.error(`API Error in ${context}:`, error);
    
    // Return user-friendly error message
    if (error.message.includes('API Error:')) {
      return {
        success: false,
        error: error.message,
        context: context
      };
    }
    
    return {
      success: false,
      error: 'Network error. Please check your connection.',
      context: context
    };
  },

  // Retry API call
  retry: async (apiCall, maxRetries = 3, delay = 1000) => {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await apiCall();
      } catch (error) {
        if (i === maxRetries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
      }
    }
  },

  // Validate API response
  validateResponse: (response, requiredFields = []) => {
    if (!response || typeof response !== 'object') {
      throw new Error('Invalid response format');
    }
    
    for (const field of requiredFields) {
      if (!(field in response)) {
        throw new Error(`Missing required field: ${field}`);
      }
    }
    
    return response;
  }
};

// Export all APIs
export default {
  personaChat: personaChatAPI,
  characterGeneration: characterGenerationAPI,
  uiMode: uiModeAPI,
  personaManagement: personaManagementAPI,
  llmRouter: llmRouterAPI,
  animation: animationAPI,
  memory: memoryAPI,
  settings: settingsAPI,
  health: healthAPI,
  currentPersona: currentPersonaAPI,
  utils: apiUtils
}; 