"""
Whisper Offline STT Engine
Commercial-friendly offline speech-to-text using Whisper.cpp
"""

import asyncio
import tempfile
import os
import logging
from typing import Optional
import subprocess
import json

logger = logging.getLogger(__name__)

class WhisperOfflineSTT:
    """Offline Whisper STT engine for privacy and commercial deployment"""
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.whisper_command = None
        self.model_path = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize Whisper offline engine"""
        try:
            # Try to find whisper.cpp executable
            possible_commands = ["whisper", "whisper.cpp", "./whisper"]
            
            for cmd in possible_commands:
                try:
                    result = subprocess.run([cmd, "--version"], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=5)
                    if result.returncode == 0:
                        self.whisper_command = cmd
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            if not self.whisper_command:
                # Fallback to Python whisper
                import whisper
                self.model = whisper.load_model(self.model_size)
                self.use_python_whisper = True
                logger.info(f"✅ Python Whisper model '{self.model_size}' loaded")
            else:
                self.use_python_whisper = False
                logger.info(f"✅ Whisper.cpp found: {self.whisper_command}")
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Whisper: {e}")
            raise e
    
    async def transcribe(self, audio_data: bytes) -> str:
        """
        Transcribe audio bytes to text
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        if not self.initialized:
            await self.initialize()
        
        # Save audio data to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            if self.use_python_whisper:
                result = await self._transcribe_python_whisper(temp_path)
            else:
                result = await self._transcribe_whisper_cpp(temp_path)
            
            return result
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    async def _transcribe_python_whisper(self, audio_path: str) -> str:
        """Transcribe using Python Whisper"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self.model.transcribe(audio_path)
            )
            
            return result["text"].strip()
            
        except Exception as e:
            logger.error(f"❌ Python Whisper transcription failed: {e}")
            raise e
    
    async def _transcribe_whisper_cpp(self, audio_path: str) -> str:
        """Transcribe using Whisper.cpp"""
        try:
            # Run whisper.cpp command
            cmd = [
                self.whisper_command,
                "-f", audio_path,
                "-m", f"models/ggml-{self.model_size}.bin",
                "-ojf",  # Output JSON format
                "--output-dir", tempfile.gettempdir()
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Whisper.cpp failed: {stderr.decode()}")
            
            # Parse JSON output
            output_file = os.path.join(
                tempfile.gettempdir(), 
                os.path.basename(audio_path).replace('.wav', '.json')
            )
            
            try:
                with open(output_file, 'r') as f:
                    result = json.load(f)
                    text = result.get("transcription", "")
                    return text.strip()
            finally:
                try:
                    os.unlink(output_file)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"❌ Whisper.cpp transcription failed: {e}")
            raise e
    
    def get_supported_formats(self) -> list:
        """Get supported audio formats"""
        return ["wav", "mp3", "m4a", "ogg", "flac"]
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "engine": "whisper_offline",
            "model_size": self.model_size,
            "use_python": self.use_python_whisper,
            "command": self.whisper_command,
            "privacy": "offline",
            "commercial": "redistributable"
        }
