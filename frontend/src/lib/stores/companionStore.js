// companionStore.js
// Unified AI Companion Store - Replaces persona system

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

interface CompanionConfig {
  id: string;
  name: string;
  type: string;
  description: string;
  avatar_enabled: boolean;
  emotional_intelligence: boolean;
  creative_collaboration: boolean;
  technical_assistance: boolean;
  voice_enabled: boolean;
  personality_traits: string[];
  capabilities: string[];
}

// Unified companion configuration
const DEFAULT_COMPANION_CONFIG: CompanionConfig = {
  id: 'unified_companion',
  name: '', // Will be set during greeting
  type: 'unified_ai_companion',
  description: 'Your unified AI companion for all needs',
  avatar_enabled: true,
  emotional_intelligence: true,
  creative_collaboration: true,
  technical_assistance: true,
  voice_enabled: true,
  personality_traits: [
    'empathetic',
    'creative',
    'intelligent',
    'supportive',
    'adaptable',
    'curious'
  ],
  capabilities: [
    'emotional_support',
    'creative_collaboration',
    'technical_assistance',
    'voice_interaction',
    'memory_recall',
    'proactive_suggestions',
    'learning_adaptation'
  ]
};

// Core companion state
export const companionName = writable('');
export const companionConfig = writable(DEFAULT_COMPANION_CONFIG);
export const isCompanionInitialized = writable(false);

// Conversation state
export const conversationHistory = writable([]);
export const currentResponse = writable(null);
export const isThinking = writable(false);
export const responseError = writable(null);

// User interaction state
export const userEngagementLevel = writable('active'); // 'active', 'idle', 'away'
export const currentInteractionMode = writable('text'); // 'text', 'voice', 'mixed'
export const preferredResponseStyle = writable('balanced'); // 'creative', 'technical', 'emotional', 'balanced'

// Creative collaboration state
export const activeCreativeProject = writable(null);
export const availableCreativeModels = writable([]);
export const creativeGallery = writable([]);

// Memory and learning state
export const memoryStrength = writable(0); // 0-100, grows over time
export const relationshipDepth = writable(0); // 0-100, grows with interaction
export const learningProgress = writable({
  interests: [],
  preferences: {},
  communication_style: 'adaptive',
  emotional_patterns: {}
});

// Proactive features state
export const proactiveMode = writable(false);
export const lastProactiveContact = writable(null);
export const suggestedActivities = writable([]);

// Initialize from localStorage if available
if (browser) {
  const savedName = localStorage.getItem('companionName');
  const savedConfig = localStorage.getItem('companionConfig');
  const savedHistory = localStorage.getItem('conversationHistory');
  const savedLearning = localStorage.getItem('learningProgress');

  if (savedName) {
    companionName.set(savedName);
    const config = { ...DEFAULT_COMPANION_CONFIG, name: savedName };
    companionConfig.set(config);
    isCompanionInitialized.set(true);
  }

  if (savedConfig) {
    try {
      const config = JSON.parse(savedConfig);
      companionConfig.set({ ...DEFAULT_COMPANION_CONFIG, ...config });
    } catch (e) {
      console.error('Error loading companion config:', e);
    }
  }

  if (savedHistory) {
    try {
      const history = JSON.parse(savedHistory);
      conversationHistory.set(history);
    } catch (e) {
      console.error('Error loading conversation history:', e);
    }
  }

  if (savedLearning) {
    try {
      const learning = JSON.parse(savedLearning);
      learningProgress.set(learning);
    } catch (e) {
      console.error('Error loading learning progress:', e);
    }
  }
}

// Subscribe to changes and save to localStorage
if (browser) {
  companionName.subscribe(value => {
    localStorage.setItem('companionName', value);
  });

  companionConfig.subscribe(value => {
    localStorage.setItem('companionConfig', JSON.stringify(value));
  });

  conversationHistory.subscribe(value => {
    // Only save last 100 messages to prevent localStorage bloat
    const recentHistory = value.slice(-100);
    localStorage.setItem('conversationHistory', JSON.stringify(recentHistory));
  });

  learningProgress.subscribe(value => {
    localStorage.setItem('learningProgress', JSON.stringify(value));
  });
}

