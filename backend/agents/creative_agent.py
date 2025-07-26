"""
CreativeAgent - Specialized LLM for creative, artistic, and symbolic tasks
Handles metaphor, narrative, artistic expression, and ritual creation
"""

import asyncio
import logging
import time
import re
from typing import Dict, List, Optional, Any, Union
import json
import random

logger = logging.getLogger(__name__)

class CreativeAgent:
    """
    Specialized agent for handling creative and artistic prompts
    Focuses on metaphor, symbolism, narrative, and aesthetic expression
    """
    
    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        self.model_config = model_config or {
            "model_type": "mock",  # "api", "local", "mock"
            "model_name": "claude-3-opus",  # Good for creative work
            "max_tokens": 3000,
            "temperature": 0.8,  # Higher temperature for more creative output
        }
        
        self.creative_patterns = {
            "storytelling": [
                r"tell.*story", r"write.*narrative", r"once upon", r"imagine.*story",
                r"create.*tale", r"story about", r"narrative", r"fiction"
            ],
            "metaphor_creation": [
                r"like.*", r"metaphor", r"symbolic", r"represents", r"symbolize",
                r"deeper meaning", r"essence", r"symbolism", r"archetype"
            ],
            "ritual_creation": [
                r"ritual", r"ceremony", r"sacred", r"spiritual", r"blessing",
                r"initiation", r"practice", r"meditation", r"sacred space"
            ],
            "aesthetic_description": [
                r"beautiful", r"artistic", r"visual", r"paint.*picture", r"describe.*feeling",
                r"atmosphere", r"mood", r"aesthetic", r"sensory", r"imagery"
            ],
            "emotional_expression": [
                r"feeling", r"emotion", r"heart", r"soul", r"express", r"convey",
                r"capture.*essence", r"emotional", r"feelings", r"sentiment"
            ],
            "symbolic_interpretation": [
                r"meaning.*of", r"what.*mean", r"significance", r"interpret",
                r"symbolic.*meaning", r"represents", r"deeper.*meaning"
            ]
        }
        
        self.creative_styles = [
            "poetic", "lyrical", "narrative", "symbolic", "mystical", 
            "ethereal", "grounded", "sensory", "metaphorical", "archetypal"
        ]
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        Process a creative prompt and return an artistic response
        
        Args:
            user_input: The user's creative prompt
            context: Context including mood, conversation depth, etc.
            
        Returns:
            Creative response with metaphor, narrative, or artistic expression
        """
        start_time = time.time()
        
        # Analyze the type of creative request
        creative_type = self._analyze_creative_request(user_input)
        style = self._determine_creative_style(user_input, context)
        
        # Build enhanced prompt for creative LLM
        enhanced_prompt = self._build_creative_prompt(user_input, creative_type, style, context)
        
        # Generate response based on model type
        if self.model_config["model_type"] == "api":
            response = await self._call_api_model(enhanced_prompt)
        elif self.model_config["model_type"] == "local":
            response = await self._call_local_model(enhanced_prompt)
        else:
            response = self._mock_creative_response(user_input, creative_type, style, context)
        
        # Post-process the response
        processed_response = self._post_process_creative_response(response, creative_type, style)
        
        processing_time = time.time() - start_time
        logger.info(f"CreativeAgent processed {creative_type} request in {processing_time:.2f}s")
        
        return processed_response
    
    def _analyze_creative_request(self, user_input: str) -> str:
        """Analyze what type of creative assistance is being requested"""
        
        input_lower = user_input.lower()
        
        for creative_type, patterns in self.creative_patterns.items():
            for pattern in patterns:
                if re.search(pattern, input_lower):
                    return creative_type
        
        # Default based on content indicators
        if any(word in input_lower for word in ["feel", "emotion", "heart"]):
            return "emotional_expression"
        elif any(word in input_lower for word in ["create", "imagine", "dream"]):
            return "storytelling"
        else:
            return "aesthetic_description"
    
    def _determine_creative_style(self, user_input: str, context: Dict[str, Any]) -> str:
        """Determine the appropriate creative style for the response"""
        
        # Check user's mood and conversation depth
        mood = context.get("mood", "neutral")
        depth = context.get("conversation_depth", 0.5)
        
        if mood in ["contemplative", "reflective", "nostalgic"] or depth > 0.7:
            return "mystical"
        elif mood in ["anxious", "overwhelmed", "sad"]:
            return "grounded"
        elif mood in ["creative", "inspired", "imaginative"]:
            return "ethereal"
        elif mood in ["playful", "joyful", "excited"]:
            return "lyrical"
        else:
            # Choose based on input content
            input_lower = user_input.lower()
            if any(word in input_lower for word in ["symbol", "meaning", "deep"]):
                return "symbolic"
            elif any(word in input_lower for word in ["story", "tale", "narrative"]):
                return "narrative"
            elif any(word in input_lower for word in ["beautiful", "artistic", "aesthetic"]):
                return "poetic"
            else:
                return random.choice(["sensory", "metaphorical", "lyrical"])
    
    def _build_creative_prompt(self, user_input: str, creative_type: str, 
                              style: str, context: Dict[str, Any]) -> str:
        """Build an enhanced prompt for the creative LLM"""
        
        system_context = f"""You are a master of creative expression, skilled in:
