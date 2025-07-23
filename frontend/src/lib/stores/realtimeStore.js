// realtimeStore.js
// Real-time Integration Store for EmotionalAI Phase 3 Features

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { socket } from './index.js';
import { currentPersona, currentPersonaConfig } from './personaStore.js';

// Real-time connection state
export const realtimeConnection = writable({
  isConnected: false,
  isConnecting: false,
  lastConnected: null,
  connectionAttempts: 0,
  error: null
});

// Real-time avatar state
export const realtimeAvatar = writable({
  isActive: false,
  currentMood: 'neutral',
  currentExpression: 'neutral',
  currentGesture: null,
  isAnimating: false,
  animationProgress: 0,
  lastUpdate: null,
  syncStatus: 'idle' // idle, syncing, synced, error
});

// Real-time memory notifications
export const realtimeMemory = writable({
  notifications: [],
  unreadCount: 0,
  lastMemoryId: null,
  isProcessing: false,
  processingProgress: 0
});

// Real-time haptic feedback
export const realtimeHaptic = writable({
  isActive: false,
  currentPattern: null,
  intensity: 0,
  duration: 0,
  remainingTime: 0,
  isVibrating: false,
  lastTrigger: null
});

// Real-time biometric data
export const realtimeBiometric = writable({
  isMonitoring: false,
  heartRate: null,
  heartRateHistory: [],
  stressLevel: null,
  energyLevel: null,
  romanticSync: null,
  lastReading: null,
  isConnected: false
});

// Real-time VR experiences
export const realtimeVR = writable({
  isActive: false,
  currentScene: null,
  sceneProgress: 0,
  isGenerating: false,
  generationProgress: 0,
  participants: [],
  lastUpdate: null
});

// Real-time voice synthesis
export const realtimeVoice = writable({
  isSpeaking: false,
  currentText: '',
  emotion: 'neutral',
  pitch: 1.0,
  rate: 1.0,
  volume: 1.0,
  isListening: false,
  lastUtterance: null
});

// Real-time relationship insights
export const realtimeRelationship = writable({
  healthScore: null,
  recentInsights: [],
  recommendations: [],
  conflictAlerts: [],
  growthOpportunities: [],
  lastAnalysis: null
});

// Real-time system events
export const realtimeEvents = writable({
  events: [],
  unreadEvents: 0,
  lastEvent: null
});

// Real-time presence and collaboration
export const realtimePresence = writable({
  activeUsers: [],
  currentUser: null,
  userStates: {},
  collaborationRooms: []
});

// Initialize real-time connection
export function initializeRealtime() {
  if (!browser) return;

  // Subscribe to socket connection changes
  socket.subscribe($socket => {
    if ($socket) {
      setupRealtimeListeners($socket);
    }
  });
}

