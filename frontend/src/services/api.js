import axios from 'axios';
import toast from 'react-hot-toast';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add loading indicator
    if (config.showLoading !== false) {
      toast.loading('Loading...', { id: config.url });
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Dismiss loading indicator
    toast.dismiss(response.config.url);
    return response;
  },
  (error) => {
    // Dismiss loading indicator
    toast.dismiss(error.config?.url);
    
    // Show error message
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    toast.error(message);
    
    return Promise.reject(error);
  }
);

// API Service Class
class APIService {
  // Health Check
  async healthCheck() {
    try {
      const response = await api.get('/api/advanced/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      return { success: false, error: error.message };
    }
  }

  // Emotional TTS Methods
  async synthesizeSpeech(text, persona = 'mia', emotion = 'neutral', intensity = 0.5) {
    try {
      const response = await api.post('/api/advanced/tts/synthesize', {
        text,
        persona,
        emotion,
        intensity,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getTTSStatus() {
    try {
      const response = await api.get('/api/advanced/tts/status');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAvailableEmotions() {
    try {
      const response = await api.get('/api/advanced/tts/available_emotions');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Avatar Methods
  async updateAvatarMood(emotion, intensity = 0.5, context = {}) {
    try {
      const response = await api.post('/api/advanced/avatar/mood', {
        emotion,
        intensity,
        context,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async triggerAvatarGesture(gesture, intensity = 0.5) {
    try {
      const response = await api.post(`/api/advanced/avatar/gesture/${gesture}`, null, {
        params: { intensity },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAvatarState() {
    try {
      const response = await api.get('/api/advanced/avatar/state');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async customizeAvatar(customization) {
    try {
      const response = await api.post('/api/advanced/avatar/customize', customization);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAvatarCustomizationOptions() {
    try {
      const response = await api.get('/api/advanced/avatar/customization_options');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAvatarSummary() {
    try {
      const response = await api.get('/api/advanced/avatar/summary');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Memory Methods
  async storeMemory(memoryData) {
    try {
      const response = await api.post('/api/advanced/memory/store', memoryData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async recallMemories(filters = {}) {
    try {
      const response = await api.get('/api/advanced/memory/recall', { params: filters });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getRelationshipInsights() {
    try {
      const response = await api.get('/api/advanced/memory/insights');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getMemorySummary() {
    try {
      const response = await api.get('/api/advanced/memory/summary');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Phase 3 Methods - Haptic
  async triggerHapticFeedback(pattern, intensity = 'moderate', duration = 2.0, location = 'general', emotionalContext = 'romantic') {
    try {
      const response = await api.post('/api/phase3/haptic/trigger', {
        pattern,
        intensity,
        duration,
        location,
        emotional_context: emotionalContext,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async triggerRomanticHaptic(action, intensity = 'moderate') {
    try {
      const response = await api.post('/api/phase3/haptic/romantic', null, {
        params: { action, intensity },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getHapticStatus() {
    try {
      const response = await api.get('/api/phase3/haptic/status');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Phase 3 Methods - Biometric
  async startBiometricMonitoring() {
    try {
      const response = await api.post('/api/phase3/biometric/start');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async updateBiometricReading(type, value, context = 'general') {
    try {
      const response = await api.post('/api/phase3/biometric/reading', {
        type,
        value,
        context,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getRomanticSyncStatus() {
    try {
      const response = await api.get('/api/phase3/biometric/romantic-sync');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Phase 3 Methods - VR
  async startVRSession(sceneType = 'romantic_garden') {
    try {
      const response = await api.post('/api/phase3/vr/start', {
        scene_type: sceneType,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async triggerVRInteraction(interactionType, intensity = 0.5) {
    try {
      const response = await api.post('/api/phase3/vr/interaction', {
        interaction_type: interactionType,
        intensity,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getVRStatus() {
    try {
      const response = await api.get('/api/phase3/vr/status');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAvailableVRScenes() {
    try {
      const response = await api.get('/api/phase3/vr/scenes');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Phase 3 Methods - Relationship AI
  async getRelationshipHealth() {
    try {
      const response = await api.get('/api/phase3/relationship/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getRelationshipAdvice(issueType, context = {}) {
    try {
      const response = await api.post('/api/phase3/relationship/advice', {
        issue_type: issueType,
        context,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getConflictResolution(conflictType, severity, context = {}) {
    try {
      const response = await api.post('/api/phase3/relationship/conflict-resolution', {
        conflict_type: conflictType,
        severity,
        context,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getRelationshipInsights() {
    try {
      const response = await api.get('/api/phase3/relationship/insights');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async trackRelationshipProgress(metric, value) {
    try {
      const response = await api.post('/api/phase3/relationship/track-progress', null, {
        params: { metric, value },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Integrated Experience Methods
  async createRomanticExperience(text, emotion = 'love', intensity = 0.7, options = {}) {
    try {
      const response = await api.post('/api/advanced/integrated/romantic_experience', {
        text,
        emotion,
        intensity,
        include_tts: options.includeTTS !== false,
        include_avatar: options.includeAvatar !== false,
        include_memory: options.includeMemory !== false,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getIntegratedStatus() {
    try {
      const response = await api.get('/api/advanced/integrated/status');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Core API Methods
  async getEmotionState() {
    try {
      const response = await api.get('/emotion/state');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async updateEmotionFromText(text) {
    try {
      const response = await api.post('/emotion/from_text', { text });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async updateEmotionFromBiometrics(bpm, hrv, context = 'general') {
    try {
      const response = await api.post('/emotion/from_biometrics', {
        bpm,
        hrv,
        context,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getMiaSelfTalk() {
    try {
      const response = await api.get('/mia/self_talk');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async recallEmotionalMemory(emotion = null, limit = 5) {
    try {
      const params = { limit };
      if (emotion) params.emotion = emotion;
      const response = await api.get('/mia/self_talk/recall', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Utility Methods
  async testConnection() {
    try {
      const response = await this.healthCheck();
      if (response.success) {
        toast.success('Connected to Mia & Solene API');
        return true;
      } else {
        toast.error('Failed to connect to API');
        return false;
      }
    } catch (error) {
      toast.error('Connection failed');
      return false;
    }
  }

  // Audio playback utility
  playAudioFromBase64(base64Audio) {
    try {
      const audioData = atob(base64Audio);
      const arrayBuffer = new ArrayBuffer(audioData.length);
      const view = new Uint8Array(arrayBuffer);
      for (let i = 0; i < audioData.length; i++) {
        view[i] = audioData.charCodeAt(i);
      }
      
      const blob = new Blob([arrayBuffer], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      
      audio.play().catch(error => {
        console.error('Audio playback failed:', error);
        toast.error('Failed to play audio');
      });
      
      // Clean up URL after playing
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };
    } catch (error) {
      console.error('Audio processing failed:', error);
      toast.error('Failed to process audio');
    }
  }
}

// Create and export singleton instance
const apiService = new APIService();
export default apiService;

// Export individual methods for convenience
export const {
  healthCheck,
  synthesizeSpeech,
  getTTSStatus,
  getAvailableEmotions,
  updateAvatarMood,
  triggerAvatarGesture,
  getAvatarState,
  customizeAvatar,
  getAvatarCustomizationOptions,
  getAvatarSummary,
  storeMemory,
  recallMemories,
  getRelationshipInsights,
  getMemorySummary,
  triggerHapticFeedback,
  triggerRomanticHaptic,
  getHapticStatus,
  startBiometricMonitoring,
  updateBiometricReading,
  getRomanticSyncStatus,
  startVRSession,
  triggerVRInteraction,
  getVRStatus,
  getAvailableVRScenes,
  getRelationshipHealth,
  getRelationshipAdvice,
  getConflictResolution,
  trackRelationshipProgress,
  createRomanticExperience,
  getIntegratedStatus,
  getEmotionState,
  updateEmotionFromText,
  updateEmotionFromBiometrics,
  getMiaSelfTalk,
  recallEmotionalMemory,
  testConnection,
  playAudioFromBase64,
} = apiService; 