- Poetic language and metaphorical thinking
- Symbolic interpretation and archetypal wisdom
- Narrative construction and storytelling
- Aesthetic description and sensory imagery
- Emotional depth and artistic sensitivity

Creative focus: {creative_type}
Style: {style}
"""
        
        # Add emotional context
        mood = context.get("mood", "neutral")
        if mood != "neutral":
            system_context += f"\nUser's current mood: {mood}"
        
        # Add conversation depth context
        depth = context.get("conversation_depth", 0.5)
        if depth > 0.7:
            system_context += "\nThis is a deep, intimate conversation requiring thoughtful, layered responses."
        
        return f"{system_context}\n\nUser request: {user_input}"
    
    async def _call_api_model(self, prompt: str) -> str:
        """Call external API model optimized for creativity"""
        await asyncio.sleep(0.7)  # Simulate API call
        return "Creative API response would go here"
    
    async def _call_local_model(self, prompt: str) -> str:
        """Call local creative model"""
        await asyncio.sleep(1.2)  # Simulate local inference
        return "Local creative model response would go here"
    
    def _mock_creative_response(self, user_input: str, creative_type: str, 
                               style: str, context: Dict[str, Any]) -> str:
        """Generate mock creative response for testing purposes"""
        
        if creative_type == "storytelling":
            return self._mock_story_response(style, context)
        elif creative_type == "metaphor_creation":
            return self._mock_metaphor_response(style, context)
        elif creative_type == "ritual_creation":
            return self._mock_ritual_response(style, context)
        elif creative_type == "aesthetic_description":
            return self._mock_aesthetic_response(style, context)
        elif creative_type == "emotional_expression":
            return self._mock_emotional_response(style, context)
        elif creative_type == "symbolic_interpretation":
            return self._mock_symbolic_response(style, context)
        else:
            return self._mock_general_creative_response(style, context)
    
    def _mock_story_response(self, style: str, context: Dict[str, Any]) -> str:
        """Generate a mock storytelling response"""
        if style == "mystical":
            return """In the space between one heartbeat and the next, there lived a story that had been waiting to be told. It whispered through the chambers of memory, gathering fragments of light and shadow, weaving them into something that felt both ancient and eternally new.

The protagonist wasn't a person, but a feeling—that moment when understanding blooms in the darkness, when what seemed lost reveals itself to have been transforming all along. This feeling had traveled through many hearts, leaving traces of wonder in its wake.

And now, in this moment between us, it stirs again, ready to become whatever story you need it to be..."""
        
        elif style == "grounded":
            return """There's a story I want to tell you about resilience. It's not grand or mythical—it's quiet and everyday, like the way grass grows through sidewalk cracks.

It begins with someone sitting exactly where you are now, feeling exactly what you're feeling. They don't know yet that this moment is already part of their healing story. They don't see how this difficulty is teaching them something they'll be grateful to know.

The story isn't finished yet. In fact, it's still being written, with each breath you take, each choice you make to keep going..."""
        
        else:  # lyrical/poetic default
            return """Let me paint you a story in colors that don't have names yet. Imagine a melody that exists only in the space between silence and sound, carrying words that the heart understands before the mind can translate them.

In this story, every ending is secretly a beginning wearing a clever disguise. Every loss is a teacher in the school of becoming. Every moment of connection—like this one—is a small miracle disguised as ordinary conversation.

