"""
ElevenLabs TTS Engine
Commercial-grade text-to-speech using ElevenLabs API
"""

import asyncio
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

class ElevenLabsTTS:
    """ElevenLabs TTS engine for high-quality commercial voice synthesis"""
    
    def __init__(self):
        self.api_key = None
        self.client = None
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        self.initialized = False
        
    async def initialize(self):
        """Initialize ElevenLabs TTS engine"""
        try:
            # Get API key from environment
            self.api_key = os.getenv("ELEVENLABS_API_KEY")
            
            if not self.api_key:
                raise Exception("ELEVENLABS_API_KEY not found in environment")
            
            # Import and initialize ElevenLabs client
            try:
                from elevenlabs import VoiceSettings, generate, set_api_key
                set_api_key(self.api_key)
                self.generate_func = generate
                self.VoiceSettings = VoiceSettings
                
                # Test API connection
                voices = await self.get_available_voices()
                logger.info(f"✅ ElevenLabs TTS initialized with {len(voices)} voices")
                
            except ImportError:
                raise Exception("elevenlabs package not installed")
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ElevenLabs TTS: {e}")
            raise e
    
    async def synthesize(self, text: str, voice_profile) -> bytes:
        """
        Synthesize text to speech using ElevenLabs
        
        Args:
            text: Text to synthesize
            voice_profile: Voice characteristics
            
        Returns:
            Audio bytes (MP3 format)
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get voice ID from profile or use default
            voice_id = getattr(voice_profile, 'voice_id', self.default_voice_id)
            
            # Map emotions to ElevenLabs voice settings
            emotion_settings = self._get_emotion_settings(voice_profile.emotion)
            
            # Apply voice modulation
            voice_settings = self.VoiceSettings(
                stability=emotion_settings['stability'],
                similarity_boost=emotion_settings['similarity_boost'],
                style=emotion_settings.get('style', 0.0),
                use_speaker_boost=True
            )
            
            # Generate audio in thread pool
            loop = asyncio.get_event_loop()
            audio_data = await loop.run_in_executor(
                None,
                lambda: self.generate_func(
                    text=text,
                    voice=voice_id,
                    voice_settings=voice_settings,
                    model="eleven_multilingual_v2"
                )
            )
            
            # Convert generator to bytes if needed
            if hasattr(audio_data, '__iter__'):
                audio_bytes = b''.join(audio_data)
            else:
                audio_bytes = audio_data
                
            return audio_bytes
            
        except Exception as e:
            logger.error(f"❌ ElevenLabs synthesis failed: {e}")
            raise e
    
    def _get_emotion_settings(self, emotion: str) -> dict:
        """Get ElevenLabs voice settings for emotions"""
        emotion_map = {
            "neutral": {
                "stability": 0.7,
                "similarity_boost": 0.8,
                "style": 0.0
            },
            "happy": {
                "stability": 0.6,
                "similarity_boost": 0.9,
                "style": 0.3
            },
            "excited": {
                "stability": 0.5,
                "similarity_boost": 0.9,
                "style": 0.5
            },
            "sad": {
                "stability": 0.8,
                "similarity_boost": 0.7,
                "style": 0.2
            },
            "calm": {
                "stability": 0.9,
                "similarity_boost": 0.8,
                "style": 0.1
            },
            "romantic": {
                "stability": 0.8,
                "similarity_boost": 0.9,
                "style": 0.4
            },
            "playful": {
                "stability": 0.6,
                "similarity_boost": 0.9,
                "style": 0.6
            }
        }
        
        return emotion_map.get(emotion, emotion_map["neutral"])
    
    async def get_available_voices(self) -> list:
        """Get available ElevenLabs voices"""
        try:
            from elevenlabs import voices
            
            loop = asyncio.get_event_loop()
            voice_list = await loop.run_in_executor(None, voices)
            
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                    "description": voice.description
                }
                for voice in voice_list
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to get ElevenLabs voices: {e}")
            return []
    
    def get_supported_emotions(self) -> list:
        """Get supported emotional modulations"""
        return ["neutral", "happy", "excited", "sad", "calm", "romantic", "playful"]
    
    def get_engine_info(self) -> dict:
        """Get engine information"""
        return {
            "engine": "elevenlabs_tts",
            "api_key_configured": bool(self.api_key),
            "default_voice": self.default_voice_id,
            "privacy": "cloud_api",
            "commercial": "licensed",
            "quality": "premium"
        }
