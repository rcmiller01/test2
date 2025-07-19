// realtimeService.js
// Real-time Service Layer for EmotionalAI Phase 3 Features

import { socket } from '../stores/index.js';
import { currentPersona } from '../stores/personaStore.js';
import { realtimeActions } from '../stores/realtimeStore.js';

class RealtimeService {
  constructor() {
    this.isInitialized = false;
    this.eventHandlers = new Map();
    this.retryAttempts = 0;
    this.maxRetries = 5;
    this.retryDelay = 1000;
  }

  // Initialize the real-time service
  async initialize() {
    if (this.isInitialized) return;

    try {
      // Wait for socket to be available
      await this.waitForSocket();
      
      // Setup event handlers
      this.setupEventHandlers();
      
      // Join persona-specific room
      this.joinPersonaRoom();
      
      this.isInitialized = true;
      console.log('[RealtimeService] Initialized successfully');
    } catch (error) {
      console.error('[RealtimeService] Initialization failed:', error);
      throw error;
    }
  }

  // Wait for socket connection
  async waitForSocket() {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Socket connection timeout'));
      }, 10000);

      const checkSocket = () => {
        const $socket = get(socket);
        if ($socket && $socket.connected) {
          clearTimeout(timeout);
          resolve($socket);
        } else if (this.retryAttempts < this.maxRetries) {
          this.retryAttempts++;
          setTimeout(checkSocket, this.retryDelay);
        } else {
          clearTimeout(timeout);
          reject(new Error('Max retry attempts reached'));
        }
      };

      checkSocket();
    });
  }

  // Setup event handlers
  setupEventHandlers() {
    const $socket = get(socket);
    if (!$socket) return;

    // Avatar events
    this.on('avatar:update', this.handleAvatarUpdate.bind(this));
    this.on('avatar:animation:start', this.handleAvatarAnimationStart.bind(this));
    this.on('avatar:animation:progress', this.handleAvatarAnimationProgress.bind(this));
    this.on('avatar:animation:complete', this.handleAvatarAnimationComplete.bind(this));

    // Memory events
    this.on('memory:notification', this.handleMemoryNotification.bind(this));
    this.on('memory:processing:start', this.handleMemoryProcessingStart.bind(this));
    this.on('memory:processing:progress', this.handleMemoryProcessingProgress.bind(this));
    this.on('memory:processing:complete', this.handleMemoryProcessingComplete.bind(this));

    // Haptic events
    this.on('haptic:trigger', this.handleHapticTrigger.bind(this));
    this.on('haptic:stop', this.handleHapticStop.bind(this));

    // Biometric events
    this.on('biometric:update', this.handleBiometricUpdate.bind(this));
    this.on('biometric:connected', this.handleBiometricConnected.bind(this));
    this.on('biometric:disconnected', this.handleBiometricDisconnected.bind(this));

    // VR events
    this.on('vr:scene:start', this.handleVRSceneStart.bind(this));
    this.on('vr:scene:progress', this.handleVRSceneProgress.bind(this));
    this.on('vr:generation:start', this.handleVRGenerationStart.bind(this));
    this.on('vr:generation:progress', this.handleVRGenerationProgress.bind(this));
    this.on('vr:generation:complete', this.handleVRGenerationComplete.bind(this));
    this.on('vr:scene:end', this.handleVRSceneEnd.bind(this));

    // Voice events
    this.on('voice:speak:start', this.handleVoiceSpeakStart.bind(this));
    this.on('voice:speak:end', this.handleVoiceSpeakEnd.bind(this));
    this.on('voice:listen:start', this.handleVoiceListenStart.bind(this));
    this.on('voice:listen:end', this.handleVoiceListenEnd.bind(this));

    // Relationship events
    this.on('relationship:insight', this.handleRelationshipInsight.bind(this));
    this.on('relationship:health:update', this.handleRelationshipHealthUpdate.bind(this));
    this.on('relationship:recommendation', this.handleRelationshipRecommendation.bind(this));

    // System events
    this.on('system:event', this.handleSystemEvent.bind(this));

    // Presence events
    this.on('presence:update', this.handlePresenceUpdate.bind(this));
    this.on('collaboration:room:join', this.handleCollaborationRoomJoin.bind(this));
    this.on('collaboration:room:leave', this.handleCollaborationRoomLeave.bind(this));
  }

  // Join persona-specific room
  joinPersonaRoom() {
    const $socket = get(socket);
    const $currentPersona = get(currentPersona);
    
    if ($socket && $currentPersona) {
      $socket.emit('join-persona-room', { 
        persona: $currentPersona,
        timestamp: Date.now()
      });
      console.log(`[RealtimeService] Joined room for persona: ${$currentPersona}`);
    }
  }

  // Generic event handler registration
  on(event, handler) {
    const $socket = get(socket);
    if (!$socket) return;

    // Store handler for cleanup
    this.eventHandlers.set(event, handler);
    
    // Register with socket
    $socket.on(event, handler);
  }

  // Generic event handler removal
  off(event) {
    const $socket = get(socket);
    if (!$socket) return;

    const handler = this.eventHandlers.get(event);
    if (handler) {
      $socket.off(event, handler);
      this.eventHandlers.delete(event);
    }
  }

  // Event handlers
  handleAvatarUpdate(data) {
    console.log('[RealtimeService] Avatar update:', data);
    // Additional processing if needed
  }

  handleAvatarAnimationStart(data) {
    console.log('[RealtimeService] Avatar animation started:', data);
  }

  handleAvatarAnimationProgress(data) {
    console.log('[RealtimeService] Avatar animation progress:', data.progress);
  }

  handleAvatarAnimationComplete(data) {
    console.log('[RealtimeService] Avatar animation completed');
  }

  handleMemoryNotification(data) {
    console.log('[RealtimeService] Memory notification:', data);
    // Show notification to user
    this.showNotification(data.title, data.message, 'memory');
  }

  handleMemoryProcessingStart(data) {
    console.log('[RealtimeService] Memory processing started');
  }

  handleMemoryProcessingProgress(data) {
    console.log('[RealtimeService] Memory processing progress:', data.progress);
  }

  handleMemoryProcessingComplete(data) {
    console.log('[RealtimeService] Memory processing completed');
  }

  handleHapticTrigger(data) {
    console.log('[RealtimeService] Haptic trigger:', data);
    // Trigger device vibration
    this.triggerDeviceVibration(data);
  }

  handleHapticStop(data) {
    console.log('[RealtimeService] Haptic stopped');
    // Stop device vibration
    this.stopDeviceVibration();
  }

  handleBiometricUpdate(data) {
    console.log('[RealtimeService] Biometric update:', data);
  }

  handleBiometricConnected(data) {
    console.log('[RealtimeService] Biometric device connected');
  }

  handleBiometricDisconnected(data) {
    console.log('[RealtimeService] Biometric device disconnected');
  }

  handleVRSceneStart(data) {
    console.log('[RealtimeService] VR scene started:', data);
  }

  handleVRSceneProgress(data) {
    console.log('[RealtimeService] VR scene progress:', data.progress);
  }

  handleVRGenerationStart(data) {
    console.log('[RealtimeService] VR generation started');
  }

  handleVRGenerationProgress(data) {
    console.log('[RealtimeService] VR generation progress:', data.progress);
  }

  handleVRGenerationComplete(data) {
    console.log('[RealtimeService] VR generation completed');
  }

  handleVRSceneEnd(data) {
    console.log('[RealtimeService] VR scene ended');
  }

  handleVoiceSpeakStart(data) {
    console.log('[RealtimeService] Voice speaking started:', data);
  }

  handleVoiceSpeakEnd(data) {
    console.log('[RealtimeService] Voice speaking ended');
  }

  handleVoiceListenStart(data) {
    console.log('[RealtimeService] Voice listening started');
  }

  handleVoiceListenEnd(data) {
    console.log('[RealtimeService] Voice listening ended');
  }

  handleRelationshipInsight(data) {
    console.log('[RealtimeService] Relationship insight:', data);
    this.showNotification('Relationship Insight', data.message, 'relationship');
  }

  handleRelationshipHealthUpdate(data) {
    console.log('[RealtimeService] Relationship health update:', data);
  }

  handleRelationshipRecommendation(data) {
    console.log('[RealtimeService] Relationship recommendation:', data);
    this.showNotification('Recommendation', data.title, 'recommendation');
  }

  handleSystemEvent(data) {
    console.log('[RealtimeService] System event:', data);
    this.showNotification(data.title, data.message, data.severity);
  }

  handlePresenceUpdate(data) {
    console.log('[RealtimeService] Presence update:', data);
  }

  handleCollaborationRoomJoin(data) {
    console.log('[RealtimeService] Collaboration room joined:', data);
  }

  handleCollaborationRoomLeave(data) {
    console.log('[RealtimeService] Collaboration room left:', data);
  }

  // Utility methods
  showNotification(title, message, type = 'info') {
    // Use browser notifications if available
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: message,
        icon: '/static/favicon.png',
        tag: type
      });
    }

    // Also show in-app notification
    this.dispatchCustomEvent('notification', {
      title,
      message,
      type,
      timestamp: Date.now()
    });
  }

  triggerDeviceVibration(data) {
    if ('vibrate' in navigator) {
      // Convert pattern to vibration API format
      let pattern;
      if (data.pattern === 'heartbeat') {
        pattern = [100, 100, 100, 100, 100, 100];
      } else if (data.pattern === 'gentle') {
        pattern = [50, 50, 50];
      } else if (data.pattern === 'passionate') {
        pattern = [200, 100, 200, 100, 200];
      } else {
        pattern = data.duration;
      }
      
      navigator.vibrate(pattern);
    }
  }

  stopDeviceVibration() {
    if ('vibrate' in navigator) {
      navigator.vibrate(0);
    }
  }

  dispatchCustomEvent(eventName, data) {
    const event = new CustomEvent(eventName, {
      detail: data,
      bubbles: true
    });
    document.dispatchEvent(event);
  }

  // Public API methods
  async updateAvatarMood(mood) {
    await this.ensureInitialized();
    realtimeActions.updateAvatarMood(mood);
  }

  async triggerAvatarGesture(gesture) {
    await this.ensureInitialized();
    realtimeActions.triggerAvatarGesture(gesture);
  }

  async updateAvatarExpression(expression) {
    await this.ensureInitialized();
    realtimeActions.updateAvatarExpression(expression);
  }

  async triggerHaptic(pattern, intensity = 50, duration = 2000) {
    await this.ensureInitialized();
    realtimeActions.triggerHaptic(pattern, intensity, duration);
  }

  async stopHaptic() {
    await this.ensureInitialized();
    realtimeActions.stopHaptic();
  }

  async startVRScene(sceneId, sceneType = 'pre_created') {
    await this.ensureInitialized();
    realtimeActions.startVRScene(sceneId, sceneType);
  }

  async stopVRScene() {
    await this.ensureInitialized();
    realtimeActions.stopVRScene();
  }

  async speakText(text, emotion = 'neutral', pitch = 1.0, rate = 1.0, volume = 1.0) {
    await this.ensureInitialized();
    realtimeActions.speakText(text, emotion, pitch, rate, volume);
  }

  async stopSpeaking() {
    await this.ensureInitialized();
    realtimeActions.stopSpeaking();
  }

  async startListening() {
    await this.ensureInitialized();
    realtimeActions.startListening();
  }

  async stopListening() {
    await this.ensureInitialized();
    realtimeActions.stopListening();
  }

  // Ensure service is initialized
  async ensureInitialized() {
    if (!this.isInitialized) {
      await this.initialize();
    }
  }

  // Cleanup
  destroy() {
    // Remove all event handlers
    for (const [event] of this.eventHandlers) {
      this.off(event);
    }
    
    this.eventHandlers.clear();
    this.isInitialized = false;
    
    console.log('[RealtimeService] Destroyed');
  }
}

// Helper function to get store value
function get(store) {
  let value;
  store.subscribe(v => value = v)();
  return value;
}

// Create singleton instance
const realtimeService = new RealtimeService();

// Export singleton instance
export default realtimeService;

// Export class for testing
export { RealtimeService }; 