// Setup real-time event listeners
function setupRealtimeListeners(socket) {
  // Connection events
  socket.on('connect', () => {
    realtimeConnection.update(state => ({
      ...state,
      isConnected: true,
      isConnecting: false,
      lastConnected: Date.now(),
      error: null
    }));
    
    // Join persona-specific room
    const persona = get(currentPersona);
    socket.emit('join-persona-room', { persona });
  });

  socket.on('disconnect', () => {
    realtimeConnection.update(state => ({
      ...state,
      isConnected: false,
      isConnecting: false
    }));
  });

  socket.on('connect_error', (error) => {
    realtimeConnection.update(state => ({
      ...state,
      isConnected: false,
      isConnecting: false,
      error: error.message,
      connectionAttempts: state.connectionAttempts + 1
    }));
  });

  // Avatar real-time updates
  socket.on('avatar:update', (data) => {
    realtimeAvatar.update(state => ({
      ...state,
      ...data,
      lastUpdate: Date.now(),
      syncStatus: 'synced'
    }));
  });

  socket.on('avatar:animation:start', (data) => {
    realtimeAvatar.update(state => ({
      ...state,
      isAnimating: true,
      animationProgress: 0,
      currentGesture: data.gesture,
      currentExpression: data.expression
    }));
  });

  socket.on('avatar:animation:progress', (data) => {
    realtimeAvatar.update(state => ({
      ...state,
      animationProgress: data.progress
    }));
  });

  socket.on('avatar:animation:complete', () => {
    realtimeAvatar.update(state => ({
      ...state,
      isAnimating: false,
      animationProgress: 100
    }));
  });

  // Memory real-time notifications
  socket.on('memory:notification', (data) => {
    realtimeMemory.update(state => ({
      ...state,
      notifications: [...state.notifications, {
        id: Date.now(),
        type: data.type,
        title: data.title,
        message: data.message,
        memoryId: data.memoryId,
        timestamp: Date.now(),
        isRead: false
      }],
      unreadCount: state.unreadCount + 1,
      lastMemoryId: data.memoryId
    }));
  });

  socket.on('memory:processing:start', () => {
    realtimeMemory.update(state => ({
      ...state,
      isProcessing: true,
      processingProgress: 0
    }));
  });

  socket.on('memory:processing:progress', (data) => {
    realtimeMemory.update(state => ({
      ...state,
      processingProgress: data.progress
    }));
  });

  socket.on('memory:processing:complete', () => {
    realtimeMemory.update(state => ({
      ...state,
      isProcessing: false,
      processingProgress: 100
    }));
  });

  // Haptic feedback real-time events
  socket.on('haptic:trigger', (data) => {
    realtimeHaptic.update(state => ({
      ...state,
      isActive: true,
      currentPattern: data.pattern,
      intensity: data.intensity,
      duration: data.duration,
      remainingTime: data.duration,
      isVibrating: true,
      lastTrigger: Date.now()
    }));

    // Trigger haptic feedback on device
    if (browser && navigator.vibrate) {
      navigator.vibrate(data.duration);
    }
  });

  socket.on('haptic:stop', () => {
    realtimeHaptic.update(state => ({
      ...state,
      isActive: false,
      isVibrating: false,
      remainingTime: 0
    }));
  });

  // Biometric real-time data
  socket.on('biometric:update', (data) => {
    realtimeBiometric.update(state => ({
      ...state,
      ...data,
      lastReading: Date.now()
    }));
  });

  socket.on('biometric:connected', () => {
    realtimeBiometric.update(state => ({
      ...state,
      isConnected: true,
      isMonitoring: true
    }));
  });

  socket.on('biometric:disconnected', () => {
    realtimeBiometric.update(state => ({
      ...state,
      isConnected: false,
      isMonitoring: false
    }));
  });

  // VR real-time experiences
  socket.on('vr:scene:start', (data) => {
    realtimeVR.update(state => ({
      ...state,
      isActive: true,
      currentScene: data.scene,
      sceneProgress: 0,
      participants: data.participants || []
    }));
  });

  socket.on('vr:scene:progress', (data) => {
    realtimeVR.update(state => ({
      ...state,
      sceneProgress: data.progress
    }));
  });

  socket.on('vr:generation:start', () => {
    realtimeVR.update(state => ({
      ...state,
      isGenerating: true,
      generationProgress: 0
    }));
  });

  socket.on('vr:generation:progress', (data) => {
    realtimeVR.update(state => ({
      ...state,
      generationProgress: data.progress
    }));
  });

  socket.on('vr:generation:complete', (data) => {
    realtimeVR.update(state => ({
      ...state,
      isGenerating: false,
      generationProgress: 100
    }));
  });

  socket.on('vr:scene:end', () => {
    realtimeVR.update(state => ({
      ...state,
      isActive: false,
      currentScene: null,
      sceneProgress: 0
    }));
  });

  // Voice real-time synthesis
  socket.on('voice:speak:start', (data) => {
    realtimeVoice.update(state => ({
      ...state,
      isSpeaking: true,
      currentText: data.text,
      emotion: data.emotion,
      pitch: data.pitch,
      rate: data.rate,
      volume: data.volume
    }));
  });

  socket.on('voice:speak:end', () => {
    realtimeVoice.update(state => ({
      ...state,
      isSpeaking: false,
      currentText: '',
      lastUtterance: Date.now()
    }));
  });

  socket.on('voice:listen:start', () => {
    realtimeVoice.update(state => ({
      ...state,
      isListening: true
    }));
  });

  socket.on('voice:listen:end', () => {
    realtimeVoice.update(state => ({
      ...state,
      isListening: false
    }));
  });

  // Relationship real-time insights
  socket.on('relationship:insight', (data) => {
    realtimeRelationship.update(state => ({
      ...state,
      recentInsights: [...state.recentInsights, {
        id: Date.now(),
        type: data.type,
        message: data.message,
        timestamp: Date.now()
      }].slice(-10) // Keep last 10 insights
    }));
  });

  socket.on('relationship:health:update', (data) => {
    realtimeRelationship.update(state => ({
      ...state,
      healthScore: data.healthScore,
      lastAnalysis: Date.now()
    }));
  });

  socket.on('relationship:recommendation', (data) => {
    realtimeRelationship.update(state => ({
      ...state,
      recommendations: [...state.recommendations, {
        id: Date.now(),
        type: data.type,
        title: data.title,
        description: data.description,
        priority: data.priority,
        timestamp: Date.now()
      }].slice(-5) // Keep last 5 recommendations
    }));
  });

  // System events
  socket.on('system:event', (data) => {
    realtimeEvents.update(state => ({
      ...state,
      events: [...state.events, {
        id: Date.now(),
        type: data.type,
        title: data.title,
        message: data.message,
        severity: data.severity,
        timestamp: Date.now(),
        isRead: false
      }].slice(-20), // Keep last 20 events
      unreadEvents: state.unreadEvents + 1,
      lastEvent: Date.now()
    }));
  });

  // Presence and collaboration
  socket.on('presence:update', (data) => {
    realtimePresence.update(state => ({
      ...state,
      activeUsers: data.activeUsers,
      userStates: data.userStates
    }));
  });

  socket.on('collaboration:room:join', (data) => {
    realtimePresence.update(state => ({
      ...state,
      collaborationRooms: [...state.collaborationRooms, data.room]
    }));
  });

  socket.on('collaboration:room:leave', (data) => {
    realtimePresence.update(state => ({
      ...state,
      collaborationRooms: state.collaborationRooms.filter(room => room.id !== data.roomId)
    }));
  });
}

