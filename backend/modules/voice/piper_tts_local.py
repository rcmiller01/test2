"""
Piper TTS Local Engine
Commercial-friendly offline text-to-speech using Piper
"""

import asyncio
import tempfile
import os
import logging
from typing import Optional
import subprocess
import json

logger = logging.getLogger(__name__)

class PiperTTSLocal:
    """Local Piper TTS engine for offline commercial deployment"""
    
    def __init__(self, model_name: str = "en_US-ljspeech-medium"):
        self.model_name = model_name
        self.piper_command = None
        self.model_path = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize Piper TTS engine"""
        try:
            # Try to find piper executable
            possible_commands = ["piper", "./piper", "piper.exe"]
            
            for cmd in possible_commands:
                try:
                    result = subprocess.run([cmd, "--version"], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=5)
                    if result.returncode == 0:
                        self.piper_command = cmd
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            if not self.piper_command:
                raise Exception("Piper executable not found")
            
            # Check for model file
            model_paths = [
                f"models/{self.model_name}.onnx",
                f"./voices/{self.model_name}.onnx",
                f"/usr/share/piper/voices/{self.model_name}.onnx"
            ]
            
            for path in model_paths:
                if os.path.exists(path):
                    self.model_path = path
                    break
            
            if not self.model_path:
                logger.warning(f"⚠️ Piper model {self.model_name} not found locally")
                # Could download model here for commercial deployment
            
            self.initialized = True
            logger.info(f"✅ Piper TTS initialized with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Piper TTS: {e}")
            raise e
    
    async def synthesize(self, text: str, voice_profile) -> bytes:
        """
        Synthesize text to speech
        
        Args:
            text: Text to synthesize
            voice_profile: Voice characteristics
            
        Returns:
            Audio bytes (WAV format)
        """
        if not self.initialized:
            await self.initialize()
        
        if not self.model_path:
            raise Exception("Piper model not available")
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_path = temp_file.name
        
        try:
            # Build Piper command
            cmd = [
                self.piper_command,
                "--model", self.model_path,
                "--output_file", output_path
            ]
            
            # Add voice modulation parameters
            if hasattr(voice_profile, 'speed') and voice_profile.speed != 1.0:
                cmd.extend(["--length_scale", str(1.0 / voice_profile.speed)])
            
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send text to Piper
            stdout, stderr = await process.communicate(input=text.encode('utf-8'))
            
            if process.returncode != 0:
                raise Exception(f"Piper TTS failed: {stderr.decode()}")
            
            # Read generated audio
            with open(output_path, 'rb') as f:
                audio_data = f.read()
            
            # Apply post-processing for emotional modulation
            if hasattr(voice_profile, 'emotion') and voice_profile.emotion != "neutral":
                audio_data = await self._apply_emotional_processing(audio_data, voice_profile)
            
            return audio_data
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(output_path)
            except:
                pass
    
    async def _apply_emotional_processing(self, audio_data: bytes, voice_profile) -> bytes:
        """Apply emotional processing to audio"""
        # This would involve audio processing for emotional modulation
        # For now, return unmodified audio
        # Future: Use librosa, soundfile for pitch/tempo modification
        return audio_data
    
    def get_available_voices(self) -> list:
        """Get list of available Piper voices"""
        voices = [
            "en_US-ljspeech-medium",
            "en_US-ljspeech-high", 
            "en_GB-alan-medium",
            "en_GB-alan-low",
            "de_DE-thorsten-medium",
            "fr_FR-upmc-medium",
            "es_ES-sharvard-medium"
        ]
        return voices
    
    def get_supported_emotions(self) -> list:
        """Get supported emotional modulations"""
        return ["neutral", "happy", "sad", "excited", "calm", "romantic"]
    
    def get_engine_info(self) -> dict:
        """Get engine information"""
        return {
            "engine": "piper_tts_local",
            "model": self.model_name,
            "command": self.piper_command,
            "model_path": self.model_path,
            "privacy": "offline",
            "commercial": "redistributable",
            "quality": "medium-high"
        }
