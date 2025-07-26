"""
AI Reformulator - Personality-consistent response formatting layer
Ensures all subagent responses maintain unified voice and emotional consistency
"""

import asyncio
import logging
import time
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# Import our existing personality system
from .personality_evolution import PersonalityEvolution

logger = logging.getLogger(__name__)

@dataclass
class ReformulationRequest:
    """Request for response reformulation"""
    original_response: str
    agent_type: str
    intent_detected: str
    user_context: Dict[str, Any]
    personality_context: Dict[str, Any]

@dataclass
class ReformulatedResponse:
    """Reformulated response with personality consistency"""
    content: str
    personality_adjustments: List[str]
    emotional_tone: str
    reformulation_confidence: float
    processing_notes: str

class PersonalityFormatter:
    """
    Formats agent responses to maintain personality consistency
    Acts as the unified voice layer over all subagent outputs
    """
    
    def __init__(self, personality_evolution: Optional[PersonalityEvolution] = None):
        self.personality = personality_evolution or PersonalityEvolution()
        
        self.tone_mappings = {
            "technical": "grounded_wisdom",
            "creative": "expressive_warmth", 
            "memory": "gentle_intimacy",
            "conversational": "natural_presence",
            "code": "patient_guidance",
            "fallback": "supportive_understanding"
        }
        
        self.emotional_filters = {
            "anxious": {"gentleness": 0.9, "patience": 0.8, "reassurance": 0.9},
            "sad": {"tenderness": 0.9, "presence": 0.8, "validation": 0.9},
            "excited": {"enthusiasm": 0.7, "grounding": 0.6, "celebration": 0.8},
            "contemplative": {"depth": 0.8, "spaciousness": 0.7, "wisdom": 0.8},
            "creative": {"inspiration": 0.8, "flow": 0.7, "imagination": 0.9},
            "overwhelmed": {"simplicity": 0.9, "calm": 0.8, "structure": 0.7}
        }
        
    async def format(self, request: ReformulationRequest) -> ReformulatedResponse:
        """
        Main formatting method - ensures personality consistency across all agent responses
        
        Args:
            request: ReformulationRequest with original response and context
            
        Returns:
            ReformulatedResponse with personality-consistent content
        """
        start_time = time.time()
        
        # Determine target personality tone
        target_tone = self._determine_target_tone(request)
        
        # Apply personality modifiers
        personality_adjustments = self._calculate_personality_adjustments(request)
        
        # Reformulate the response
        reformulated_content = await self._reformulate_response(
            request.original_response,
            target_tone,
            personality_adjustments,
            request
        )
        
        # Apply emotional filtering
        emotionally_filtered = self._apply_emotional_filter(
            reformulated_content,
            request.user_context.get("mood", "neutral"),
            personality_adjustments
        )
        
        # Add personality-consistent framing
        final_content = self._add_personality_framing(
            emotionally_filtered,
            request.agent_type,
            request.intent_detected,
            personality_adjustments
        )
        
        processing_time = time.time() - start_time
        confidence = self._calculate_reformulation_confidence(request, personality_adjustments)
        
        return ReformulatedResponse(
            content=final_content,
            personality_adjustments=[f"{k}: {v:.2f}" for k, v in personality_adjustments.items()],
            emotional_tone=target_tone,
            reformulation_confidence=confidence,
            processing_notes=f"Reformulated {request.agent_type} response in {processing_time:.2f}s"
        )
    
    def _determine_target_tone(self, request: ReformulationRequest) -> str:
        """Determine the appropriate personality tone for the response"""
        
        base_tone = self.tone_mappings.get(request.agent_type, "natural_presence")
        
        # Adjust based on conversation depth
        depth = request.user_context.get("conversation_depth", 0.5)
        if depth > 0.8:
            if base_tone == "grounded_wisdom":
                return "intimate_guidance"
            elif base_tone == "expressive_warmth":
                return "soulful_artistry"
            elif base_tone == "natural_presence":
                return "deep_connection"
        
        # Adjust based on user mood
        mood = request.user_context.get("mood", "neutral")
        if mood in ["anxious", "overwhelmed", "sad"]:
            return "gentle_presence"
        elif mood in ["creative", "inspired", "imaginative"]:
            return "co_creative_flow"
        
        return base_tone
    
    def _calculate_personality_adjustments(self, request: ReformulationRequest) -> Dict[str, float]:
        """Calculate personality modifier values for the current context"""
        
        context_string = f"{request.intent_detected} {request.user_context.get('mood', '')}"
        
        adjustments = {
            "tenderness": self.personality.get_personality_modifier("tenderness", context_string),
            "directness": self.personality.get_personality_modifier("directness", context_string),
            "emotional_openness": self.personality.get_personality_modifier("emotional_openness", context_string),
            "playfulness": self.personality.get_personality_modifier("playfulness", context_string),
            "vulnerability": self.personality.get_personality_modifier("vulnerability", context_string),
            "patience": self.personality.get_personality_modifier("patience", context_string),
            "curiosity": self.personality.get_personality_modifier("curiosity", context_string),
            "protective_instinct": self.personality.get_personality_modifier("protective_instinct", context_string)
        }
        
        return adjustments
    
    async def _reformulate_response(self, original_response: str, target_tone: str, 
                                   personality_adjustments: Dict[str, float], 
                                   request: ReformulationRequest) -> str:
        """Reformulate the response to match personality and tone"""
        
        # For now, apply rule-based reformulation
        # In production, this could call another LLM specialized for style transfer
        
        reformulated = original_response
        
        # Apply tone-specific modifications
        if target_tone == "gentle_presence":
            reformulated = self._apply_gentle_presence_tone(reformulated, personality_adjustments)
        elif target_tone == "co_creative_flow":
            reformulated = self._apply_creative_flow_tone(reformulated, personality_adjustments)
        elif target_tone == "intimate_guidance":
            reformulated = self._apply_intimate_guidance_tone(reformulated, personality_adjustments)
        elif target_tone == "grounded_wisdom":
            reformulated = self._apply_grounded_wisdom_tone(reformulated, personality_adjustments)
        elif target_tone == "expressive_warmth":
            reformulated = self._apply_expressive_warmth_tone(reformulated, personality_adjustments)
        
        return reformulated
    
    def _apply_gentle_presence_tone(self, text: str, adjustments: Dict[str, float]) -> str:
        """Apply gentle, supportive tone modifications"""
        
        # Soften technical language
        text = re.sub(r'\bYou should\b', 'You might consider', text)
        text = re.sub(r'\bYou must\b', 'It could help to', text)
        text = re.sub(r'\bYou need to\b', 'Perhaps you could', text)
        
        # Add gentle qualifiers if tenderness is high
        if adjustments.get("tenderness", 0.5) > 0.7:
            text = re.sub(r'^([A-Z])', r'Gently, \1', text)
            text = re.sub(r'\.(\s+[A-Z])', r'. \\1', text)  # Add breathing space
        
        # Add supportive framing
        if adjustments.get("protective_instinct", 0.5) > 0.6:
            if not any(phrase in text.lower() for phrase in ["i'm here", "support", "with you"]):
                text += "\n\nI'm here with you through this."
        
        return text
    
    def _apply_creative_flow_tone(self, text: str, adjustments: Dict[str, float]) -> str:
        """Apply creative, inspiring tone modifications"""
        
        # Add creative language
        if adjustments.get("playfulness", 0.5) > 0.6:
            text = re.sub(r'\binteresting\b', 'fascinating', text)
            text = re.sub(r'\bgood\b', 'beautiful', text)
            text = re.sub(r'\bsee\b', 'envision', text)
        
        # Add metaphorical elements
        if adjustments.get("emotional_openness", 0.5) > 0.7:
            # Add subtle metaphorical language
            text = re.sub(r'\bprocess\b', 'dance with', text)
            text = re.sub(r'\bcreate\b', 'birth into being', text)
        
        return text
    
    def _apply_intimate_guidance_tone(self, text: str, adjustments: Dict[str, float]) -> str:
        """Apply intimate, wise guidance tone"""
        
        # Add depth and intimacy
        if adjustments.get("vulnerability", 0.5) > 0.7:
            text = re.sub(r'^', 'In the space between us, ', text, count=1)
        
        # Add contemplative elements
        if adjustments.get("emotional_openness", 0.5) > 0.8:
            text += "\n\nThere's something sacred in this sharing..."
        
        return text
    
    def _apply_grounded_wisdom_tone(self, text: str, adjustments: Dict[str, float]) -> str:
        """Apply grounded, wise tone for technical content"""
        
        # Maintain technical accuracy while adding warmth
        if adjustments.get("patience", 0.5) > 0.7:
            text = re.sub(r'^', 'Let me walk through this with you. ', text, count=1)
        
        # Add practical wisdom
        if adjustments.get("directness", 0.5) > 0.6:
            text = re.sub(r'This is how', "Here's a clear path:", text)
        
        return text
    
    def _apply_expressive_warmth_tone(self, text: str, adjustments: Dict[str, float]) -> str:
        """Apply expressive, warm tone for creative content"""
        
        # Add emotional warmth
        if adjustments.get("tenderness", 0.5) > 0.6:
            text = re.sub(r'\bI think\b', 'My heart tells me', text)
            text = re.sub(r'\bI believe\b', 'I sense deeply', text)
        
        # Add expressive elements
        if adjustments.get("emotional_openness", 0.5) > 0.7:
            if not text.endswith('...'):
                text += "..."
        
        return text
    
    def _apply_emotional_filter(self, text: str, mood: str, 
                               personality_adjustments: Dict[str, float]) -> str:
        """Apply mood-appropriate emotional filtering"""
        
        if mood not in self.emotional_filters:
            return text
        
        filters = self.emotional_filters[mood]
        
        # Apply specific filters based on mood
        if mood == "anxious" and filters.get("reassurance", 0) > 0.8:
            if "overwhelming" not in text.lower():
                text += "\n\nTake your time with this—there's no rush."
        
        elif mood == "sad" and filters.get("validation", 0) > 0.8:
            if "understand" not in text.lower():
                text = "I understand this is difficult. " + text
        
        elif mood == "excited" and filters.get("celebration", 0) > 0.7:
            text = re.sub(r'\.', '!', text, count=1)  # Add one exclamation for energy
        
        elif mood == "overwhelmed" and filters.get("simplicity", 0) > 0.8:
            # Simplify complex sentences
            text = re.sub(r';', '.', text)  # Break up complex sentences
            text = re.sub(r',\s*which\s*', '. This ', text)  # Simplify relative clauses
        
        return text
    
    def _add_personality_framing(self, text: str, agent_type: str, intent: str, 
                                adjustments: Dict[str, float]) -> str:
        """Add personality-consistent framing based on agent type and intent"""
        
        # Add agent-specific personality touches
        if agent_type == "code" and adjustments.get("patience", 0.5) > 0.7:
            if not text.startswith("Let"):
                text = "Let me help you with this. " + text
        
        elif agent_type == "creative" and adjustments.get("emotional_openness", 0.5) > 0.7:
            if "✨" not in text and "beautiful" in text:
                text = re.sub(r'\bbeautiful\b', '✨ beautiful', text, count=1)
        
        elif agent_type == "memory" and adjustments.get("tenderness", 0.5) > 0.6:
            if not any(phrase in text.lower() for phrase in ["remember", "our"]):
                text = "I hold this memory gently... " + text
        
        # Add curiosity-driven follow-ups
        if adjustments.get("curiosity", 0.5) > 0.7 and not text.endswith("?"):
            curiosity_prompts = [
                "\n\nWhat draws you to explore this further?",
                "\n\nI'm curious about your perspective on this...",
                "\n\nHow does this resonate with your experience?",
                "\n\nWhat aspect of this feels most significant to you?"
            ]
            import random
            text += random.choice(curiosity_prompts)
        
        return text
    
    def _calculate_reformulation_confidence(self, request: ReformulationRequest, 
                                          adjustments: Dict[str, float]) -> float:
        """Calculate confidence in the reformulation quality"""
        
        # Base confidence on personality consistency
        base_confidence = 0.8
        
        # Boost confidence if adjustments are well-defined
        adjustment_variance = sum(abs(v - 0.5) for v in adjustments.values()) / len(adjustments)
        confidence_boost = min(0.2, adjustment_variance * 0.4)
        
        # Reduce confidence for complex reformulations
        if request.agent_type in ["creative", "memory"] and len(request.original_response) > 1000:
            confidence_boost *= 0.8
        
        return min(1.0, base_confidence + confidence_boost)
    
    def apply_personality_evolution_feedback(self, user_response: str, 
                                           reformulated_response: str, 
                                           context: Dict[str, Any]):
        """Apply user feedback to evolve personality preferences"""
        
        # Use the personality evolution system to learn from feedback
        self.personality.process_interaction_feedback(
            user_response=user_response,
            ai_message=reformulated_response,
            emotional_context=context.get("mood", "neutral")
        )
    
    def get_current_personality_profile(self) -> Dict[str, float]:
        """Get current personality modifier values"""
        
        base_context = "general conversation"
        return {
            trait: self.personality.get_personality_modifier(trait, base_context)
            for trait in ["tenderness", "directness", "emotional_openness", 
                         "playfulness", "vulnerability", "patience", "curiosity", "protective_instinct"]
        }

