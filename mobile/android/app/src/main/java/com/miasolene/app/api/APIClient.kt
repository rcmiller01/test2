package com.miasolene.app.api

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

data class APIConfig(
    val baseUrl: String,
    val timeout: Int = 30,
    val retryAttempts: Int = 3
)

data class APIResponse(
    val success: Boolean,
    val data: JSONObject? = null,
    val message: String = "",
    val error: String? = null
)

class APIClient(private val config: APIConfig) {
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(config.timeout.toLong(), TimeUnit.SECONDS)
        .readTimeout(config.timeout.toLong(), TimeUnit.SECONDS)
        .writeTimeout(config.timeout.toLong(), TimeUnit.SECONDS)
        .build()
    
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()
    
    companion object {
        private const val TAG = "APIClient"
    }
    
    suspend fun makeRequest(
        method: String,
        endpoint: String,
        data: JSONObject? = null,
        params: Map<String, String>? = null
    ): APIResponse = withContext(Dispatchers.IO) {
        
        var lastException: Exception? = null
        
        for (attempt in 0 until config.retryAttempts) {
            try {
                val url = buildUrl(endpoint, params)
                val request = buildRequest(method, url, data)
                
                val response = client.newCall(request).execute()
                
                if (response.isSuccessful) {
                    val responseBody = response.body?.string()
                    return@withContext parseResponse(responseBody)
                } else {
                    return@withContext APIResponse(
                        success = false,
                        error = "HTTP ${response.code}: ${response.message}"
                    )
                }
                
            } catch (e: Exception) {
                lastException = e
                Log.w(TAG, "API request attempt ${attempt + 1} failed: ${e.message}")
                
                if (attempt == config.retryAttempts - 1) {
                    return@withContext APIResponse(
                        success = false,
                        error = "Request failed after ${config.retryAttempts} attempts: ${e.message}"
                    )
                }
            }
        }
        
        APIResponse(
            success = false,
            error = "Unknown error occurred"
        )
    }
    
    private fun buildUrl(endpoint: String, params: Map<String, String>?): String {
        val urlBuilder = StringBuilder(config.baseUrl).append(endpoint)
        
        if (!params.isNullOrEmpty()) {
            urlBuilder.append("?")
            params.forEach { (key, value) ->
                urlBuilder.append("$key=$value&")
            }
            urlBuilder.deleteCharAt(urlBuilder.length - 1) // Remove last &
        }
        
        return urlBuilder.toString()
    }
    
    private fun buildRequest(method: String, url: String, data: JSONObject?): Request {
        val requestBuilder = Request.Builder().url(url)
        
        when (method.uppercase()) {
            "GET" -> requestBuilder.get()
            "POST" -> {
                val body = data?.toString()?.toRequestBody(jsonMediaType)
                requestBuilder.post(body ?: "{}".toRequestBody(jsonMediaType))
            }
            else -> throw IllegalArgumentException("Unsupported HTTP method: $method")
        }
        
        return requestBuilder
            .addHeader("Content-Type", "application/json")
            .addHeader("User-Agent", "MiaSolene-Android/1.0")
            .build()
    }
    
    private fun parseResponse(responseBody: String?): APIResponse {
        return try {
            if (responseBody.isNullOrEmpty()) {
                APIResponse(success = false, error = "Empty response")
            } else {
                val json = JSONObject(responseBody)
                APIResponse(
                    success = json.optBoolean("success", false),
                    data = json,
                    message = json.optString("message", ""),
                    error = if (json.has("error")) json.getString("error") else null
                )
            }
        } catch (e: Exception) {
            APIResponse(success = false, error = "Failed to parse response: ${e.message}")
        }
    }
    
    // Core API Methods
    
    suspend fun getEmotionState(): APIResponse {
        return makeRequest("GET", "/emotion/state")
    }
    
    suspend fun updateEmotionFromText(text: String): APIResponse {
        val data = JSONObject().apply {
            put("text", text)
        }
        return makeRequest("POST", "/emotion/from_text", data)
    }
    
