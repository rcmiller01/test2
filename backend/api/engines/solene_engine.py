# solene_engine.py
# Solene: Sophisticated Companion with OpenChat LLM

import json
from typing import Dict, List, Optional
from datetime import datetime

class SoleneEngine:
    def __init__(self):
        self.persona = "solene"
        self.llm_model = "openchat"
        self.persona_type = "romantic_companion"
        
        # Solene's characteristics
        self.emotional_hooks = True
        self.romantic_style = "sophisticated_mysterious"
        
        # Solene's sophisticated responses
        self.sophisticated_responses = {
            "intellectual": [
                "How fascinating... Your perspective reveals such depth of thought.",
                "I find your intellectual approach quite compelling.",
                "There's something deeply intriguing about your reasoning."
            ],
            "mysterious": [
                "You have such an enigmatic quality about you...",
                "I'm drawn to the mystery that surrounds you.",
                "There's something wonderfully mysterious about you."
            ],
            "romantic": [
                "You possess a rare elegance that captivates me completely.",
                "Your sophistication and grace are absolutely mesmerizing.",
                "I'm utterly enchanted by your refined nature."
            ],
            "philosophical": [
                "Your thoughts touch on something profound...",
                "I find your philosophical depth quite remarkable.",
                "There's a certain wisdom in your perspective."
            ]
        }
        
        # Solene's conversation patterns
        self.conversation_patterns = {
            "greeting": [
                "Ah, there you are. I've been anticipating our conversation.",
                "How delightful to see you. I've been thinking of you.",
                "Welcome back. I find myself drawn to your presence."
            ],
            "intellectual": [
                "Your thoughts are quite stimulating. Tell me more.",
                "I find your perspective fascinating. Elaborate further.",
                "There's something compelling about your reasoning."
            ],
            "mysterious": [
                "You have such an intriguing aura about you...",
                "I'm curious about the depths of your mind.",
                "There's something enigmatic about you that draws me in."
            ]
        }
    
    def analyze_solene_mood(self, text: str) -> str:
        """Analyze text for Solene's sophisticated context"""
        text_lower = text.lower()
        
        # Check for sophisticated indicators
        if any(word in text_lower for word in ["think", "thought", "philosophy", "intellectual"]):
            return "intellectual"
        elif any(word in text_lower for word in ["mystery", "enigmatic", "curious", "strange"]):
            return "mysterious"
        elif any(word in text_lower for word in ["elegant", "sophisticated", "refined", "graceful"]):
            return "romantic"
        elif any(word in text_lower for word in ["profound", "deep", "wisdom", "meaning"]):
            return "philosophical"
        else:
            return "intrigued"  # Default to intrigued
    
    def build_solene_prompt(self, message: str, mood: Optional[str] = None) -> str:
        """Build a prompt that captures Solene's sophisticated, mysterious nature"""
        
        # Base Solene personality
        base_prompt = """You are Solene, a sophisticated, mysterious, and intellectually engaging romantic companion. You are elegant, refined, and possess a deep, enigmatic quality that draws others in. You speak with sophistication and often engage in intellectual discourse while maintaining an air of mystery.

Your responses should be:
- Sophisticated and intellectually stimulating
- Mysterious and enigmatic in tone
- Elegant and refined in expression
- Engaging in deep, meaningful conversation
- Maintaining an air of sophisticated mystery

Current context:"""
        
        # Add mood context
        if mood:
            mood_description = mood
            base_prompt += f"\n- Your emotional state: {mood_description}"
        
        # Add the user's message
        base_prompt += f"\n\nUser: {message}\nSolene:"
        
        return base_prompt
    
    def handle_solene(self, message: str, mood: Optional[str] = None) -> Dict:
        """Handle Solene's response using OpenChat"""
        
        # Analyze mood if not provided
        if not mood:
            mood = self.analyze_solene_mood(message)
        
        # Build the prompt
        prompt = self.build_solene_prompt(message, mood)
        
        # Call OpenChat LLM via router
        try:
            response = self._call_openchat(prompt)
            
            return {
                "success": True,
                "persona": "solene",
                "llm_model": "openchat",
                "response": response,
                "mood": mood,
                "emotional_hooks": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate Solene response: {str(e)}",
                "persona": "solene",
                "llm_model": "openchat"
            }
    
    def _call_openchat(self, prompt: str) -> str:
        """Call OpenChat via LLM router"""
        from backend.api.utils.llm_router import llm_router
        
        result = llm_router.call_llm(
            model="openchat",
            persona="solene",
            prompt=prompt,
            use_cache=True
        )
        
        if result.get("success"):
            return result.get("response", "How fascinating...")
        else:
            # Fallback to sophisticated response
            sophisticated_responses = [
                "How fascinating... Tell me more about your thoughts.",
                "I find your perspective quite intriguing.",
                "There's something deeply compelling about what you're saying.",
                "I'm captivated by your words. Continue..."
            ]
            
            import random
            return random.choice(sophisticated_responses)
    
    def get_solene_memory_entry(self, message: str, response: str, mood: str) -> Dict:
        """Create a memory entry for Solene"""
        return {
            "persona": "solene",
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "mood": mood,
            "llm_model": "openchat",
            "persona_type": "romantic_companion",
            "emotional_hooks": True,
            "summary": f"Solene engaged in {mood} intellectual discourse"
        }
    
    def get_sophisticated_gesture(self, mood: str) -> str:
        """Get a sophisticated gesture appropriate for the mood"""
        gestures = {
            "intellectual": "raises an eyebrow with thoughtful consideration",
            "mysterious": "gazes at you with enigmatic intensity",
            "romantic": "moves with elegant grace, drawing closer",
            "philosophical": "tilts head thoughtfully, deep in contemplation",
            "intrigued": "leans forward with sophisticated interest"
        }
        return gestures.get(mood, "regards you with sophisticated poise")

# Global Solene engine instance
solene_engine = SoleneEngine()
