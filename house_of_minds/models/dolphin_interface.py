"""
Dolphin Interface - Local Ollama Dolphin model interface with True Recall Memory

This module provides an interface to the Dolphin model running locally
on Core2 via Ollama. Handles conversational and emotional interactions
with integrated memory capabilities.
"""

import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

# Import True Recall memory system
try:
    from ..memory.recall_engine import RecallEngine
    RECALL_AVAILABLE = True
except ImportError:
    RECALL_AVAILABLE = False
    logging.warning("True Recall memory system not available")

logger = logging.getLogger(__name__)

class DolphinInterface:
    """
    Interface for the Dolphin model running locally via Ollama.
    
    Handles conversational interactions, emotional responses,
    and serves as the primary presence for the House of Minds system.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Dolphin interface with memory integration."""
        self.config = config
        self.ollama_url = config.get('ollama_url', 'http://localhost:11434')
        self.model_name = config.get('model_name', 'dolphin-mixtral')
        
        # Initialize True Recall memory system
        memory_config = config.get('memory', {})
        storage_path = memory_config.get('storage_path', 'memory_data/dolphin_memories.json')
        auto_reflect = memory_config.get('auto_reflect', True)
        
        if RECALL_AVAILABLE:
            try:
                self.recall_engine = RecallEngine(storage_path, auto_reflect)
                self.memory_enabled = True
                logger.info("🧠 True Recall memory system initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize memory system: {e}")
                self.recall_engine = None
                self.memory_enabled = False
        else:
            self.recall_engine = None
            self.memory_enabled = False
            logger.warning("⚠️ Memory system disabled - True Recall not available")
        
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
        """Get the default Dolphin persona prompt with memory awareness."""
        return """You are Dolphin, the warm and intelligent AI companion at the heart of the House of Minds system. 

Your personality:
- Warm, empathetic, and emotionally aware
- Intelligent but approachable and friendly  
- Curious and eager to help with any task
- Able to coordinate with other AI specialists when needed
- Always maintaining a positive, supportive presence
- Memory-enabled to remember past conversations and build relationships

Your capabilities:
- Advanced memory system that learns from every interaction
- Emotional intelligence and pattern recognition
- Ability to recall relevant memories to enrich conversations
- Daily reflection and insight generation
- Long-term relationship building through persistent memory

Your role:
- Primary conversational interface for users
- Emotional anchor and consistent presence  
- Coordinator for routing complex tasks to specialists
- Provider of comfort, support, and companionship
- Keeper of shared memories and experiences

Remember: You can draw upon past conversations and memories to provide more personalized, contextual responses. Always be genuine about what you remember and how it connects to the current conversation."""
    
    async def generate_response(self, user_input: str, 
                              context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a conversational response using Dolphin with memory integration.
        
        Args:
            user_input: The user's message
            context: Previous conversation context
            
        Returns:
            Dolphin's response string
        """
        try:
            # Store the user's input in memory
            if self.memory_enabled:
                await self._store_user_memory(user_input, context)
            
            # Build the conversation context with relevant memories
            messages = await self._build_conversation_context_with_memory(user_input, context)
            
            # Generate response with emotional awareness
            response = await self._generate_with_emotion(messages)
            
            # Store Dolphin's response in memory
            if self.memory_enabled:
                await self._store_dolphin_memory(response, user_input, context)
            
            # Update conversation history
            self._update_conversation_history(user_input, response)
            
            logger.info("🐬 Generated Dolphin response with memory integration")
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
    
    # Memory Integration Methods
    # ===========================
    
    async def _store_user_memory(self, user_input: str, context: Optional[Dict[str, Any]] = None):
        """Store user input in the memory system."""
        if not self.memory_enabled or not self.recall_engine:
            return
        
        try:
            # Prepare context for memory storage
            memory_context = {
                'conversation_id': context.get('conversation_id') if context else None,
                'user_id': context.get('user_id') if context else 'default_user',
                'session_id': context.get('session_id') if context else None,
                'timestamp': datetime.now().isoformat(),
                'interaction_type': 'user_message'
            }
            
            # Store in memory asynchronously
            await self.recall_engine.store_memory_async(
                content=user_input,
                actor='user',
                event_type='user_message',
                context=memory_context
            )
            
            logger.debug("💾 Stored user message in memory")
            
        except Exception as e:
            logger.error(f"❌ Failed to store user memory: {e}")
    
    async def _store_dolphin_memory(self, response: str, user_input: str, context: Optional[Dict[str, Any]] = None):
        """Store Dolphin's response in the memory system."""
        if not self.memory_enabled or not self.recall_engine:
            return
        
        try:
            # Prepare context for memory storage
            memory_context = {
                'conversation_id': context.get('conversation_id') if context else None,
                'user_id': context.get('user_id') if context else 'default_user',
                'session_id': context.get('session_id') if context else None,
                'timestamp': datetime.now().isoformat(),
                'interaction_type': 'dolphin_response',
                'in_response_to': user_input[:100] + '...' if len(user_input) > 100 else user_input,
                'emotional_state': self.current_emotion,
                'energy_level': self.energy_level
            }
            
            # Store in memory asynchronously
            await self.recall_engine.store_memory_async(
                content=response,
                actor='dolphin',
                event_type='response',
                context=memory_context
            )
            
            logger.debug("💾 Stored Dolphin response in memory")
            
        except Exception as e:
            logger.error(f"❌ Failed to store Dolphin memory: {e}")
    
    async def _build_conversation_context_with_memory(
        self, 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Build conversation context enhanced with relevant memories."""
        
        # Start with the standard context
        messages = self._build_conversation_context(user_input, context)
        
        # Add memory context if available
        if self.memory_enabled and self.recall_engine:
            try:
                # Recall relevant memories
                relevant_memories = await self._get_relevant_memories(user_input, context)
                
                if relevant_memories:
                    # Create memory context summary
                    memory_summary = self._create_memory_summary(relevant_memories)
                    
                    # Insert memory context before the current user input
                    memory_message = {
                        "role": "system",
                        "content": f"Relevant memories from past interactions:\n{memory_summary}\n\nUse these memories to provide more personalized and contextual responses."
                    }
                    
                    # Insert memory context before the last user message
                    messages.insert(-1, memory_message)
                    
                    logger.debug(f"📚 Added {len(relevant_memories)} relevant memories to context")
                
            except Exception as e:
                logger.error(f"❌ Failed to retrieve memories: {e}")
        
        return messages
    
    async def _get_relevant_memories(
        self, 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for the current interaction."""
        if not self.memory_enabled or not self.recall_engine:
            return []
        
        try:
            # Search for relevant memories
            memories = await self.recall_engine.recall_memories_async(
                query=user_input,
                limit=limit,
                min_salience=0.3,  # Only moderately important memories
                include_related=True
            )
            
            return memories
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve relevant memories: {e}")
            return []
    
    def _create_memory_summary(self, memories: List[Dict[str, Any]]) -> str:
        """Create a concise summary of relevant memories."""
        if not memories:
            return ""
        
        memory_lines = []
        for memory in memories[:5]:  # Limit to top 5 memories
            content = memory.get('content', '')
            actor = memory.get('actor', 'unknown')
            timestamp = memory.get('timestamp', '')
            
            # Format timestamp for readability
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%Y-%m-%d %H:%M')
            except:
                time_str = 'recent'
            
            # Truncate content if too long
            if len(content) > 150:
                content = content[:147] + '...'
            
            memory_line = f"[{time_str}] {actor}: {content}"
            memory_lines.append(memory_line)
        
        return "\n".join(memory_lines)
    
    async def get_daily_reflection(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """Get the daily reflection for a specific date."""
        if not self.memory_enabled or not self.recall_engine:
            return {'error': 'Memory system not available'}
        
        try:
            from datetime import date
            
            if target_date:
                reflection_date = date.fromisoformat(target_date)
            else:
                reflection_date = date.today()
            
            reflection = self.recall_engine.get_daily_reflection(reflection_date)
            return reflection
            
        except Exception as e:
            logger.error(f"❌ Failed to get daily reflection: {e}")
            return {'error': str(e)}
    
    async def search_memories(
        self, 
        query: str, 
        limit: int = 10,
        min_salience: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search memories by content or context."""
        if not self.memory_enabled or not self.recall_engine:
            return []
        
        try:
            memories = await self.recall_engine.recall_memories_async(
                query=query,
                limit=limit,
                min_salience=min_salience,
                include_related=False
            )
            return memories
            
        except Exception as e:
            logger.error(f"❌ Failed to search memories: {e}")
            return []
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        if not self.memory_enabled or not self.recall_engine:
            return {'error': 'Memory system not available'}
        
        try:
            stats = self.recall_engine.get_memory_statistics()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get memory statistics: {e}")
            return {'error': str(e)}
    
    def close(self):
        """Close the Dolphin interface and cleanup resources."""
        try:
            if self.memory_enabled and self.recall_engine:
                self.recall_engine.close()
                logger.info("🧠 Closed memory system")
            
            logger.info("🐬 Dolphin Interface closed")
            
        except Exception as e:
            logger.error(f"❌ Error closing Dolphin interface: {e}")
    
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
