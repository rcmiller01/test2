package com.miasolene.app.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.miasolene.app.api.APIClient
import com.miasolene.app.api.APIResponse
import kotlinx.coroutines.launch
import android.util.Log

class MainViewModel : ViewModel() {
    
    private val _connectionStatus = MutableLiveData<String>("Disconnected")
    val connectionStatus: LiveData<String> = _connectionStatus
    
    private val _errorMessage = MutableLiveData<String>("")
    val errorMessage: LiveData<String> = _errorMessage
    
    private val _ttsResult = MutableLiveData<String>("")
    val ttsResult: LiveData<String> = _ttsResult
    
    private val _avatarResult = MutableLiveData<String>("")
    val avatarResult: LiveData<String> = _avatarResult
    
    private val _memoryResult = MutableLiveData<String>("")
    val memoryResult: LiveData<String> = _memoryResult
    
    companion object {
        private const val TAG = "MainViewModel"
    }
    
    fun testConnection(apiClient: APIClient) {
        viewModelScope.launch {
            try {
                _connectionStatus.value = "Testing connection..."
                
                val response = apiClient.healthCheck()
                
                if (response.success) {
                    _connectionStatus.value = "Connected - All systems operational"
                    _errorMessage.value = ""
                } else {
                    _connectionStatus.value = "Connection failed"
                    _errorMessage.value = response.error ?: "Unknown error"
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Connection test failed", e)
                _connectionStatus.value = "Connection error"
                _errorMessage.value = "Connection failed: ${e.message}"
            }
        }
    }
    
    fun testTTS(apiClient: APIClient, text: String, persona: String, emotion: String, intensity: Float) {
        viewModelScope.launch {
            try {
                _ttsResult.value = "Synthesizing speech..."
                
                val response = apiClient.synthesizeSpeech(text, persona, emotion, intensity)
                
                if (response.success) {
                    val audioData = response.data?.optString("audio_data")
                    if (!audioData.isNullOrEmpty()) {
                        _ttsResult.value = "Speech synthesized successfully! Audio data received."
                        // TODO: Play audio data
                    } else {
                        _ttsResult.value = "Speech synthesis completed but no audio data received."
                    }
                    _errorMessage.value = ""
                } else {
                    _ttsResult.value = "TTS synthesis failed"
                    _errorMessage.value = response.error ?: "Unknown TTS error"
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "TTS test failed", e)
                _ttsResult.value = "TTS error"
                _errorMessage.value = "TTS failed: ${e.message}"
            }
        }
    }
    
    fun testAvatar(apiClient: APIClient, emotion: String, intensity: Float) {
        viewModelScope.launch {
            try {
                _avatarResult.value = "Updating avatar mood..."
                
                val response = apiClient.updateAvatarMood(emotion, intensity)
                
                if (response.success) {
                    _avatarResult.value = "Avatar mood updated to $emotion with intensity $intensity"
                    _errorMessage.value = ""
                } else {
                    _avatarResult.value = "Avatar update failed"
                    _errorMessage.value = response.error ?: "Unknown avatar error"
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Avatar test failed", e)
                _avatarResult.value = "Avatar error"
                _errorMessage.value = "Avatar failed: ${e.message}"
            }
        }
    }
    
    fun testMemory(apiClient: APIClient) {
        viewModelScope.launch {
            try {
                _memoryResult.value = "Testing memory system..."
                
                // First, store a test memory
                val storeResponse = apiClient.storeMemory(
                    memoryType = "emotional_moment",
                    title = "Test Memory from Android",
                    description = "This is a test memory created from the Android app",
                    emotionalIntensity = 0.7f,
                    emotions = listOf("love", "excitement"),
                    personasInvolved = listOf("mia"),
                    context = mapOf("source" to "android_app", "test" to true),
                    relationshipImpact = 0.5f,
                    tags = listOf("test", "android", "love")
                )
                
                if (storeResponse.success) {
                    val memoryId = storeResponse.data?.optString("memory_id")
                    _memoryResult.value = "Memory stored successfully! ID: $memoryId"
                    
                    // Then, try to recall memories
                    val recallResponse = apiClient.recallMemories(
                        emotion = "love",
                        limit = 5
                    )
                    
                    if (recallResponse.success) {
                        val memories = recallResponse.data?.optJSONArray("memories")
                        val count = memories?.length() ?: 0
                        _memoryResult.value = "Memory system working! Retrieved $count memories about love."
                    } else {
                        _memoryResult.value = "Memory stored but recall failed"
                        _errorMessage.value = recallResponse.error ?: "Unknown recall error"
                    }
                    
                } else {
                    _memoryResult.value = "Memory storage failed"
                    _errorMessage.value = storeResponse.error ?: "Unknown memory error"
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Memory test failed", e)
                _memoryResult.value = "Memory error"
                _errorMessage.value = "Memory failed: ${e.message}"
            }
        }
    }
    
    fun clearError() {
        _errorMessage.value = ""
    }
} 