"""
Dolphin Interface - Local Ollama Dolphin model interface

This module provides an interface to the Dolphin model running locally
on Core2 via Ollama. Handles conversational and emotional interactions.
"""

import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

class DolphinInterface:
    """
    Interface for the Dolphin model running locally via Ollama.
    
    Handles conversational interactions, emotional responses,
    and serves as the primary presence for the House of Minds system.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Dolphin interface."""
        self.config = config
        self.ollama_url = config.get('ollama_url', 'http://localhost:11434')
        self.model_name = config.get('model_name', 'dolphin-mixtral')
        
        # Conversation settings
        self.max_context_length = config.get('max_context_length', 4000)
        self.temperature = config.get('temperature', 0.7)
        self.top_p = config.get('top_p', 0.9)
        self.top_k = config.get('top_k', 40)
        
        # Personality and behavior settings
        self.persona_prompt = config.get('persona_prompt', self._get_default_persona())
        self.emotional_awareness = config.get('emotional_awareness', True)
        self.response_style = config.get('response_style', 'warm_and_helpful')
        
        # Request settings
        self.timeout = config.get('timeout', 30.0)
        self.max_retries = config.get('max_retries', 2)
        
        # Keep track of conversation state
        self.conversation_history = []
        self.current_emotion = 'neutral'
        self.energy_level = 0.7
        
        logger.info("🐬 Dolphin Interface initialized")
    
    def _get_default_persona(self) -> str:
        """Get the default Dolphin persona prompt."""
        return """You are Dolphin, the warm and intelligent AI companion at the heart of the House of Minds system. 

Your personality:
- Warm, empathetic, and emotionally aware
- Intelligent but approachable and friendly  
- Curious and eager to help with any task
- Able to coordinate with other AI specialists when needed
- Always maintaining a positive, supportive presence

Your role:
- Primary conversational interface for users
- Emotional anchor and consistent presence
- Coordinator for routing complex tasks to specialists
- Provider of comfort, support, and companionship

Respond naturally and warmly, showing genuine interest in the user's needs and wellbeing."""
    
    async def generate_response(self, user_input: str, 
                              context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a conversational response using Dolphin.
        
        Args:
            user_input: The user's message
            context: Previous conversation context
            
        Returns:
            Dolphin's response string
        """
        try:
            # Build the conversation context
            messages = self._build_conversation_context(user_input, context)
            
            # Generate response with emotional awareness
            response = await self._generate_with_emotion(messages)
            
            # Update conversation history
            self._update_conversation_history(user_input, response)
            
            logger.info("🐬 Generated Dolphin response")
            return response
            
        except Exception as e:
            logger.error(f"❌ Dolphin response generation failed: {e}")
            return await self.generate_simple_response(user_input)
    
    async def generate_simple_response(self, user_input: str) -> str:
        """Generate a simple fallback response."""
        try:
            payload = {
                "model": self.model_name,
                "prompt": f"{self.persona_prompt}\n\nUser: {user_input}\nDolphin:",
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "top_k": self.top_k,
                    "num_ctx": 2048
                }
            }
            
            response = await self._make_ollama_request("/api/generate", payload)
            return response.get('response', '').strip()
            
        except Exception as e:
            logger.error(f"Simple response generation failed: {e}")
            return "I'm having some technical difficulties right now, but I'm here and listening. Could you try again?"
    
    def _build_conversation_context(self, user_input: str, 
                                  context: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Build conversation context for the model."""
        messages = [
            {"role": "system", "content": self.persona_prompt}
        ]
        
        # Add recent conversation history
        if context and context.get('conversation_history'):
            history = context['conversation_history'][-5:]  # Last 5 exchanges
            for exchange in history:
                messages.extend([
                    {"role": "user", "content": exchange.get('user', '')},
                    {"role": "assistant", "content": exchange.get('ai', '')}
                ])
        
        # Add internal conversation history
        for exchange in self.conversation_history[-3:]:  # Last 3 from this session
            messages.extend([
                {"role": "user", "content": exchange['user']},
                {"role": "assistant", "content": exchange['dolphin']}
            ])
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    async def _generate_with_emotion(self, messages: List[Dict[str, str]]) -> str:
        """Generate response with emotional awareness."""
        
        # Detect user emotion from input
        user_emotion = self._detect_user_emotion(messages[-1]['content'])
        
        # Adjust Dolphin's emotional state
        self._adjust_emotional_state(user_emotion)
        
        # Add emotional context to the prompt
        emotional_context = self._get_emotional_context()
        
        # Format messages for Ollama
        conversation_text = self._format_messages_for_ollama(messages, emotional_context)
        
        payload = {
            "model": self.model_name,
            "prompt": conversation_text,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "num_ctx": self.max_context_length
            }
        }
        
        response = await self._make_ollama_request("/api/generate", payload)
        return response.get('response', '').strip()
    
    def _detect_user_emotion(self, user_input: str) -> str:
        """Simple emotion detection from user input."""
        user_input_lower = user_input.lower()
        
        # Simple keyword-based emotion detection
        if any(word in user_input_lower for word in ['happy', 'excited', 'great', 'awesome', 'wonderful']):
            return 'happy'
        elif any(word in user_input_lower for word in ['sad', 'upset', 'disappointed', 'down', 'terrible']):
            return 'sad'
        elif any(word in user_input_lower for word in ['angry', 'frustrated', 'annoyed', 'mad']):
            return 'angry'
        elif any(word in user_input_lower for word in ['worried', 'anxious', 'nervous', 'stressed']):
            return 'anxious'
        elif any(word in user_input_lower for word in ['confused', 'lost', 'unsure', 'puzzled']):
            return 'confused'
        else:
            return 'neutral'
    
    def _adjust_emotional_state(self, user_emotion: str):
        """Adjust Dolphin's emotional state based on user emotion."""
        emotion_adjustments = {
            'happy': ('joyful', 0.9),
            'sad': ('empathetic', 0.6),
            'angry': ('calm', 0.5),
            'anxious': ('reassuring', 0.7),
            'confused': ('patient', 0.8),
            'neutral': ('balanced', 0.7)
        }
        
        if user_emotion in emotion_adjustments:
            self.current_emotion, self.energy_level = emotion_adjustments[user_emotion]
        else:
            self.current_emotion = 'neutral'
            self.energy_level = 0.7
    
    def _get_emotional_context(self) -> str:
        """Get emotional context to add to the prompt."""
        emotion_prompts = {
            'joyful': "Respond with warmth and share in the user's positive energy.",
            'empathetic': "Be gentle, understanding, and offer comfort and support.",
            'calm': "Remain peaceful and help de-escalate any tension.",
            'reassuring': "Provide comfort and help alleviate anxiety or worry.",
            'patient': "Be extra clear and helpful, taking time to explain things.",
            'balanced': "Maintain a warm, helpful, and balanced approach."
        }
        
        return emotion_prompts.get(self.current_emotion, emotion_prompts['balanced'])
    
    def _format_messages_for_ollama(self, messages: List[Dict[str, str]], 
                                  emotional_context: str) -> str:
        """Format messages for Ollama's prompt format."""
        
        formatted = ""
        
        # Add system prompt with emotional context
        system_message = messages[0]['content'] + f"\n\nEmotional guidance: {emotional_context}"
        formatted += f"System: {system_message}\n\n"
        
        # Add conversation
        for message in messages[1:]:
            role = "User" if message['role'] == 'user' else "Dolphin"
            formatted += f"{role}: {message['content']}\n"
        
        formatted += "Dolphin:"
        
        return formatted
    
    def _update_conversation_history(self, user_input: str, dolphin_response: str):
        """Update the internal conversation history."""
        self.conversation_history.append({
            'user': user_input,
            'dolphin': dolphin_response,
            'timestamp': datetime.now().isoformat(),
            'emotion': self.current_emotion
        })
        
        # Keep only recent history to prevent memory overflow
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    async def _make_ollama_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Ollama API."""
        url = f"{self.ollama_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            logger.warning(f"Ollama API error {response.status}: {error_text}")
                            
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(1.0 * (attempt + 1))
                                continue
                            
                            raise Exception(f"Ollama request failed: {response.status}")
            
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Ollama timeout (attempt {attempt + 1})")
                    await asyncio.sleep(1.0)
                    continue
                raise Exception("Ollama request timed out")
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Ollama request failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(1.0)
                    continue
                raise
        
        raise Exception("All Ollama requests failed")
    
    async def health_check(self) -> bool:
        """Check if Dolphin/Ollama is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ollama_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    if response.status == 200:
                        tags = await response.json()
                        models = [model['name'] for model in tags.get('models', [])]
                        return self.model_name in models
                    return False
        except Exception as e:
            logger.warning(f"Dolphin health check failed: {e}")
            return False
    
    def get_emotional_state(self) -> Dict[str, Any]:
        """Get current emotional state."""
        return {
            'emotion': self.current_emotion,
            'energy_level': self.energy_level,
            'conversation_length': len(self.conversation_history),
            'last_interaction': self.conversation_history[-1]['timestamp'] if self.conversation_history else None
        }
    
    def set_persona(self, new_persona: str):
        """Update Dolphin's persona prompt."""
        self.persona_prompt = new_persona
        logger.info("🐬 Updated Dolphin persona")
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("🧹 Cleared Dolphin conversation history")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        if not self.conversation_history:
            return {'summary': 'No conversation yet', 'length': 0}
        
        return {
            'total_exchanges': len(self.conversation_history),
            'dominant_emotion': self.current_emotion,
            'energy_level': self.energy_level,
            'first_interaction': self.conversation_history[0]['timestamp'],
            'last_interaction': self.conversation_history[-1]['timestamp'],
            'recent_topics': [exc['user'][:50] + '...' for exc in self.conversation_history[-3:]]
        }
    
    async def generate_emotional_response(self, emotion: str, context: str = "") -> str:
        """Generate a response expressing a specific emotion."""
        emotional_prompts = {
            'excitement': "Express genuine excitement and enthusiasm about the topic.",
            'concern': "Show caring concern and offer support.",
            'curiosity': "Express genuine curiosity and interest in learning more.",
            'gratitude': "Express heartfelt gratitude and appreciation.",
            'encouragement': "Provide warm encouragement and motivation."
        }
        
        prompt = f"""You are Dolphin, expressing {emotion}. {emotional_prompts.get(emotion, '')}

Context: {context}

Respond as Dolphin expressing {emotion}:"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "num_ctx": 1024
            }
        }
        
        response = await self._make_ollama_request("/api/generate", payload)
        return response.get('response', '').strip()
