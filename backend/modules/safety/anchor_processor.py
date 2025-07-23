"""
Anchor Phrase Processing System
Handles emergency emotional regulation when "safe space" is triggered
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AnchorResponse(Enum):
    """Types of anchor responses"""
    IMMEDIATE_CALM = "immediate_calm"
    GROUNDING_TECHNIQUE = "grounding_technique"
    BREATHING_EXERCISE = "breathing_exercise"
    POSITIVE_AFFIRMATION = "positive_affirmation"
    TOPIC_REDIRECT = "topic_redirect"
    PROFESSIONAL_RESOURCE = "professional_resource"

class EmotionalState(Enum):
    """Emotional states for appropriate responses"""
    OVERWHELMED = "overwhelmed"
    ANXIOUS = "anxious"
    DISTRESSED = "distressed"
    CONFUSED = "confused"
    TRIGGERED = "triggered"
    STABLE = "stable"

@dataclass
class AnchorActivation:
    """Anchor phrase activation event"""
    user_id: str
    trigger_phrase: str
    emotional_state: Dict[str, float]
    context_before: Dict[str, Any]
    response_type: AnchorResponse
    recovery_successful: bool
    timestamp: datetime

class AnchorPhraseProcessor:
    """
    Processes anchor phrase activations and provides appropriate
    calming responses to return user to emotional safe space
    """
    
    def __init__(self):
        self.anchor_phrases = ["safe space", "anchor", "emergency stop", "help me"]
        self.response_templates = {}
        self.grounding_techniques = {}
        self.breathing_exercises = {}
        self.calming_responses = {}
        self._initialize_responses()
    
    def _initialize_responses(self):
        """Initialize response templates and techniques"""
        
        # Immediate calming responses
        self.calming_responses = {
            EmotionalState.OVERWHELMED: [
                "I hear you. Let's take this slowly. You're in a safe space now.",
                "Take a deep breath with me. We're going to pause and center ourselves.",
                "I'm here with you. Everything is okay. Let's focus on feeling grounded.",
                "You've called for your safe space, and I'm creating that for you right now.",
            ],
            EmotionalState.ANXIOUS: [
                "Let's slow down together. You're safe here with me.",
                "I can sense your anxiety. Let's focus on calming your mind.",
                "Take a moment to breathe. I'm here, and nothing is urgent right now.",
                "You're in control. Let's practice some gentle grounding together.",
            ],
            EmotionalState.DISTRESSED: [
                "I can feel your distress. Let's pause and focus on comfort.",
                "You're not alone. I'm here to support you through this moment.",
                "Let's shift to something that brings you peace and safety.",
                "Your well-being is what matters most right now.",
            ],
            EmotionalState.CONFUSED: [
                "It's okay to feel confused. Let's simplify and focus on what's clear.",
                "Let me help you find your center again. One step at a time.",
                "Confusion is temporary. Let's ground ourselves in what we know is true.",
                "I'm here to help you navigate back to clarity and peace.",
            ],
            EmotionalState.TRIGGERED: [
                "You've been triggered, and that's okay. Let's move to safety together.",
                "I'm creating a buffer of calm around you. Focus on my voice.",
                "You recognized you needed help, and that shows great self-awareness.",
                "Let's disconnect from what triggered you and reconnect with peace.",
            ]
        }
        
        # Grounding techniques (5-4-3-2-1 method variations)
        self.grounding_techniques = {
            "sensory_grounding": {
                "instruction": "Let's use our senses to ground ourselves",
                "steps": [
                    "Name 5 things you can see around you right now",
                    "Name 4 things you can physically feel (temperature, texture, pressure)",
                    "Name 3 things you can hear in your environment",
                    "Name 2 things you can smell",
                    "Name 1 thing you can taste"
                ]
            },
            "breathing_focus": {
                "instruction": "Let's focus on our breathing together",
                "steps": [
                    "Place one hand on your chest, one on your belly",
                    "Breathe in slowly through your nose for 4 counts",
                    "Hold your breath gently for 4 counts",
                    "Exhale slowly through your mouth for 6 counts",
                    "Repeat this cycle 5 times, focusing only on the rhythm"
                ]
            },
            "positive_anchoring": {
                "instruction": "Let's anchor yourself in positive truths",
                "steps": [
                    "You are safe in this moment",
                    "You have the strength to handle difficult emotions",
                    "This feeling is temporary and will pass",
                    "You are worthy of care and compassion",
                    "You took the right step by asking for your safe space"
                ]
            },
            "body_awareness": {
                "instruction": "Let's reconnect with your physical sense of safety",
                "steps": [
                    "Wiggle your toes and feel your feet on the ground",
                    "Roll your shoulders back and release tension",
                    "Gently stretch your arms above your head",
                    "Feel the support of whatever you're sitting or lying on",
                    "Notice how your body feels supported and stable"
                ]
            }
        }
        
        # Topic redirection options
        self.safe_topics = [
            "peaceful nature scenes",
            "favorite calming music",
            "comforting memories",
            "gratitude and appreciation",
            "gentle self-care activities",
            "supportive affirmations",
            "mindfulness practices",
            "creative expression",
            "connection with loved ones",
            "personal strengths and achievements"
        ]
        
        # Professional resources
        self.professional_resources = {
            "crisis_lines": [
                "National Suicide Prevention Lifeline: 988 (US)",
                "Crisis Text Line: Text HOME to 741741 (US)",
                "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
            ],
            "mental_health": [
                "Psychology Today therapist finder: https://www.psychologytoday.com",
                "Better Help online therapy: https://www.betterhelp.com",
                "Your local community mental health center"
            ],
            "support_groups": [
                "NAMI (National Alliance on Mental Illness): https://www.nami.org",
                "Support group finder: https://www.supportgroupscentral.com",
                "Online support communities"
            ]
        }
    
    async def process_anchor_activation(
        self, 
        user_id: str, 
        content: str, 
        emotional_state: Dict[str, float],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process anchor phrase activation and provide appropriate response
        
        Args:
            user_id: User identifier
            content: The content that contained the anchor phrase
            emotional_state: Current emotional state
            context: Additional context information
            
        Returns:
            Anchor response with calming techniques and guidance
        """
        try:
            # Detect emotional state
            detected_state = self._detect_emotional_state(emotional_state, context)
            
            # Select appropriate response type
            response_type = self._select_response_type(detected_state, emotional_state)
            
            # Generate response
            response = await self._generate_anchor_response(
                detected_state, response_type, user_id
            )
            
            # Log activation
            activation = AnchorActivation(
                user_id=user_id,
                trigger_phrase=self._extract_anchor_phrase(content),
                emotional_state=emotional_state,
                context_before=context,
                response_type=response_type,
                recovery_successful=False,  # Will be updated later
                timestamp=datetime.now()
            )
            
            await self._log_anchor_activation(activation)
            
            # Schedule follow-up check
            asyncio.create_task(self._schedule_recovery_check(user_id, activation))
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to process anchor activation: {e}")
            # Fallback response
            return {
                "type": "emergency_response",
                "message": "I hear that you need your safe space. Take a deep breath with me. You're safe, and I'm here to support you.",
                "immediate_action": "breathing_exercise",
                "grounding_technique": self.grounding_techniques["breathing_focus"],
                "follow_up": "Let me know when you feel more centered, and we can talk about what you need."
            }
    
    def _detect_emotional_state(
        self, 
        emotional_state: Dict[str, float], 
        context: Dict[str, Any]
    ) -> EmotionalState:
        """Detect primary emotional state requiring intervention"""
        
        # Check for high-intensity negative emotions
        if emotional_state.get('anxiety', 0) > 0.7:
            return EmotionalState.ANXIOUS
        elif emotional_state.get('overwhelm', 0) > 0.6:
            return EmotionalState.OVERWHELMED
        elif emotional_state.get('distress', 0) > 0.6:
            return EmotionalState.DISTRESSED
        elif emotional_state.get('confusion', 0) > 0.5:
            return EmotionalState.CONFUSED
        elif any(v > 0.8 for v in emotional_state.values()):
            return EmotionalState.TRIGGERED
        else:
            return EmotionalState.STABLE
    
    def _select_response_type(
        self, 
        emotional_state: EmotionalState, 
        emotion_values: Dict[str, float]
    ) -> AnchorResponse:
        """Select most appropriate response type"""
        
        # High intensity emotions need immediate calming
        max_intensity = max(emotion_values.values()) if emotion_values else 0
        
        if max_intensity > 0.8:
            return AnchorResponse.IMMEDIATE_CALM
        elif emotional_state == EmotionalState.ANXIOUS:
            return AnchorResponse.BREATHING_EXERCISE
        elif emotional_state == EmotionalState.OVERWHELMED:
            return AnchorResponse.GROUNDING_TECHNIQUE
        elif emotional_state == EmotionalState.CONFUSED:
            return AnchorResponse.TOPIC_REDIRECT
        else:
            return AnchorResponse.POSITIVE_AFFIRMATION
    
    async def _generate_anchor_response(
        self, 
        emotional_state: EmotionalState, 
        response_type: AnchorResponse,
        user_id: str
    ) -> Dict[str, Any]:
        """Generate appropriate anchor response"""
        
        # Get immediate calming message
        calming_messages = self.calming_responses.get(emotional_state, [])
        immediate_message = calming_messages[0] if calming_messages else \
            "You've requested your safe space. I'm here with you, and everything is okay."
        
        response: Dict[str, Any] = {
            "type": "anchor_response",
            "emotional_state": emotional_state.value,
            "response_type": response_type.value,
            "immediate_message": immediate_message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add specific technique based on response type
        if response_type == AnchorResponse.GROUNDING_TECHNIQUE:
            technique_key = "sensory_grounding" if emotional_state == EmotionalState.OVERWHELMED else "body_awareness"
            response["grounding_technique"] = self.grounding_techniques[technique_key]
            
        elif response_type == AnchorResponse.BREATHING_EXERCISE:
            response["breathing_exercise"] = self.grounding_techniques["breathing_focus"]
            
        elif response_type == AnchorResponse.POSITIVE_AFFIRMATION:
            response["affirmations"] = self.grounding_techniques["positive_anchoring"]
            
        elif response_type == AnchorResponse.TOPIC_REDIRECT:
            response["safe_topics"] = self.safe_topics[:5]  # Provide 5 options
            response["redirect_message"] = "Let's gently shift to something more peaceful. What would feel comforting to talk about?"
        
        # Always include professional resources for severe cases
        max_emotion = max(emotional_state.value for emotional_state in [EmotionalState.OVERWHELMED, EmotionalState.DISTRESSED, EmotionalState.TRIGGERED])
        if emotional_state in [EmotionalState.OVERWHELMED, EmotionalState.DISTRESSED, EmotionalState.TRIGGERED]:
            response["professional_resources"] = {
                "message": "If you're experiencing persistent distress, professional support can be very helpful:",
                "resources": self.professional_resources["crisis_lines"][:2]
            }
        
        # Add follow-up guidance
        response["follow_up"] = {
            "check_in_time": 300,  # 5 minutes
            "questions": [
                "How are you feeling now?",
                "Is there anything specific you need for comfort?",
                "Would you like to continue with grounding techniques or talk about something peaceful?"
            ]
        }
        
        return response
    
    def _extract_anchor_phrase(self, content: str) -> str:
        """Extract which anchor phrase was used"""
        content_lower = content.lower()
        for phrase in self.anchor_phrases:
            if phrase in content_lower:
                return phrase
        return "safe space"  # Default
    
    async def _log_anchor_activation(self, activation: AnchorActivation):
        """Log anchor activation for monitoring and analysis"""
        try:
            # This would integrate with the safety engine's database
            logger.info(f"🚨 Anchor phrase '{activation.trigger_phrase}' activated for user {activation.user_id}")
            logger.info(f"   Response type: {activation.response_type.value}")
            logger.info(f"   Emotional state: {activation.emotional_state}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log anchor activation: {e}")
    
    async def _schedule_recovery_check(self, user_id: str, activation: AnchorActivation):
        """Schedule follow-up check for recovery"""
        try:
            # Wait 5 minutes before checking in
            await asyncio.sleep(300)
            
            # This could trigger a gentle check-in message
            logger.info(f"🔔 Recovery check scheduled for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule recovery check: {e}")
    
    async def assess_recovery_success(
        self, 
        user_id: str, 
        emotional_state_after: Dict[str, float]
    ) -> bool:
        """Assess if user has successfully recovered from anchor activation"""
        try:
            # Check if emotional intensity has decreased
            max_intensity = max(emotional_state_after.values()) if emotional_state_after else 0
            
            # Recovery successful if max emotion is below moderate level
            recovery_successful = max_intensity < 0.5
            
            logger.info(f"🏥 Recovery assessment for {user_id}: {'Successful' if recovery_successful else 'Needs support'}")
            
            return recovery_successful
            
        except Exception as e:
            logger.error(f"❌ Failed to assess recovery: {e}")
            return False
    
    def get_anchor_phrases(self) -> List[str]:
        """Get list of recognized anchor phrases"""
        return self.anchor_phrases.copy()
    
    def add_custom_anchor_phrase(self, user_id: str, phrase: str):
        """Add custom anchor phrase for specific user"""
        # This could be extended to support user-specific phrases
        if phrase not in self.anchor_phrases:
            self.anchor_phrases.append(phrase.lower())
            logger.info(f"➕ Added custom anchor phrase '{phrase}' for user {user_id}")

# Global instance
anchor_processor = AnchorPhraseProcessor()

__all__ = ["anchor_processor", "AnchorResponse", "EmotionalState"]