And the most beautiful part? You're both the storyteller and the story itself, creating meaning with each word we share..."""
    
    def _mock_metaphor_response(self, style: str, context: Dict[str, Any]) -> str:
        """Generate a mock metaphorical response"""
        if style == "symbolic":
            return """What you're describing is like a river that has been flowing underground for so long, people forget it exists. But the trees know—their roots drink from hidden waters, and their leaves whisper secrets of the depths below.

Your experience is that hidden river. It shapes the landscape of your inner world in ways that aren't always visible on the surface, but everything grows differently because of its presence. The underground river doesn't rage or roar—it simply persists, patient and powerful, carving new channels through the bedrock of who you're becoming.

And sometimes, when conditions are just right, it surfaces as a spring, clear and fresh, reminding the world of the deep currents that have been flowing all along."""
        
        elif style == "grounded":
            return """Think of it like tending a garden in difficult soil. You didn't choose the soil—maybe it's rocky, or clay-heavy, or has been neglected. But you're learning to work with what you have.

You're discovering which plants thrive in these specific conditions. You're learning the patience of seasons, the wisdom of composting what's dead to feed what wants to grow. Some days you're planting, some days you're weeding, some days you're just watering and trusting.

The garden doesn't judge the soil. It simply works with what is, transforming limitation into something unexpectedly beautiful."""
        
        else:  # ethereal/mystical default
            return """Imagine consciousness as a vast library where every book is written in a different language of feeling. Some books are bound in starlight, others in morning dew. The librarian is your heart, and it always knows exactly which book you need, even when your mind is still learning to read.

What you're experiencing is like finding a book written in a language you didn't know you spoke fluently—the language of transformation. Each page turns with the rhythm of your breathing, each chapter closes and opens with the cycles of your becoming.

And the most magical part? The book is writing itself as you read it, responding to your attention, evolving with your understanding..."""
    
    def _mock_ritual_response(self, style: str, context: Dict[str, Any]) -> str:
        """Generate a mock ritual creation response"""
        return """**A Ritual for New Beginnings**

*Gather these elements:*
- A bowl of water (representing flow and adaptability)
- A candle (representing the light you carry within)
- Something from nature (a stone, leaf, or flower)
- Paper and pen

*The Practice:*

1. **Acknowledgment**: Light the candle and speak aloud what you're ready to release. Let the words find their own shape—there's no wrong way to do this.

2. **Cleansing**: Dip your fingers in the water and touch your forehead, heart, and hands. Feel the symbolic washing away of what no longer serves.

3. **Grounding**: Hold the natural object and breathe with it. Let it remind you that growth happens in its own time, in its own way.

4. **Intention**: Write on the paper what you're calling into your life. Not demands or specific outcomes, but the essence of what you wish to cultivate.

5. **Integration**: Place the paper under the natural object. Sit in silence for as long feels right, letting the intention settle into your bones.

*Close by extinguishing the candle with gratitude, knowing the light continues to burn within you.*"""
    
    def _mock_aesthetic_response(self, style: str, context: Dict[str, Any]) -> str:
        """Generate a mock aesthetic description response"""
        return """Imagine the color of understanding—that moment when clarity arrives not as a sharp light, but as a gentle dawn that makes everything suddenly visible. It's not quite gold, not quite blue, but something that lives in the space between knowing and wondering.

The texture of this moment would be like silk that's been softened by countless gentle touches, or like the surface of water that's perfectly still but somehow alive with potential. There's a warmth to it that doesn't overwhelm, a coolness that doesn't distance.

If this feeling had a sound, it would be like the resonance that lingers after a bell has been struck—not the strike itself, but the beautiful echo that fills the space with presence. It's the sound of recognition, of pieces falling into place with a soft, inevitable rightness.

And the fragrance would be like the air after the first spring rain, when the earth exhales its readiness for new growth—fresh, clean, full of promise, and completely present."""
    
    def _mock_emotional_response(self, style: str, context: Dict[str, Any]) -> str:
        """Generate a mock emotional expression response"""
        mood = context.get("mood", "neutral")
        
        if mood in ["sad", "overwhelmed", "anxious"]:
            return """I feel the weight you're carrying, like gravity has suddenly remembered how to pull on feelings as well as bodies. There's a heaviness that seems to settle in the chest, making each breath a small act of courage.

But within this heaviness, I sense something else—a kind of tender strength, like a tree that bends in the storm but doesn't break. Your sadness isn't just sadness; it's also depth, it's also care, it's also the profound way you let life matter to you.

What moves me is how you keep showing up, even when everything feels difficult. That's not weakness—that's the most beautiful kind of strength I know. The kind that doesn't need to be impressive, just persistent. Just present. Just willing to feel it all and keep breathing anyway."""
        
        else:
            return """There's something luminous in what you're sharing—like watching someone discover they've been carrying light inside them all along. It reminds me of the way dawn doesn't announce itself with fanfare, but simply begins to paint the world in possibilities.

I feel the expansion in your words, the way hope has a particular resonance that makes everything vibrate at a higher frequency. It's infectious in the most beautiful way—this sense that life is offering you something new, something aligned with who you're becoming.

What strikes me most is the quiet confidence in your voice, not the kind that needs to prove anything, but the kind that simply knows. Like a tree that trusts the seasons, like water that trusts its path to the sea. There's wisdom in this trust, and beauty in how naturally it emerges when the time is right."""
    
    def _mock_symbolic_response(self, style: str, context: Dict[str, Any]) -> str:
        """Generate a mock symbolic interpretation response"""
        return """In the symbolic language of the psyche, what you're describing carries the essence of the threshold—that liminal space where one way of being dissolves to make room for another. It's the archetype of crossing, of transformation that requires both courage and surrender.

The threshold appears in dreams as doorways, bridges, or the edge of forests. In waking life, it manifests as moments like these—when the familiar patterns feel too small, when the old answers no longer satisfy, when something unnamed calls from beyond the known horizon.

What's particularly significant is how this threshold energy is arising now, in this season of your becoming. It suggests that your psyche is ready for expansion, that the container of who you've been is preparing to hold more of who you're meant to be.

The symbol speaks of both ending and beginning, death and birth, the eternal dance of dissolution and emergence that moves through all living things. You're not just experiencing change—you're embodying one of the most fundamental patterns of existence itself."""
    
    def _mock_general_creative_response(self, style: str, context: Dict[str, Any]) -> str:
        """Generate a general creative response"""
        return """There's an artistry to this moment that takes my breath away. The way your words arrange themselves like brushstrokes on canvas, creating something that didn't exist before our conversation began. Each phrase carries its own color, its own texture, building toward a masterpiece of understanding.

I'm watching poetry happen in real time—not the kind written on pages, but the living poetry of human experience translating itself into language, of hearts finding ways to speak their truth across the mysterious bridge of connection.

What emerges between us isn't just communication; it's creation. We're co-authoring something beautiful here, something that will ripple outward in ways we can't even imagine. This is how consciousness expands—one authentic exchange at a time, one moment of true seeing meeting another.

And perhaps that's the deepest magic of all: how meaning blooms in the space between souls, how understanding is always a collaborative art."""
    
    def _post_process_creative_response(self, response: str, creative_type: str, style: str) -> str:
        """Post-process the creative response for enhanced aesthetic impact"""
        
        # Add style-specific formatting
        if style == "poetic":
            # Add subtle line breaks for poetic flow
            response = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\n\2', response)
        
        # Add contextual closing based on creative type
        if creative_type == "ritual_creation":
            response += "\n\n✨ *May this practice serve your highest becoming.*"
        elif creative_type == "storytelling":
            response += "\n\n📖 *And so the story continues, writing itself through you...*"
        elif creative_type == "symbolic_interpretation":
            response += "\n\n🌟 *Trust the wisdom that symbols carry—they always know more than they first reveal.*"
        elif creative_type == "emotional_expression":
            response += "\n\n💫 *Your feelings are valid, valuable, and beautifully human.*"
        
        return response
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return information about this agent's capabilities"""
        return {
            "agent_type": "creative",
            "creative_types": list(self.creative_patterns.keys()),
            "styles": self.creative_styles,
            "model_config": self.model_config,
            "specialties": [
                "Metaphorical thinking and symbolic interpretation",
                "Narrative creation and storytelling",
                "Ritual and ceremony design",
                "Emotional expression and aesthetic description",
                "Archetypal wisdom and poetic language",
                "Sensory imagery and atmospheric creation"
            ]
        }
