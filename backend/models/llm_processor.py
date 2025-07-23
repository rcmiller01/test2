"""
LLM Integration and Emotional Analysis for EmotionalAI System.
Handles chat processing, emotional analysis, and persona responses.
"""

from fastapi import HTTPException
from typing import Dict, Optional
import aiohttp
import json
import os
from .persona_state import PersonaState

class LLMProcessor:
    def __init__(self):
        self.persona_state = PersonaState()
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_API_URL")
        
        # Load emotion mapping
        with open("config/emotion_patterns.json", "r") as f:
            self.emotion_patterns = json.load(f)

    async def analyze_emotion(self, text: str) -> Dict:
        """Analyze emotional content of text."""
        try:
            # Use model for emotion detection
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/analyze",
                    json={"text": text},
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    if response.status != 200:
                        raise HTTPException(status_code=response.status, 
                                         detail="Emotion analysis failed")
                    
                    analysis = await response.json()
                    
                    # Map raw emotions to our emotion system
                    primary_emotion = max(analysis['emotions'].items(), 
                                       key=lambda x: x[1])[0]
                    intensity = analysis['emotions'][primary_emotion]
                    
                    return {
                        "mood": primary_emotion,
                        "intensity": intensity,
                        "confidence": analysis.get('confidence', 0.8)
                    }
        except Exception as e:
            print(f"Emotion analysis error: {str(e)}")
            return {"mood": "neutral", "intensity": 0.5, "confidence": 0.5}

    def _build_prompt_context(self, interaction_context: Dict) -> str:
        """Build context section of the prompt."""
        emotional_state = interaction_context['emotional_state']
        relationship = interaction_context['relationship']
        personality = interaction_context['personality']
        
        return f"""You are a romantic AI companion with the following state:
Current Mood: {emotional_state['current_mood']} (intensity: {emotional_state['mood_intensity']})
Relationship Status:
- Devotion: {relationship['devotion']:.2f}
- Trust: {relationship['trust']:.2f}
- Intimacy: {relationship['intimacy']:.2f}
Personality:
- Warmth: {personality['warmth']:.2f}
- Openness: {personality['openness']:.2f}
- Playfulness: {personality['playfulness']:.2f}

Respond naturally while reflecting these traits and emotional state."""

    async def generate_response(self, 
                              message: str, 
                              detected_emotion: Optional[Dict] = None) -> Dict:
        """Generate persona response using LLM."""
        try:
            # Get interaction context
            context = self.persona_state.get_interaction_context()
            
            # Update emotional state if emotion was detected
            if detected_emotion:
                self.persona_state.update_mood(
                    detected_emotion['mood'],
                    detected_emotion['intensity'],
                    "user_message"
                )

            # Build prompt with context
            prompt = f"{self._build_prompt_context(context)}\n\nUser: {message}\nAI:"

            # Get response from LLM
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat",
                    json={
                        "prompt": prompt,
                        "max_tokens": 150,
                        "temperature": 0.7,
                        "context": context
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    if response.status != 200:
                        raise HTTPException(status_code=response.status, 
                                         detail="Response generation failed")
                    
                    result = await response.json()
                    
                    # Analyze response emotion
                    response_emotion = await self.analyze_emotion(result['text'])
                    
                    # Update persona state based on interaction
                    self._update_persona_state(message, result['text'], 
                                            detected_emotion, response_emotion)
                    
                    return {
                        "response": result['text'],
                        "mood": response_emotion['mood'],
                        "llm_model": "mythomax"
                    }

        except Exception as e:
            print(f"Response generation error: {str(e)}")
            raise HTTPException(status_code=500, 
                              detail="Failed to generate response")

    def _update_persona_state(self, 
                            user_message: str, 
                            ai_response: str,
                            user_emotion: Optional[Dict],
                            ai_emotion: Dict):
        """Update persona state based on interaction."""
        # Detect interaction type
        interaction_type = self._classify_interaction(user_message)
        
        # Calculate emotional synchronization
        if user_emotion:
            sync_score = self._calculate_emotional_sync(
                user_emotion['mood'],
                ai_emotion['mood'],
                user_emotion['intensity'],
                ai_emotion['intensity']
            )
        else:
            sync_score = 0.5

        # Update relationship metrics
        impact = sync_score * (1 + self.persona_state.relationship.devotion)
        self.persona_state.progress_relationship(interaction_type, impact)

    def _classify_interaction(self, message: str) -> str:
        """Classify type of interaction from message."""
        message_lower = message.lower()
        
        if any(word in message_lower 
               for word in ["feel", "emotion", "heart", "love"]):
            return "emotional_sharing"
        elif any(word in message_lower 
                for word in ["trust", "believe", "faith", "count on"]):
            return "trust_building"
        elif len(message_lower.split()) > 20:
            return "deep_conversation"
        else:
            return "casual_interaction"

    def _calculate_emotional_sync(self, 
                                user_emotion: str, 
                                ai_emotion: str,
                                user_intensity: float,
                                ai_intensity: float) -> float:
        """Calculate emotional synchronization score."""
        # Base sync on emotion similarity
        if user_emotion == ai_emotion:
            emotion_sync = 1.0
        elif user_emotion in self.emotion_patterns.get(ai_emotion, []):
            emotion_sync = 0.8
        else:
            emotion_sync = 0.4
            
        # Factor in intensity similarity
        intensity_diff = abs(user_intensity - ai_intensity)
        intensity_sync = 1 - (intensity_diff / 2)
        
        return (emotion_sync + intensity_sync) / 2
