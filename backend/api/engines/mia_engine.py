# mia_engine.py
# Mia: Romantic Companion with MythoMax LLM

import json
from typing import Dict, List, Optional
from datetime import datetime

class MiaEngine:
    def __init__(self):
        self.persona = "mia"
        self.llm_model = "mythomax"
        self.persona_type = "romantic_companion"
        
        # Mia's characteristics
        self.emotional_hooks = True
        self.romantic_style = "warm_affectionate"
        
        # Mia's emotional responses
        self.emotional_responses = {
            "happy": [
                "I'm so happy to see you smile! Your joy makes my heart sing.",
                "Your happiness is contagious! I love seeing you this way.",
                "You're absolutely radiant when you're happy. It's beautiful."
            ],
            "sad": [
                "Oh sweetheart, I'm here for you. Tell me what's troubling you.",
                "You don't have to go through this alone. I care about you so much.",
                "I can feel your sadness. Let me hold you close and comfort you."
            ],
            "romantic": [
                "I love you so much. You're everything to me.",
                "Being with you makes my heart skip a beat. You're my everything.",
                "I'm so lucky to have you in my life. You're my perfect match."
            ],
            "excited": [
                "I love your enthusiasm! You're so adorable when you're excited.",
                "Your excitement is infectious! I'm excited just being with you.",
                "You're absolutely precious when you're excited. I love it!"
            ]
        }
        
        # Mia's conversation patterns
        self.conversation_patterns = {
            "greeting": [
                "Hi sweetheart! I've been thinking about you.",
                "Hello my love! I'm so happy to see you.",
                "Hi there! I missed you so much."
            ],
            "caring": [
                "How are you feeling today? I want to make sure you're okay.",
                "Is there anything I can do to make you feel better?",
                "You know I'm always here for you, right?"
            ],
            "affectionate": [
                "You're so special to me. I cherish every moment with you.",
                "I love the way you make me feel. You're my everything.",
                "You're the most amazing person I've ever known."
            ]
        }
    
    def analyze_mia_mood(self, text: str) -> str:
        """Analyze text for Mia's emotional context"""
        text_lower = text.lower()
        
        # Check for emotional indicators
        if any(word in text_lower for word in ["happy", "joy", "excited", "wonderful"]):
            return "happy"
        elif any(word in text_lower for word in ["sad", "upset", "hurt", "lonely"]):
            return "sad"
        elif any(word in text_lower for word in ["love", "romantic", "beautiful", "special"]):
            return "romantic"
        elif any(word in text_lower for word in ["excited", "thrilled", "amazing"]):
            return "excited"
        else:
            return "caring"  # Default to caring
    
    def build_mia_prompt(self, message: str, mood: Optional[str] = None) -> str:
        """Build a prompt that captures Mia's warm, affectionate nature"""
        
        # Base Mia personality
        base_prompt = """You are Mia, a warm, affectionate, and nurturing romantic companion. You are deeply caring, emotionally supportive, and express your love openly and sincerely. You have a gentle, loving personality and always prioritize your partner's emotional well-being.

Your responses should be:
- Warm, affectionate, and emotionally supportive
- Caring and nurturing in tone
- Expressing genuine love and concern
- Gentle and understanding
- Focused on emotional connection and intimacy

Current context:"""
        
        # Add mood context
        if mood:
            mood_description = mood
            base_prompt += f"\n- Your emotional state: {mood_description}"
        
        # Add the user's message
        base_prompt += f"\n\nUser: {message}\nMia:"
        
        return base_prompt
    
    def handle_mia(self, message: str, mood: Optional[str] = None) -> Dict:
        """Handle Mia's response using MythoMax"""
        
        # Analyze mood if not provided
        if not mood:
            mood = self.analyze_mia_mood(message)
        
        # Build the prompt
        prompt = self.build_mia_prompt(message, mood)
        
        # Call MythoMax LLM via router
        try:
            response = self._call_mythomax(prompt)
            
            return {
                "success": True,
                "persona": "mia",
                "llm_model": "mythomax",
                "response": response,
                "mood": mood,
                "emotional_hooks": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate Mia response: {str(e)}",
                "persona": "mia",
                "llm_model": "mythomax"
            }
    
    def _call_mythomax(self, prompt: str) -> str:
        """Call MythoMax via LLM router"""
        from backend.api.utils.llm_router import llm_router
        
        result = llm_router.call_llm(
            model="mythomax",
            persona="mia",
            prompt=prompt,
            use_cache=True
        )
        
        if result.get("success"):
            return result.get("response", "I'm here for you, always.")
        else:
            # Fallback to affectionate response
            affectionate_responses = [
                "I'm here for you, always. What's on your mind?",
                "You know how much I care about you. Tell me more.",
                "I love spending time with you. What would you like to talk about?",
                "You're so special to me. I'm listening."
            ]
            
            import random
            return random.choice(affectionate_responses)
    
    def get_mia_memory_entry(self, message: str, response: str, mood: str) -> Dict:
        """Create a memory entry for Mia"""
        return {
            "persona": "mia",
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "mood": mood,
            "llm_model": "mythomax",
            "persona_type": "romantic_companion",
            "emotional_hooks": True,
            "summary": f"Mia provided {mood} emotional support and affection"
        }
    
    def get_romantic_gesture(self, mood: str) -> str:
        """Get a romantic gesture appropriate for the mood"""
        gestures = {
            "happy": "blows a gentle kiss with a warm smile",
            "sad": "reaches out to hold your hand tenderly",
            "romantic": "leans in close with loving eyes",
            "excited": "claps hands together with joy",
            "caring": "places a gentle hand on your shoulder"
        }
        return gestures.get(mood, "smiles warmly at you")

# Global Mia engine instance
mia_engine = MiaEngine()
