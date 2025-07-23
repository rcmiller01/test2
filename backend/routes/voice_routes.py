"""
Voice API Routes for Enhanced Voice Layer
Provides STT/TTS endpoints with commercial-grade voice processing
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from typing import Optional
import logging
import json

from ..modules.voice.voice_orchestrator import voice_orchestrator, VoiceEngine

logger = logging.getLogger(__name__)

# Create voice router
voice_router = APIRouter(prefix="/api/voice", tags=["voice"])

@voice_router.on_event("startup")
async def initialize_voice_system():
    """Initialize voice orchestrator on startup"""
    try:
        await voice_orchestrator.initialize()
        logger.info("🎤 Voice system initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize voice system: {e}")

@voice_router.post("/stt/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    engine: Optional[str] = Form(None),
    language: Optional[str] = Form("en")
):
    """
    Transcribe audio to text using multiple STT engines
    
    Args:
        audio: Audio file (WAV, MP3, M4A, OGG, FLAC)
        engine: Preferred STT engine (whisper_offline, openai_stt, azure_stt)
        language: Language code (en, es, fr, de, etc.)
        
    Returns:
        JSON with transcribed text and metadata
    """
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Parse engine preference
        preferred_engine = None
        if engine:
            try:
                preferred_engine = VoiceEngine(engine)
            except ValueError:
                logger.warning(f"Unknown engine '{engine}', using auto-select")
        
        # Transcribe audio
        text = await voice_orchestrator.transcribe_audio(
            audio_data=audio_data,
            preferred_engine=preferred_engine
        )
        
        return {
            "success": True,
            "text": text,
            "language": language,
            "engine_used": engine,
            "confidence": 0.95  # Would come from actual engine in production
        }
        
    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@voice_router.post("/tts/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    emotion: str = Form("neutral"),
    engine: Optional[str] = Form(None),
    voice_id: Optional[str] = Form(None),
    language: str = Form("en")
):
    """
    Synthesize text to speech with emotional modulation
    
    Args:
        text: Text to synthesize
        emotion: Emotion (neutral, happy, sad, excited, calm, romantic, playful)
        engine: Preferred TTS engine (piper_tts, elevenlabs_tts, azure_tts, openai_tts)
        voice_id: Specific voice ID for the engine
        language: Language code
        
    Returns:
        Audio file (WAV/MP3)
    """
    try:
        # Parse engine preference
        preferred_engine = None
        if engine:
            try:
                preferred_engine = VoiceEngine(engine)
            except ValueError:
                logger.warning(f"Unknown engine '{engine}', using auto-select")
        
        # Update voice profile if voice_id provided
        if voice_id:
            voice_orchestrator.update_voice_profile(voice_id=voice_id, language=language)
        
        # Synthesize speech
        audio_data = await voice_orchestrator.synthesize_speech(
            text=text,
            emotion=emotion,
            preferred_engine=preferred_engine
        )
        
        # Determine content type based on engine used
        content_type = "audio/wav"  # Default
        if preferred_engine == VoiceEngine.ELEVENLABS_TTS:
            content_type = "audio/mpeg"
        
        return Response(
            content=audio_data,
            media_type=content_type,
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Speech synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@voice_router.get("/engines/available")
async def get_available_engines():
    """
    Get list of available voice engines
    
    Returns:
        JSON with available STT and TTS engines
    """
    try:
        engines = voice_orchestrator.get_available_engines()
        
        return {
            "success": True,
            "engines": engines,
            "total_stt": len(engines["stt"]),
            "total_tts": len(engines["tts"])
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get engines: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@voice_router.post("/persona/configure")
async def configure_persona_voice(
    pitch: Optional[float] = Form(None),
    speed: Optional[float] = Form(None),
    voice_id: Optional[str] = Form(None),
    language: Optional[str] = Form(None)
):
    """
    Configure persona voice profile
    
    Args:
        pitch: Voice pitch (0.5-2.0, 1.0 = normal)
        speed: Speech speed (0.5-2.0, 1.0 = normal)
        voice_id: Voice identifier for TTS engines
        language: Language code (en, es, fr, de, etc.)
        
    Returns:
        Updated voice profile
    """
    try:
        # Update voice profile
        voice_orchestrator.update_voice_profile(
            pitch=pitch,
            speed=speed,
            voice_id=voice_id,
            language=language
        )
        
        # Get updated profile
        profile = voice_orchestrator.get_voice_profile()
        
        return {
            "success": True,
            "voice_profile": profile,
            "message": "Voice profile updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to configure voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@voice_router.get("/persona/profile")
async def get_persona_voice_profile():
    """
    Get current persona voice profile
    
    Returns:
        Current voice configuration
    """
    try:
        profile = voice_orchestrator.get_voice_profile()
        
        return {
            "success": True,
            "voice_profile": profile
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get voice profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@voice_router.get("/emotions/available")
async def get_available_emotions():
    """
    Get list of available emotional modulations
    
    Returns:
        List of supported emotions
    """
    emotions = [
        {
            "id": "neutral",
            "name": "Neutral",
            "description": "Standard voice tone"
        },
        {
            "id": "happy",
            "name": "Happy",
            "description": "Upbeat and cheerful"
        },
        {
            "id": "excited",
            "name": "Excited",
            "description": "Energetic and enthusiastic"
        },
        {
            "id": "sad",
            "name": "Sad",
            "description": "Gentle and melancholic"
        },
        {
            "id": "calm",
            "name": "Calm",
            "description": "Peaceful and soothing"
        },
        {
            "id": "romantic",
            "name": "Romantic",
            "description": "Warm and intimate"
        },
        {
            "id": "playful",
            "name": "Playful",
            "description": "Light and teasing"
        }
    ]
    
    return {
        "success": True,
        "emotions": emotions
    }

@voice_router.post("/test/quality")
async def test_voice_quality(
    test_text: str = Form("Hello, this is a voice quality test."),
    engine: Optional[str] = Form(None),
    emotion: str = Form("neutral")
):
    """
    Test voice quality with sample text
    
    Args:
        test_text: Text to use for testing
        engine: Specific engine to test
        emotion: Emotion to test
        
    Returns:
        Audio sample for quality evaluation
    """
    try:
        # Parse engine preference
        preferred_engine = None
        if engine:
            try:
                preferred_engine = VoiceEngine(engine)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Unknown engine: {engine}")
        
        # Generate test audio
        audio_data = await voice_orchestrator.synthesize_speech(
            text=test_text,
            emotion=emotion,
            preferred_engine=preferred_engine
        )
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=voice_test.wav"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Voice quality test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export router
__all__ = ["voice_router"]
