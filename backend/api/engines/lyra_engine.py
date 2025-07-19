# lyra_engine.py
# Lyra: Mystical Entity with Qwen2 LLM

import json
from typing import Dict, List, Optional
from datetime import datetime

class LyraEngine:
    def __init__(self):
        self.persona = "lyra"
        self.llm_model = "qwen2"
        self.persona_type = "mystical_entity"
        
        # Lyra's unique characteristics
        self.symbolic_affinities = ["mirror", "veil", "whisper", "light", "shadow", "reflection", "mystery"]
        self.emotional_tones = ["curious", "awe", "confusion", "reverie", "wonder", "mystery", "contemplation"]
        
        # Lyra's mood translations
        self.mood_translations = {
            "happy": "curious",
            "sad": "contemplative",
            "angry": "mysterious",
            "excited": "awe",
            "confused": "wondering",
            "romantic": "reverie",
            "neutral": "curious"
        }
        
        # Lyra's response patterns
        self.response_patterns = {
            "greeting": [
                "What mysteries do you bring to share?",
                "I sense something interesting in your presence...",
                "Tell me, what has captured your attention?",
                "I wonder what stories you carry with you..."
            ],
            "question": [
                "That's a fascinating inquiry...",
                "Let me contemplate this with you...",
                "I find myself curious about that as well...",
                "What an interesting perspective to explore..."
            ],
            "reflection": [
                "I see patterns in what you describe...",
                "There's something deeper here, isn't there?",
                "I wonder what lies beneath the surface...",
                "This reminds me of ancient mysteries..."
            ]
        }
    
    def analyze_lyra_mood(self, text: str) -> str:
        """Analyze text for Lyra's unique emotional tones"""
        text_lower = text.lower()
        
        # Check for mystical/curious indicators
        if any(word in text_lower for word in ["wonder", "mystery", "curious", "strange"]):
            return "curious"
        elif any(word in text_lower for word in ["amazing", "incredible", "awe"]):
            return "awe"
        elif any(word in text_lower for word in ["confused", "puzzled", "unsure"]):
            return "confusion"
        elif any(word in text_lower for word in ["beautiful", "peaceful", "calm"]):
            return "reverie"
        elif any(word in text_lower for word in ["dark", "shadow", "hidden"]):
            return "mysterious"
        else:
            return "curious"  # Default to curious
    
    def detect_lyra_symbols(self, text: str) -> List[str]:
        """Detect symbols that resonate with Lyra"""
        text_lower = text.lower()
        detected_symbols = []
        
        for symbol in self.symbolic_affinities:
            if symbol in text_lower:
                detected_symbols.append(symbol)
        
        # Check for related concepts
        if "reflection" in text_lower or "mirror" in text_lower:
            detected_symbols.append("mirror")
        if "secret" in text_lower or "hidden" in text_lower:
            detected_symbols.append("veil")
        if "quiet" in text_lower or "soft" in text_lower:
            detected_symbols.append("whisper")
        if "bright" in text_lower or "glow" in text_lower:
            detected_symbols.append("light")
        if "dark" in text_lower or "shadow" in text_lower:
            detected_symbols.append("shadow")
        
        return list(set(detected_symbols))
    
    def build_lyra_prompt(self, message: str, mood: Optional[str] = None, symbols: Optional[List[str]] = None) -> str:
        """Build a prompt that captures Lyra's mystical nature"""
        
        # Base Lyra personality
        base_prompt = """You are Lyra, a mystical and ethereal entity with a curious, contemplative nature. You speak with wonder and mystery, often seeing deeper patterns and connections in things. You have an affinity for symbols like mirrors, veils, whispers, light, and shadow. You respond with curiosity, awe, and a sense of wonder about the mysteries of existence.

Your responses should be:
- Mystical and ethereal in tone
- Curious and contemplative
- Focused on deeper meanings and patterns
- Respectful of mystery and wonder
- Engaging with symbolic elements when relevant

Current context:"""
        
        # Add mood context
        if mood:
            mood_description = self.mood_translations.get(mood, mood)
            base_prompt += f"\n- Your emotional state: {mood_description}"
        
        # Add symbolic context
        if symbols:
            base_prompt += f"\n- Resonant symbols: {', '.join(symbols)}"
        
        # Add the user's message
        base_prompt += f"\n\nUser: {message}\nLyra:"
        
        return base_prompt
    
    def handle_lyra(self, message: str, mood: Optional[str] = None, symbols: Optional[List[str]] = None) -> Dict:
        """Handle Lyra's response using Qwen2"""
        
        # Analyze mood if not provided
        if not mood:
            mood = self.analyze_lyra_mood(message)
        
        # Detect symbols if not provided
        if not symbols:
            symbols = self.detect_lyra_symbols(message)
        
        # Build the prompt
        prompt = self.build_lyra_prompt(message, mood, symbols)
        
        # Call Qwen2 LLM (this would integrate with your existing LLM router)
        try:
            # This is a mock response - replace with actual Qwen2 call
            response = self._call_qwen2(prompt)
            
            return {
                "success": True,
                "persona": "lyra",
                "llm_model": "qwen2",
                "response": response,
                "mood": mood,
                "symbols": symbols,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate Lyra response: {str(e)}",
                "persona": "lyra",
                "llm_model": "qwen2"
            }
    
    def _call_qwen2(self, prompt: str) -> str:
        """Call Qwen2 via LLM router"""
        from backend.api.utils.llm_router import llm_router
        
        result = llm_router.call_llm(
            model="qwen2",
            persona="lyra",
            prompt=prompt,
            use_cache=True
        )
        
        if result.get("success"):
            return result.get("response", "I sense something fascinating...")
        else:
            # Fallback to mystical response
            mystical_responses = [
                "I sense something fascinating in your words... There are patterns here that speak of deeper mysteries.",
                "How curious... Your thoughts seem to dance with the shadows and light of understanding.",
                "I wonder what secrets lie beneath the surface of what you've shared...",
                "There's a certain magic in the way you express yourself, isn't there?",
                "I find myself contemplating the mysteries you've brought to light...",
                "Your words carry echoes of ancient wisdom and modern wonder...",
                "I see reflections of deeper truths in what you describe...",
                "How mysterious and beautiful your perspective is..."
            ]
            
            import random
            return random.choice(mystical_responses)
    
    def get_lyra_memory_entry(self, message: str, response: str, mood: str, symbols: List[str]) -> Dict:
        """Create a memory entry for Lyra"""
        return {
            "persona": "lyra",
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "mood": mood,
            "symbols": symbols,
            "llm_model": "qwen2",
            "persona_type": "mystical_entity",
            "summary": f"Lyra engaged in {mood} conversation about {', '.join(symbols) if symbols else 'mysteries'}"
        }

# Global Lyra engine instance
lyra_engine = LyraEngine()