// Real-time action functions
export const realtimeActions = {
  // Avatar actions
  updateAvatarMood: (mood) => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('avatar:update:mood', { mood });
    }
  },

  triggerAvatarGesture: (gesture) => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('avatar:trigger:gesture', { gesture });
    }
  },

  updateAvatarExpression: (expression) => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('avatar:update:expression', { expression });
    }
  },

  // Memory actions
  markMemoryAsRead: (memoryId) => {
    realtimeMemory.update(state => ({
      ...state,
      notifications: state.notifications.map(notification => 
        notification.memoryId === memoryId 
          ? { ...notification, isRead: true }
          : notification
      ),
      unreadCount: Math.max(0, state.unreadCount - 1)
    }));
  },

  clearMemoryNotifications: () => {
    realtimeMemory.update(state => ({
      ...state,
      notifications: [],
      unreadCount: 0
    }));
  },

  // Haptic actions
  triggerHaptic: (pattern, intensity = 50, duration = 2000) => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('haptic:trigger', { pattern, intensity, duration });
    }
  },

  stopHaptic: () => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('haptic:stop');
    }
  },

  // VR actions
  startVRScene: (sceneId, sceneType = 'pre_created') => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('vr:scene:start', { sceneId, sceneType });
    }
  },

  stopVRScene: () => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('vr:scene:stop');
    }
  },

  // Voice actions
  speakText: (text, emotion = 'neutral', pitch = 1.0, rate = 1.0, volume = 1.0) => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('voice:speak', { text, emotion, pitch, rate, volume });
    }
  },

  stopSpeaking: () => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('voice:stop');
    }
  },

  startListening: () => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('voice:listen:start');
    }
  },

  stopListening: () => {
    const $socket = get(socket);
    if ($socket && $socket.connected) {
      $socket.emit('voice:listen:stop');
    }
  },

  // System actions
  markEventAsRead: (eventId) => {
    realtimeEvents.update(state => ({
      ...state,
      events: state.events.map(event => 
        event.id === eventId 
          ? { ...event, isRead: true }
          : event
      ),
      unreadEvents: Math.max(0, state.unreadEvents - 1)
    }));
  },

  clearEvents: () => {
    realtimeEvents.update(state => ({
      ...state,
      events: [],
      unreadEvents: 0
    }));
  }
};

// Derived stores for combined real-time state
export const realtimeStatus = derived(
  [realtimeConnection, realtimeAvatar, realtimeMemory, realtimeHaptic, realtimeBiometric, realtimeVR, realtimeVoice],
  ([$connection, $avatar, $memory, $haptic, $biometric, $vr, $voice]) => ({
    isConnected: $connection.isConnected,
    hasActiveFeatures: $avatar.isActive || $memory.isProcessing || $haptic.isActive || $vr.isActive || $voice.isSpeaking,
    totalNotifications: $memory.unreadCount + $realtimeEvents.unreadEvents,
    systemHealth: {
      avatar: $avatar.syncStatus,
      memory: $memory.isProcessing ? 'processing' : 'idle',
      haptic: $haptic.isActive ? 'active' : 'idle',
      biometric: $biometric.isConnected ? 'connected' : 'disconnected',
      vr: $vr.isActive ? 'active' : 'idle',
      voice: $voice.isSpeaking ? 'speaking' : 'idle'
    }
  })
);

// Helper function to get store value
function get(store) {
  let value;
  store.subscribe(v => value = v)();
  return value;
}

// Initialize real-time system when store is imported
if (browser) {
  initializeRealtime();
} 