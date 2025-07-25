"""
Voice Synthesis Implementation for EmotionalAI Companion
Supports ElevenLabs API with emotional voice modulation and fallback options
"""

import aiohttp
import asyncio
import json
import os
from typing import Dict, Optional, Any
from datetime import datetime
import base64

class VoiceSynthesizer:
    """Voice synthesis with emotional modulation"""
    
    def __init__(self):
        self.config = self._load_voice_config()
        self.session: Optional[aiohttp.ClientSession] = None
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        
    def _load_voice_config(self) -> Dict[str, Any]:
        """Load voice configuration from JSON file"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "voice_config.json")
        try:
            with open(config_path, 'r') as f:
                return json.load(f)["voice_config"]
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default voice configuration"""
        return {
            "default_voice": {
                "provider": "elevenlabs",
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "stability": 0.5,
                "similarity_boost": 0.5
            },
            "emotional_voice_mapping": {
                "neutral": {"stability": 0.5, "similarity_boost": 0.5},
                "caring": {"stability": 0.7, "similarity_boost": 0.6},
                "romantic": {"stability": 0.8, "similarity_boost": 0.8}
            }
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            headers = {
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key or "demo"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def synthesize_speech(self, text: str, emotion: str = "neutral") -> Dict[str, Any]:
        """Synthesize speech with emotional modulation"""
        try:
            if self.elevenlabs_api_key:
                return await self._synthesize_elevenlabs(text, emotion)
            else:
                return await self._synthesize_fallback(text, emotion)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_text": text,
                "timestamp": datetime.now()
            }
    
    async def _synthesize_elevenlabs(self, text: str, emotion: str) -> Dict[str, Any]:
        """Synthesize using ElevenLabs API"""
        session = await self._get_session()
        
        # Get emotional voice settings
        voice_settings = self.config["emotional_voice_mapping"].get(
            emotion, 
            self.config["default_voice"]
        )
        
        voice_id = self.config["default_voice"]["voice_id"]
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": voice_settings.get("stability", 0.5),
                "similarity_boost": voice_settings.get("similarity_boost", 0.5),
                "style": voice_settings.get("style", 0.0),
                "use_speaker_boost": True
            }
        }
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                audio_data = await response.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                return {
                    "success": True,
                    "audio_data": audio_base64,
                    "format": "mp3",
                    "emotion": emotion,
                    "provider": "elevenlabs",
                    "timestamp": datetime.now()
                }
            else:
                error_text = await response.text()
                return await self._synthesize_fallback(text, emotion, f"ElevenLabs error: {error_text}")
    
    async def _synthesize_fallback(self, text: str, emotion: str, error_reason: Optional[str] = None) -> Dict[str, Any]:
        """Fallback synthesis method"""
        return {
            "success": True,
            "fallback": True,
            "text": text,
            "emotion": emotion,
            "provider": "browser_speech",
            "instructions": "Use browser speech synthesis",
            "error_reason": error_reason,
            "timestamp": datetime.now()
        }
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global instance
voice_synthesizer = VoiceSynthesizer()