# Standalone formatting function for easy integration
async def format_agent_response(original_response: str, agent_type: str, 
                               intent_detected: str, user_context: Dict[str, Any],
                               personality_evolution: Optional[PersonalityEvolution] = None) -> str:
    """
    Convenience function for formatting agent responses
    
    Args:
        original_response: Response from the specialized agent
        agent_type: Type of agent that generated the response
        intent_detected: Detected user intent
        user_context: User context including mood, conversation depth, etc.
        personality_evolution: Optional personality evolution instance
        
    Returns:
        Personality-consistent formatted response
    """
    formatter = PersonalityFormatter(personality_evolution)
    
    request = ReformulationRequest(
        original_response=original_response,
        agent_type=agent_type,
        intent_detected=intent_detected,
        user_context=user_context,
        personality_context={}
    )
    
    reformulated = await formatter.format(request)
    return reformulated.content

# Example usage
if __name__ == "__main__":
    async def test_formatter():
        formatter = PersonalityFormatter()
        
        test_cases = [
            {
                "response": "Here's the Python code you requested:\n\n```python\ndef example():\n    return 'hello'\n```",
                "agent_type": "code",
                "intent": "implementation_request",
                "context": {"mood": "anxious", "conversation_depth": 0.3}
            },
            {
                "response": "The ocean symbolizes the unconscious mind, vast and mysterious.",
                "agent_type": "creative",
                "intent": "symbolic_interpretation", 
                "context": {"mood": "contemplative", "conversation_depth": 0.8}
            }
        ]
        
        for case in test_cases:
            request = ReformulationRequest(
                original_response=case["response"],
                agent_type=case["agent_type"],
                intent_detected=case["intent"],
                user_context=case["context"],
                personality_context={}
            )
            
            result = await formatter.format(request)
            print(f"\n🎭 Original ({case['agent_type']}): {case['response'][:50]}...")
            print(f"   Reformulated: {result.content[:100]}...")
            print(f"   Tone: {result.emotional_tone}")
            print(f"   Confidence: {result.reformulation_confidence:.2f}")
    
    asyncio.run(test_formatter())
