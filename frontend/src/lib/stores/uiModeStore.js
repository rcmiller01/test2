// uiModeStore.js
// UI Mode Management Store for Companion/Dev Mode Switching

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// UI Mode configurations
export const UI_MODES = {
  companion: {
    id: 'companion',
    name: 'Companion Mode',
    description: 'Romantic AI companion experience with avatars',
    icon: '💕',
    color: '#FF6B9D',
    features: {
      avatar_visible: true,
      emotional_hooks: true,
      romantic_gestures: true,
      voice_synthesis: true,
      activity_suggestions: true,
      relationship_tracking: true,
      nsfw_generation: true
    },
    theme: {
      primary: '#FF6B9D',
      secondary: '#FFB3D1',
      background: '#FFF5F7',
      text: '#2D3748'
    }
  },
  dev: {
    id: 'dev',
    name: 'Dev Mode',
    description: 'Professional development interface',
    icon: '💻',
    color: '#3B82F6',
    features: {
      avatar_visible: false,
      emotional_hooks: false,
      romantic_gestures: false,
      voice_synthesis: false,
      activity_suggestions: false,
      relationship_tracking: false,
      nsfw_generation: false
    },
    theme: {
      primary: '#3B82F6',
      secondary: '#93C5FD',
      background: '#F8FAFC',
      text: '#1F2937'
    }
  }
};

// Current UI mode state
export const currentUIMode = writable('companion');

// UI mode switching state
export const isSwitchingMode = writable(false);

// Theme state
export const currentTheme = writable(UI_MODES.companion.theme);

// Feature flags state
export const currentFeatures = writable(UI_MODES.companion.features);

// Initialize from localStorage if available
if (browser) {
  const savedMode = localStorage.getItem('uiMode');
  if (savedMode && UI_MODES[savedMode]) {
    currentUIMode.set(savedMode);
  }
}

// Subscribe to changes and save to localStorage
if (browser) {
  currentUIMode.subscribe(mode => {
    localStorage.setItem('uiMode', mode);
    
    // Update theme and features when mode changes
    if (UI_MODES[mode]) {
      currentTheme.set(UI_MODES[mode].theme);
      currentFeatures.set(UI_MODES[mode].features);
    }
  });
}

// Derived stores
export const isCompanionMode = derived(
  currentUIMode,
  $mode => $mode === 'companion'
);

export const isDevMode = derived(
  currentUIMode,
  $mode => $mode === 'dev'
);

export const currentModeConfig = derived(
  currentUIMode,
  $mode => UI_MODES[$mode]
);

// UI Mode management functions
export const uiModeActions = {
  // Switch to a specific UI mode
  switchMode: async (modeId) => {
    if (!UI_MODES[modeId]) {
      throw new Error(`Unknown UI mode: ${modeId}`);
    }
    
    isSwitchingMode.set(true);
    
    try {
      // Update current mode
      currentUIMode.set(modeId);
      
      // Update theme and features
      currentTheme.set(UI_MODES[modeId].theme);
      currentFeatures.set(UI_MODES[modeId].features);
      
      // Apply theme to document
      if (browser) {
        applyThemeToDocument(UI_MODES[modeId].theme);
      }
      
      console.log(`Switched to UI mode: ${modeId}`);
    } catch (error) {
      console.error('UI mode switch error:', error);
      throw error;
    } finally {
      isSwitchingMode.set(false);
    }
  },
  
  // Toggle between companion and dev modes
  toggleMode: async () => {
    const currentMode = get(currentUIMode);
    const newMode = currentMode === 'companion' ? 'dev' : 'companion';
    await uiModeActions.switchMode(newMode);
  },
  
  // Get current mode configuration
  getCurrentModeConfig: () => {
    const mode = get(currentUIMode);
    return UI_MODES[mode];
  },
  
  // Check if a feature is enabled in current mode
  isFeatureEnabled: (featureName) => {
    const features = get(currentFeatures);
    return features[featureName] || false;
  },
  
  // Get current theme
  getCurrentTheme: () => {
    return get(currentTheme);
  }
};

// Helper function to apply theme to document
function applyThemeToDocument(theme) {
  if (typeof document !== 'undefined') {
    const root = document.documentElement;
    
    // Set CSS custom properties
    root.style.setProperty('--color-primary', theme.primary);
    root.style.setProperty('--color-secondary', theme.secondary);
    root.style.setProperty('--color-background', theme.background);
    root.style.setProperty('--color-text', theme.text);
    
    // Add theme class to body
    document.body.className = document.body.className
      .replace(/theme-\w+/g, '')
      .trim();
    document.body.classList.add(`theme-${theme.id}`);
  }
}

// Helper function to get store value
function get(store) {
  let value;
  store.subscribe(v => value = v)();
  return value;
}

// Initialize theme on load
if (browser) {
  const mode = get(currentUIMode);
  if (UI_MODES[mode]) {
    applyThemeToDocument(UI_MODES[mode].theme);
  }
} 