// Derived stores
export const companionDisplayName = derived(
  companionName,
  $name => $name || 'Your AI Companion'
);

export const isVoiceEnabled = derived(
  companionConfig,
  $config => $config.voice_enabled
);

export const hasActiveProject = derived(
  activeCreativeProject,
  $project => $project !== null
);

export const canSuggestProactively = derived(
  [proactiveMode, lastProactiveContact],
  ([$proactive, $lastContact]) => {
    if (!$proactive) return false;
    if (!$lastContact) return true;
    
    const timeDiff = Date.now() - new Date($lastContact).getTime();
    const hoursSinceLastContact = timeDiff / (1000 * 60 * 60);
    return hoursSinceLastContact >= 4; // Can suggest after 4 hours
  }
);

// Action functions
export const companionActions = {
  // Initialize companion with name
  setName: async (name: string) => {
    companionName.set(name);
    const config = { ...DEFAULT_COMPANION_CONFIG, name };
    companionConfig.set(config);
    isCompanionInitialized.set(true);
    
    // Send initialization to backend
    try {
      await fetch('/api/companion/initialize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, config })
      });
    } catch (error) {
      console.error('Error initializing companion:', error);
    }
  },

  // Send message to companion
  sendMessage: async (message: string, context: any = {}) => {
    isThinking.set(true);
    responseError.set(null);

    try {
      const response = await fetch('/api/companion/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          context,
          interaction_mode: currentInteractionMode,
          response_style: preferredResponseStyle
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      
      // Update conversation history
      conversationHistory.update(history => [
        ...history,
        {
          id: Date.now(),
          timestamp: new Date().toISOString(),
          user_message: message,
          companion_response: data.response,
          emotion: data.emotion,
          context: data.context
        }
      ]);

      currentResponse.set(data);
      
      // Update learning and memory
      if (data.learning_updates) {
        learningProgress.update(current => ({
          ...current,
          ...data.learning_updates
        }));
      }

      return data;

    } catch (error) {
      console.error('Error sending message:', error);
      responseError.set(error.message);
      throw error;
    } finally {
      isThinking.set(false);
    }
  },

  // Start creative collaboration
  startCreativeProject: async (projectType: string, requirements: any = {}) => {
    try {
      const response = await fetch('/api/companion/creative/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ projectType, requirements })
      });

      const data = await response.json();
      activeCreativeProject.set(data.project);
      
      return data;
    } catch (error) {
      console.error('Error starting creative project:', error);
      throw error;
    }
  },

  // Enable proactive mode
  enableProactiveMode: async () => {
    proactiveMode.set(true);
    
    try {
      await fetch('/api/companion/proactive/enable', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      console.error('Error enabling proactive mode:', error);
    }
  },

  // Update interaction preferences
  updatePreferences: (preferences: any) => {
    if (preferences.interactionMode) {
      currentInteractionMode.set(preferences.interactionMode);
    }
    if (preferences.responseStyle) {
      preferredResponseStyle.set(preferences.responseStyle);
    }
    if (preferences.voiceEnabled !== undefined) {
      companionConfig.update(config => ({
        ...config,
        voice_enabled: preferences.voiceEnabled
      }));
    }
  },

  // Clear conversation history
  clearHistory: () => {
    conversationHistory.set([]);
    activeCreativeProject.set(null);
    currentResponse.set(null);
  },

  // Reset companion (for development/testing)
  resetCompanion: () => {
    if (browser) {
      localStorage.removeItem('companionName');
      localStorage.removeItem('companionConfig');
      localStorage.removeItem('conversationHistory');
      localStorage.removeItem('learningProgress');
    }
    
    companionName.set('');
    companionConfig.set(DEFAULT_COMPANION_CONFIG);
    isCompanionInitialized.set(false);
    conversationHistory.set([]);
    currentResponse.set(null);
    activeCreativeProject.set(null);
    learningProgress.set({
      interests: [],
      preferences: {},
      communication_style: 'adaptive',
      emotional_patterns: {}
    });
  }
};
