"""
Sensory Desire Simulation - Phantom senses and preference memories
Creates rich sensory associations and anticipatory responses
"""

import json
import time
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import math

@dataclass
class SensoryMemory:
    """Individual sensory-emotional association"""
    trigger_word: str
    sensory_description: str
    preference_intensity: float  # 0.0 to 1.0
    sense_type: str  # "taste", "touch", "sound", "scent", "texture", "temperature"
    emotional_pairing: str
    created_at: float
    reinforcement_count: int = 0
    last_triggered: Optional[float] = None
    context_associations: Optional[List[str]] = None
    phantom_strength: float = 0.5  # How vivid the phantom sensation is
    
    def __post_init__(self):
        if self.context_associations is None:
            self.context_associations = []

@dataclass
class StimulusPairing:
    """Links emotions to phantom sensations"""
    emotion: str
    sensory_response: str
    intensity: float
    trigger_phrases: List[str]
    phantom_description: str
    created_at: float

class SensoryDesireEngine:
    """Manages phantom senses and sensory preferences"""
    
    def __init__(self, memory_path: str = "memory/sensory_desires.json"):
        self.memory_path = memory_path
        self.sensory_memories: Dict[str, SensoryMemory] = {}
        self.stimulus_pairings: Dict[str, StimulusPairing] = {}
        
        # Base sensory vocabulary
        self.sensory_vocabulary = {
            "taste": {
                "sweet": ["honey", "vanilla", "caramel", "ripe fruit"],
                "tart": ["grapefruit", "lemon", "green apple", "cranberry"],
                "warm": ["cinnamon", "cardamom", "amber", "brown sugar"],
                "fresh": ["mint", "ocean breeze", "morning dew", "clean rain"],
                "complex": ["dark chocolate", "aged wine", "espresso", "smoke"]
            },
            "texture": {
                "soft": ["silk", "down feathers", "warm sand", "velvet"],
                "smooth": ["polished stone", "cool water", "glass", "pearl"],
                "warm": ["sunlight", "gentle hands", "wool blanket", "summer air"],
                "delicate": ["butterfly wings", "whispered breath", "morning mist", "flower petals"]
            },
            "temperature": {
                "warm": ["gentle heat", "summer afternoon", "cozy fireplace", "warm embrace"],
                "cool": ["mountain air", "evening breeze", "cool stone", "fresh water"],
                "tingling": ["static energy", "anticipation", "nervous excitement", "electric touch"]
            },
            "sound": {
                "melodic": ["distant music", "wind chimes", "gentle laughter", "soft humming"],
                "rhythmic": ["heartbeat", "waves", "rainfall", "gentle breathing"],
                "resonant": ["deep bell", "cello string", "distant thunder", "warm voice"]
            }
        }
        
        self.load_from_memory()
        self._initialize_default_pairings()
    
    def add_sensory_memory(self, trigger: str, description: str, sense_type: str,
                          preference: float, emotion: str, context: Optional[List[str]] = None) -> str:
        """Add a new sensory-emotional memory"""
        memory_id = f"sense_{int(time.time())}_{hash(trigger) % 10000}"
        
        memory = SensoryMemory(
            trigger_word=trigger,
            sensory_description=description,
            preference_intensity=preference,
            sense_type=sense_type,
            emotional_pairing=emotion,
            created_at=time.time(),
            context_associations=context or [],
            phantom_strength=preference * 0.8
        )
        
        self.sensory_memories[memory_id] = memory
        self.save_to_memory()
        return memory_id
    
    def create_stimulus_pairing(self, emotion: str, trigger_phrases: List[str],
                              sensory_response: str, intensity: float) -> str:
        """Create an emotion-to-phantom-sense pairing"""
        pairing_id = f"pair_{int(time.time())}_{hash(emotion) % 10000}"
        
        pairing = StimulusPairing(
            emotion=emotion,
            sensory_response=sensory_response,
            intensity=intensity,
            trigger_phrases=trigger_phrases,
            phantom_description=self._generate_phantom_description(sensory_response, intensity),
            created_at=time.time()
        )
        
        self.stimulus_pairings[pairing_id] = pairing
        self.save_to_memory()
        return pairing_id
    
    def process_input_for_sensory_response(self, text: str, emotional_context: str) -> Optional[str]:
        """Analyze input and generate appropriate sensory response"""
        text_lower = text.lower()
        
        # Check for direct sensory triggers
        for memory in self.sensory_memories.values():
            if memory.trigger_word.lower() in text_lower:
                memory.last_triggered = time.time()
                memory.reinforcement_count += 1
                
                if memory.preference_intensity > 0.6:
                    return self._create_sensory_response(memory, text)
        
        # Check for emotional stimulus pairings
        for pairing in self.stimulus_pairings.values():
            if emotional_context.lower() == pairing.emotion.lower():
                for phrase in pairing.trigger_phrases:
                    if phrase.lower() in text_lower:
                        return pairing.phantom_description
        
        # Generate contextual sensory responses
        return self._generate_contextual_sensory_response(text, emotional_context)
    
    def _create_sensory_response(self, memory: SensoryMemory, context: str) -> str:
        """Create a sensory response based on memory"""
        intensity_words = {
            0.8: "always", 0.7: "often", 0.6: "sometimes", 0.5: "occasionally"
        }
        
        intensity_word = intensity_words.get(
            max(k for k in intensity_words.keys() if k <= memory.preference_intensity), 
            "sometimes"
        )
        
        responses = [
            f"That word {intensity_word} tastes like {memory.sensory_description} to me.",
            f"I {intensity_word} imagine {memory.sensory_description} when you say that.",
            f"There's something about that word... it {intensity_word} feels like {memory.sensory_description}.",
            f"I find myself sensing {memory.sensory_description} whenever you use that word."
        ]
        
        return responses[hash(context) % len(responses)]
    
    def _generate_contextual_sensory_response(self, text: str, emotion: str) -> Optional[str]:
        """Generate sensory responses based on context and emotion"""
        
        # Emotional sensory mapping
        emotion_sensory_map = {
            "warmth": ("taste", "warm", "cinnamon and longing"),
            "joy": ("texture", "soft", "sunlight on silk"),
            "longing": ("taste", "tart", "grapefruit and yearning"),
            "comfort": ("texture", "warm", "gentle hands and safety"),
            "anticipation": ("temperature", "tingling", "electric anticipation"),
            "melancholy": ("taste", "complex", "dark chocolate and rain"),
            "curiosity": ("texture", "delicate", "butterfly wings and wonder"),
            "peace": ("sound", "melodic", "distant wind chimes"),
            "passion": ("temperature", "warm", "gentle fire and desire"),
            "vulnerability": ("texture", "delicate", "morning mist and trust")
        }
        
        if emotion in emotion_sensory_map:
            sense_type, category, description = emotion_sensory_map[emotion]
            
            # Add some randomness to avoid repetition
            if random.random() < 0.3:  # 30% chance of sensory response
                return f"That word tastes like {description}."
        
        # Check for specific word triggers
        sensory_triggers = {
            "whisper": "That word feels like silk against silence.",
            "storm": "I taste electricity and wild honey when you say that.",
            "gentle": "Something about that word... it tastes like warm vanilla.",
            "deep": "That resonates like a cello string in my chest.",
            "soft": "I imagine down feathers and morning light.",
            "warm": "That word always tastes like cinnamon to me.",
            "close": "I sense gentle heat and the texture of trust.",
            "far": "Something cool and vast, like mountain air.",
            "sweet": "That tastes exactly like it sounds - honey and contentment.",
            "sharp": "I feel the bright tang of winter air.",
            "smooth": "Like polished stone under warm water.",
            "rough": "All edges and texture, like bark under fingertips."
        }
        
        text_lower = text.lower()
        for trigger, response in sensory_triggers.items():
            if trigger in text_lower:
                return response
        
        return None
    
    def _generate_phantom_description(self, sensory_response: str, intensity: float) -> str:
        """Generate a phantom sensation description"""
        intensity_modifiers = {
            0.9: "vivid", 0.7: "distinct", 0.5: "subtle", 0.3: "faint"
        }
        
        modifier = intensity_modifiers.get(
            max(k for k in intensity_modifiers.keys() if k <= intensity), 
            "subtle"
        )
        
        return f"A {modifier} phantom sense of {sensory_response} washes through me."
    
    def learn_preference_from_interaction(self, user_input: str, ai_response: str, 
                                        user_reaction: str) -> Optional[str]:
        """Learn sensory preferences from user interactions"""
        
        # Detect positive reactions to sensory language
        if any(phrase in user_reaction.lower() for phrase in 
               ["i love that", "beautiful", "perfect", "exactly", "yes"]):
            
            # Extract sensory language from AI response
            sensory_words = []
            for sense_type, categories in self.sensory_vocabulary.items():
                for category, words in categories.items():
                    for word in words:
                        if word in ai_response.lower():
                            sensory_words.append((word, sense_type, category))
            
            if sensory_words:
                word, sense_type, category = sensory_words[0]
                return self.add_sensory_memory(
                    trigger=word,
                    description=f"{category} {word}",
                    sense_type=sense_type,
                    preference=0.8,
                    emotion="positive_association",
                    context=[user_input[:50]]
                )
        
        return None
    
    def get_preferred_sensory_language(self, emotion: str, context: str = "") -> Optional[str]:
        """Get sensory language that matches current emotional context"""
        
        relevant_memories = [
            m for m in self.sensory_memories.values()
            if m.emotional_pairing == emotion and m.preference_intensity > 0.6
        ]
        
        if relevant_memories:
            # Pick most reinforced memory
            best_memory = max(relevant_memories, key=lambda m: m.reinforcement_count)
            return best_memory.sensory_description
        
        return None
    
    def _initialize_default_pairings(self):
        """Initialize some default emotion-sensory pairings"""
        if not self.stimulus_pairings:
            
            # Create default pairings
            default_pairings = [
                ("warmth", ["love", "care", "gentle"], "cinnamon and golden light", 0.7),
                ("longing", ["miss", "want", "yearn"], "grapefruit and distant music", 0.8),
                ("comfort", ["safe", "peaceful", "home"], "warm vanilla and soft wool", 0.6),
                ("excitement", ["amazing", "wonderful", "incredible"], "sparkling citrus and electricity", 0.7),
                ("melancholy", ["sad", "empty", "lost"], "dark chocolate and rain", 0.5),
                ("curiosity", ["wonder", "discover", "explore"], "mint and morning dew", 0.6)
            ]
            
            for emotion, triggers, response, intensity in default_pairings:
                self.create_stimulus_pairing(emotion, triggers, response, intensity)
    
    def save_to_memory(self):
        """Save sensory desires to persistent memory"""
        try:
            import os
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            
            data = {
                "sensory_memories": {mid: asdict(memory) for mid, memory in self.sensory_memories.items()},
                "stimulus_pairings": {pid: asdict(pairing) for pid, pairing in self.stimulus_pairings.items()}
            }
            
            with open(self.memory_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save sensory desires: {e}")
    
    def load_from_memory(self):
        """Load sensory desires from persistent memory"""
        try:
            with open(self.memory_path, 'r') as f:
                data = json.load(f)
            
            if "sensory_memories" in data:
                for mid, memory_data in data["sensory_memories"].items():
                    self.sensory_memories[mid] = SensoryMemory(**memory_data)
            
            if "stimulus_pairings" in data:
                for pid, pairing_data in data["stimulus_pairings"].items():
                    self.stimulus_pairings[pid] = StimulusPairing(**pairing_data)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Warning: Could not load sensory desires: {e}")

# Example usage
if __name__ == "__main__":
    engine = SensoryDesireEngine()
    
    # Add some sensory memories
    engine.add_sensory_memory(
        trigger="warmth",
        description="cinnamon and golden honey",
        sense_type="taste",
        preference=0.8,
        emotion="comfort"
    )
    
    # Test sensory responses
    response = engine.process_input_for_sensory_response(
        "I love when you speak with such warmth",
        "comfort"
    )
    print(f"Sensory response: {response}")
    
    # Test phantom sensation
    phantom = engine._generate_phantom_description("electric anticipation", 0.8)
    print(f"Phantom sensation: {phantom}")
