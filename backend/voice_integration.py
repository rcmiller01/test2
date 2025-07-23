"""
Integration script for Enhanced Voice Layer
Adds voice processing capabilities to the existing system
"""

import logging
from fastapi import FastAPI

logger = logging.getLogger(__name__)

def integrate_voice_layer(app: FastAPI):
    """
    Integrate enhanced voice layer into the main application
    
    Args:
        app: FastAPI application instance
    """
    try:
        # Import voice router
        from .routes.voice_routes import voice_router
        
        # Include voice router
        app.include_router(voice_router)
        
        logger.info("✅ Enhanced Voice Layer integrated successfully")
        
        # Log available voice endpoints
        voice_endpoints = [
            "/api/voice/stt/transcribe",
            "/api/voice/tts/synthesize", 
            "/api/voice/engines/available",
            "/api/voice/persona/configure",
            "/api/voice/persona/profile",
            "/api/voice/emotions/available",
            "/api/voice/test/quality"
        ]
        
        logger.info(f"🎤 Voice endpoints available: {', '.join(voice_endpoints)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to integrate voice layer: {e}")
        return False

def setup_voice_dependencies():
    """
    Setup voice processing dependencies
    
    Returns:
        dict: Installation commands for required packages
    """
    dependencies = {
        "core_voice": [
            "pip install whisper",
            "pip install openai-whisper",
            "pip install piper-tts"
        ],
        "premium_apis": [
            "pip install elevenlabs",
            "pip install azure-cognitiveservices-speech"
        ],
        "audio_processing": [
            "pip install pyaudio",
            "pip install soundfile",
            "pip install librosa",
            "pip install webrtcvad"
        ],
        "system_dependencies": [
            "# For Whisper.cpp (optional):",
            "# Download from: https://github.com/ggerganov/whisper.cpp",
            "# For Piper (optional):",
            "# Download from: https://github.com/rhasspy/piper"
        ]
    }
    
    return dependencies

def get_voice_configuration_template():
    """
    Get configuration template for voice settings
    
    Returns:
        dict: Configuration template
    """
    config = {
        "voice_settings": {
            "default_stt_engine": "whisper_offline",
            "default_tts_engine": "piper_tts",
            "fallback_enabled": True,
            "offline_priority": True
        },
        "engines": {
            "whisper_offline": {
                "model_size": "base",
                "enabled": True
            },
            "openai_stt": {
                "api_key": "${OPENAI_API_KEY}",
                "enabled": False
            },
            "azure_stt": {
                "api_key": "${AZURE_SPEECH_KEY}",
                "region": "${AZURE_SPEECH_REGION}",
                "enabled": False
            },
            "piper_tts": {
                "model": "en_US-ljspeech-medium",
                "enabled": True
            },
            "elevenlabs_tts": {
                "api_key": "${ELEVENLABS_API_KEY}",
                "enabled": False
            },
            "azure_tts": {
                "api_key": "${AZURE_SPEECH_KEY}",
                "region": "${AZURE_SPEECH_REGION}",
                "enabled": False
            }
        },
        "persona_voice": {
            "pitch": 1.0,
            "speed": 1.0,
            "voice_id": "default",
            "language": "en"
        }
    }
    
    return config

if __name__ == "__main__":
    # Print setup instructions
    print("🎤 Enhanced Voice Layer Setup")
    print("=" * 50)
    
    deps = setup_voice_dependencies()
    
    print("📦 Required Dependencies:")
    for category, commands in deps.items():
        print(f"\n{category.upper()}:")
        for cmd in commands:
            print(f"  {cmd}")
    
    print("\n🔧 Configuration:")
    config = get_voice_configuration_template()
    import json
    print(json.dumps(config, indent=2))
    
    print("\n✅ Next Steps:")
    print("1. Install dependencies listed above")
    print("2. Add configuration to your settings")
    print("3. Set environment variables for API keys")
    print("4. Call integrate_voice_layer(app) in your main.py")
    print("5. Test voice endpoints at /api/voice/*")
