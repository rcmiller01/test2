"""
Voice Orchestrator for Enhanced Voice Layer
Manages multiple STT/TTS engines with commercial licensing compliance
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union
from enum import Enum
import json

logger = logging.getLogger(__name__)

class VoiceEngine(Enum):
    """Available voice processing engines"""
    WHISPER_OFFLINE = "whisper_offline"
    OPENAI_STT = "openai_stt"
    AZURE_STT = "azure_stt"
    PIPER_TTS = "piper_tts"
    ELEVENLABS_TTS = "elevenlabs_tts"
    AZURE_TTS = "azure_tts"
    OPENAI_TTS = "openai_tts"

class VoiceProfile:
    """Voice characteristics for persona customization"""
    def __init__(self, 
                 pitch: float = 1.0,
                 speed: float = 1.0,
                 emotion: str = "neutral",
                 voice_id: str = "default",
                 language: str = "en"):
        self.pitch = pitch
        self.speed = speed
        self.emotion = emotion
        self.voice_id = voice_id
        self.language = language

class VoiceOrchestrator:
    """Main orchestrator for voice processing with commercial compliance"""
    
    def __init__(self):
        self.stt_engines = {}
        self.tts_engines = {}
        self.voice_profile = VoiceProfile()
        self.fallback_enabled = True
        
    async def initialize(self):
        """Initialize all available voice engines"""
        logger.info("Initializing Voice Orchestrator...")
        
        # Initialize STT engines
        await self._init_stt_engines()
        
        # Initialize TTS engines  
        await self._init_tts_engines()
        
        logger.info(f"Voice Orchestrator initialized with {len(self.stt_engines)} STT and {len(self.tts_engines)} TTS engines")
    
    async def _init_stt_engines(self):
        """Initialize Speech-to-Text engines"""
        try:
            # Whisper offline (always available)
            from .whisper_offline import WhisperOfflineSTT
            self.stt_engines[VoiceEngine.WHISPER_OFFLINE] = WhisperOfflineSTT()
            logger.info("✅ Whisper offline STT initialized")
        except ImportError:
            logger.warning("⚠️ Whisper offline STT not available")
        
        try:
            # OpenAI STT (if API key available)
            from .openai_stt import OpenAISTT
            self.stt_engines[VoiceEngine.OPENAI_STT] = OpenAISTT()
            logger.info("✅ OpenAI STT initialized")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI STT not available: {e}")
        
        try:
            # Azure STT (if configured)
            from .azure_stt import AzureSTT
            self.stt_engines[VoiceEngine.AZURE_STT] = AzureSTT()
            logger.info("✅ Azure STT initialized")
        except Exception as e:
            logger.warning(f"⚠️ Azure STT not available: {e}")
    
    async def _init_tts_engines(self):
        """Initialize Text-to-Speech engines"""
        try:
            # Piper TTS (offline, always available)
            from .piper_tts_local import PiperTTSLocal
            self.tts_engines[VoiceEngine.PIPER_TTS] = PiperTTSLocal()
            logger.info("✅ Piper TTS initialized")
        except ImportError:
            logger.warning("⚠️ Piper TTS not available")
        
        try:
            # ElevenLabs TTS (premium)
            from .elevenlabs_tts import ElevenLabsTTS
            self.tts_engines[VoiceEngine.ELEVENLABS_TTS] = ElevenLabsTTS()
            logger.info("✅ ElevenLabs TTS initialized")
        except Exception as e:
            logger.warning(f"⚠️ ElevenLabs TTS not available: {e}")
        
        try:
            # Azure TTS (enterprise)
            from .azure_tts import AzureTTS
            self.tts_engines[VoiceEngine.AZURE_TTS] = AzureTTS()
            logger.info("✅ Azure TTS initialized")
        except Exception as e:
            logger.warning(f"⚠️ Azure TTS not available: {e}")
        
        try:
            # OpenAI TTS
            from .openai_tts import OpenAITTS
            self.tts_engines[VoiceEngine.OPENAI_TTS] = OpenAITTS()
            logger.info("✅ OpenAI TTS initialized")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI TTS not available: {e}")
    
    async def transcribe_audio(self, 
                             audio_data: bytes, 
                             preferred_engine: Optional[VoiceEngine] = None) -> str:
        """
        Transcribe audio to text using available STT engines
        
        Args:
            audio_data: Raw audio bytes
            preferred_engine: Preferred STT engine, falls back if unavailable
            
        Returns:
            Transcribed text
        """
        # Determine engine priority
        engines_to_try = []
        
        if preferred_engine and preferred_engine in self.stt_engines:
            engines_to_try.append(preferred_engine)
        
        # Add fallback engines in priority order
        fallback_order = [
            VoiceEngine.WHISPER_OFFLINE,  # Privacy-focused
            VoiceEngine.OPENAI_STT,       # Quality
            VoiceEngine.AZURE_STT         # Enterprise
        ]
        
        for engine in fallback_order:
            if engine in self.stt_engines and engine not in engines_to_try:
                engines_to_try.append(engine)
        
        # Try each engine
        for engine in engines_to_try:
            try:
                logger.info(f"Attempting transcription with {engine.value}")
                result = await self.stt_engines[engine].transcribe(audio_data)
                if result and result.strip():
                    logger.info(f"✅ Transcription successful with {engine.value}")
                    return result.strip()
            except Exception as e:
                logger.warning(f"⚠️ Transcription failed with {engine.value}: {e}")
                continue
        
        raise Exception("All STT engines failed")
    
    async def synthesize_speech(self, 
                              text: str, 
                              emotion: str = "neutral",
                              preferred_engine: Optional[VoiceEngine] = None) -> bytes:
        """
        Synthesize text to speech using available TTS engines
        
        Args:
            text: Text to synthesize
            emotion: Emotional tone (neutral, happy, sad, excited, etc.)
            preferred_engine: Preferred TTS engine, falls back if unavailable
            
        Returns:
            Audio bytes
        """
        # Apply emotional modulation to voice profile
        modulated_profile = self._apply_emotional_modulation(emotion)
        
        # Determine engine priority based on quality and availability
        engines_to_try = []
        
        if preferred_engine and preferred_engine in self.tts_engines:
            engines_to_try.append(preferred_engine)
        
        # Add fallback engines in quality order
        fallback_order = [
            VoiceEngine.ELEVENLABS_TTS,  # Highest quality
            VoiceEngine.OPENAI_TTS,      # Good quality
            VoiceEngine.AZURE_TTS,       # Enterprise
            VoiceEngine.PIPER_TTS        # Offline fallback
        ]
        
        for engine in fallback_order:
            if engine in self.tts_engines and engine not in engines_to_try:
                engines_to_try.append(engine)
        
        # Try each engine
        for engine in engines_to_try:
            try:
                logger.info(f"Attempting synthesis with {engine.value}")
                result = await self.tts_engines[engine].synthesize(text, modulated_profile)
                if result:
                    logger.info(f"✅ Synthesis successful with {engine.value}")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Synthesis failed with {engine.value}: {e}")
                continue
        
        raise Exception("All TTS engines failed")
    
    def _apply_emotional_modulation(self, emotion: str) -> VoiceProfile:
        """Apply emotional modulation to voice profile"""
        modulated = VoiceProfile(
            pitch=self.voice_profile.pitch,
            speed=self.voice_profile.speed,
            emotion=emotion,
            voice_id=self.voice_profile.voice_id,
            language=self.voice_profile.language
        )
        
        # Emotional modulations
        emotion_mods = {
            "happy": {"pitch": 1.1, "speed": 1.05},
            "excited": {"pitch": 1.15, "speed": 1.1},
            "sad": {"pitch": 0.9, "speed": 0.95},
            "calm": {"pitch": 0.95, "speed": 0.9},
            "romantic": {"pitch": 0.98, "speed": 0.92},
            "playful": {"pitch": 1.08, "speed": 1.03}
        }
        
        if emotion in emotion_mods:
            mods = emotion_mods[emotion]
            modulated.pitch *= mods.get("pitch", 1.0)
            modulated.speed *= mods.get("speed", 1.0)
        
        return modulated
    
    def update_voice_profile(self, 
                           pitch: Optional[float] = None,
                           speed: Optional[float] = None,
                           voice_id: Optional[str] = None,
                           language: Optional[str] = None):
        """Update the persona voice profile"""
        if pitch is not None:
            self.voice_profile.pitch = max(0.5, min(2.0, pitch))
        if speed is not None:
            self.voice_profile.speed = max(0.5, min(2.0, speed))
        if voice_id is not None:
            self.voice_profile.voice_id = voice_id
        if language is not None:
            self.voice_profile.language = language
        
        logger.info(f"Voice profile updated: {self.voice_profile.__dict__}")
    
    def get_available_engines(self) -> Dict[str, List[str]]:
        """Get list of available voice engines"""
        return {
            "stt": [engine.value for engine in self.stt_engines.keys()],
            "tts": [engine.value for engine in self.tts_engines.keys()]
        }
    
    def get_voice_profile(self) -> Dict:
        """Get current voice profile"""
        return {
            "pitch": self.voice_profile.pitch,
            "speed": self.voice_profile.speed,
            "emotion": self.voice_profile.emotion,
            "voice_id": self.voice_profile.voice_id,
            "language": self.voice_profile.language
        }

# Global instance
voice_orchestrator = VoiceOrchestrator()
