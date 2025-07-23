package com.miasolene.app

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.miasolene.app.viewmodel.MainViewModel
import com.miasolene.app.api.APIClient
import com.miasolene.app.api.APIConfig

class MainActivity : AppCompatActivity() {
    
    private lateinit var viewModel: MainViewModel
    private lateinit var apiClient: APIClient
    
    private lateinit var statusText: TextView
    private lateinit var connectButton: Button
    private lateinit var testTTSButton: Button
    private lateinit var testAvatarButton: Button
    private lateinit var testMemoryButton: Button
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize API client
        val config = APIConfig(
            baseUrl = "http://10.0.2.2:8000", // Android emulator localhost
            timeout = 30,
            retryAttempts = 3
        )
        apiClient = APIClient(config)
        
        // Initialize ViewModel
        viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        
        // Initialize UI components
        initializeUI()
        
        // Observe ViewModel data
        observeViewModel()
        
        // Test connection on startup
        testConnection()
    }
    
    private fun initializeUI() {
        statusText = findViewById(R.id.statusText)
        connectButton = findViewById(R.id.connectButton)
        testTTSButton = findViewById(R.id.testTTSButton)
        testAvatarButton = findViewById(R.id.testAvatarButton)
        testMemoryButton = findViewById(R.id.testMemoryButton)
        
        connectButton.setOnClickListener {
            testConnection()
        }
        
        testTTSButton.setOnClickListener {
            testTTS()
        }
        
        testAvatarButton.setOnClickListener {
            testAvatar()
        }
        
        testMemoryButton.setOnClickListener {
            testMemory()
        }
    }
    
    private fun observeViewModel() {
        viewModel.connectionStatus.observe(this) { status ->
            statusText.text = "Status: $status"
        }
        
        viewModel.errorMessage.observe(this) { message ->
            if (message.isNotEmpty()) {
                Toast.makeText(this, message, Toast.LENGTH_LONG).show()
            }
        }
    }
    
    private fun testConnection() {
        viewModel.testConnection(apiClient)
    }
    
    private fun testTTS() {
        viewModel.testTTS(apiClient, "Hello, I love you", "mia", "love", 0.8f)
    }
    
    private fun testAvatar() {
        viewModel.testAvatar(apiClient, "love", 0.8f)
    }
    
    private fun testMemory() {
        viewModel.testMemory(apiClient)
    }
} 