    suspend fun getMiaSelfTalk(): APIResponse {
        return makeRequest("GET", "/mia/self_talk")
    }
    
    // Advanced Features API Methods
    
    suspend fun synthesizeSpeech(
        text: String,
        persona: String = "mia",
        emotion: String = "neutral",
        intensity: Float = 0.5f
    ): APIResponse {
        val data = JSONObject().apply {
            put("text", text)
            put("persona", persona)
            put("emotion", emotion)
            put("intensity", intensity)
        }
        return makeRequest("POST", "/api/advanced/tts/synthesize", data)
    }
    
    suspend fun getTTSStatus(): APIResponse {
        return makeRequest("GET", "/api/advanced/tts/status")
    }
    
    suspend fun updateAvatarMood(
        emotion: String,
        intensity: Float = 0.5f,
        context: Map<String, Any>? = null
    ): APIResponse {
        val data = JSONObject().apply {
            put("emotion", emotion)
            put("intensity", intensity)
            if (context != null) {
                put("context", JSONObject(context))
            }
        }
        return makeRequest("POST", "/api/advanced/avatar/mood", data)
    }
    
    suspend fun getAvatarState(): APIResponse {
        return makeRequest("GET", "/api/advanced/avatar/state")
    }
    
    suspend fun storeMemory(
        memoryType: String,
        title: String,
        description: String,
        emotionalIntensity: Float,
        emotions: List<String>,
        personasInvolved: List<String>,
        context: Map<String, Any>? = null,
        relationshipImpact: Float = 0.0f,
        tags: List<String>? = null
    ): APIResponse {
        val data = JSONObject().apply {
            put("memory_type", memoryType)
            put("title", title)
            put("description", description)
            put("emotional_intensity", emotionalIntensity)
            put("emotions", JSONObject().apply {
                emotions.forEachIndexed { index, emotion ->
                    put("$index", emotion)
                }
            })
            put("personas_involved", JSONObject().apply {
                personasInvolved.forEachIndexed { index, persona ->
                    put("$index", persona)
                }
            })
            if (context != null) {
                put("context", JSONObject(context))
            }
            put("relationship_impact", relationshipImpact)
            if (tags != null) {
                put("tags", JSONObject().apply {
                    tags.forEachIndexed { index, tag ->
                        put("$index", tag)
                    }
                })
            }
        }
        return makeRequest("POST", "/api/advanced/memory/store", data)
    }
    
    suspend fun recallMemories(
        emotion: String? = null,
        persona: String? = null,
        memoryType: String? = null,
        limit: Int = 10
    ): APIResponse {
        val params = mutableMapOf<String, String>()
        params["limit"] = limit.toString()
        emotion?.let { params["emotion"] = it }
        persona?.let { params["persona"] = it }
        memoryType?.let { params["memory_type"] = it }
        
        return makeRequest("GET", "/api/advanced/memory/recall", params = params)
    }
    
    suspend fun getRelationshipInsights(): APIResponse {
        return makeRequest("GET", "/api/advanced/memory/insights")
    }
    
    // Phase 3 Features API Methods
    
    suspend fun triggerHapticFeedback(
        pattern: String,
        intensity: String = "moderate",
        duration: Float = 2.0f,
        location: String = "general",
        emotionalContext: String = "romantic"
    ): APIResponse {
        val data = JSONObject().apply {
            put("pattern", pattern)
            put("intensity", intensity)
            put("duration", duration)
            put("location", location)
            put("emotional_context", emotionalContext)
        }
        return makeRequest("POST", "/api/phase3/haptic/trigger", data)
    }
    
    suspend fun startBiometricMonitoring(): APIResponse {
        return makeRequest("POST", "/api/phase3/biometric/start")
    }
    
    suspend fun getRomanticSyncStatus(): APIResponse {
        return makeRequest("GET", "/api/phase3/biometric/romantic-sync")
    }
    
    // Health Check
    
    suspend fun healthCheck(): APIResponse {
        return makeRequest("GET", "/api/advanced/health")
    }
} 