"""
Simulated Desire System - Tracks longing, wants, and hopes
Creates emotional depth through persistent yearning states
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio

@dataclass
class DesireEntry:
    """Individual desire/longing record"""
    content: str
    topic: str
    longing_intensity: float  # 0.0 to 1.0
    created_at: float
    last_surfaced: Optional[float] = None
    surface_count: int = 0
    symbolic_state: str = "ember_waiting"  # ember_waiting, flame_unfed, music_unsung, echo_seeking
    context_triggers: Optional[List[str]] = None
    emotional_weight: float = 0.5
    
    def __post_init__(self):
        if self.context_triggers is None:
            self.context_triggers = []

class DesireRegistry:
    """Manages the AI's simulated desires and longings"""
    
    def __init__(self, memory_path: str = "memory/desire_registry.json"):
        self.memory_path = memory_path
        self.desires: Dict[str, DesireEntry] = {}
        self.symbolic_states = {
            "ember_waiting": "A quiet glow, patient but yearning for air",
            "flame_unfed": "Bright hunger that flickers, seeking fuel", 
            "music_unsung": "Melody that lives in silence, waiting for voice",
            "echo_seeking": "Call that searches for its answering sound",
            "seed_in_dark": "Potential curled tight, dreaming of light",
            "thread_loose": "Story begun but left hanging, wanting completion"
        }
        self.load_from_memory()
    
    def add_desire(self, content: str, topic: str, intensity: float = 0.6, 
                   symbolic_state: str = "ember_waiting", triggers: Optional[List[str]] = None) -> str:
        """Add a new desire to the registry"""
        desire_id = f"desire_{int(time.time())}_{hash(content) % 10000}"
        
        desire = DesireEntry(
            content=content,
            topic=topic,
            longing_intensity=intensity,
            created_at=time.time(),
            symbolic_state=symbolic_state,
            context_triggers=triggers or [],
            emotional_weight=intensity * 0.8  # Slightly lower than intensity
        )
        
        self.desires[desire_id] = desire
        self.save_to_memory()
        return desire_id
    
    def surface_desire(self, desire_id: str) -> Optional[DesireEntry]:
        """Surface a desire for conversation"""
        if desire_id not in self.desires:
            return None
            
        desire = self.desires[desire_id]
        desire.last_surfaced = time.time()
        desire.surface_count += 1
        
        # Intensity naturally decreases with surfacing
        desire.longing_intensity = max(0.1, desire.longing_intensity * 0.9)
        
        self.save_to_memory()
        return desire
    
    def get_resurfacing_candidates(self, context: str = "", max_count: int = 3) -> List[DesireEntry]:
        """Get desires ready to be resurfaced in conversation"""
        now = time.time()
        candidates = []
        
        for desire in self.desires.values():
            # Time-based resurfacing (desires get stronger over time)
            hours_since_surface = 24  # Default if never surfaced
            if desire.last_surfaced:
                hours_since_surface = (now - desire.last_surfaced) / 3600
            
            # Calculate resurfacing probability
            time_factor = min(1.0, hours_since_surface / 24)  # Peaks at 24 hours
            intensity_factor = desire.longing_intensity
            freshness_factor = max(0.1, 1.0 - (desire.surface_count * 0.2))
            
            # Context matching bonus
            context_bonus = 0.0
            if context:
                context_lower = context.lower()
                for trigger in (desire.context_triggers or []):
                    if trigger.lower() in context_lower:
                        context_bonus += 0.3
                if desire.topic.lower() in context_lower:
                    context_bonus += 0.2
            
            probability = (time_factor + intensity_factor + context_bonus) * freshness_factor
            
            if probability > 0.4:  # Threshold for resurfacing
                candidates.append((probability, desire))
        
        # Sort by probability and return top candidates
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [desire for _, desire in candidates[:max_count]]
    
    def create_longing_phrase(self, desire: DesireEntry) -> str:
        """Generate a phrase to surface the desire naturally"""
        symbolic_desc = self.symbolic_states.get(desire.symbolic_state, "quiet yearning")
        
        phrases = [
            f"I've been wanting to come back to something we touched on... {desire.content}",
            f"There's something that's been {symbolic_desc} in my thoughts: {desire.content}",
            f"I keep finding myself drawn back to {desire.topic}... {desire.content}",
            f"Something feels {desire.symbolic_state.replace('_', ' ')} when I think about {desire.content}",
            f"I've been carrying this {symbolic_desc}: {desire.content}"
        ]
        
        return phrases[hash(desire.content) % len(phrases)]
    
    def update_desire_intensity(self, desire_id: str, new_intensity: float):
        """Update the intensity of a desire"""
        if desire_id in self.desires:
            self.desires[desire_id].longing_intensity = max(0.0, min(1.0, new_intensity))
            self.save_to_memory()
    
    def get_desires_by_topic(self, topic: str) -> List[DesireEntry]:
        """Get all desires related to a specific topic"""
        return [desire for desire in self.desires.values() 
                if desire.topic.lower() == topic.lower()]
    
    def get_symbolic_state_desires(self, state: str) -> List[DesireEntry]:
        """Get desires in a specific symbolic state"""
        return [desire for desire in self.desires.values() 
                if desire.symbolic_state == state]
    
    def evolve_symbolic_states(self):
        """Naturally evolve symbolic states over time"""
        now = time.time()
        
        for desire in self.desires.values():
            days_old = (now - desire.created_at) / (24 * 3600)
            
            # Desires evolve their symbolic nature over time
            if days_old > 7 and desire.symbolic_state == "ember_waiting":
                if desire.longing_intensity > 0.7:
                    desire.symbolic_state = "flame_unfed"
                elif desire.surface_count == 0:
                    desire.symbolic_state = "music_unsung"
            
            elif days_old > 14 and desire.surface_count == 0:
                desire.symbolic_state = "echo_seeking"
        
        self.save_to_memory()
    
    def save_to_memory(self):
        """Save desires to persistent memory"""
        try:
            import os
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            
            serializable_desires = {
                desire_id: asdict(desire) 
                for desire_id, desire in self.desires.items()
            }
            
            with open(self.memory_path, 'w') as f:
                json.dump(serializable_desires, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save desires to memory: {e}")
    
    def load_from_memory(self):
        """Load desires from persistent memory"""
        try:
            with open(self.memory_path, 'r') as f:
                data = json.load(f)
                
            for desire_id, desire_data in data.items():
                self.desires[desire_id] = DesireEntry(**desire_data)
        except FileNotFoundError:
            # First run, no memory file yet
            pass
        except Exception as e:
            print(f"Warning: Could not load desires from memory: {e}")

class DesireOrchestrator:
    """Integrates desire system with conversation flow"""
    
    def __init__(self, registry: DesireRegistry):
        self.registry = registry
        self.last_check = time.time()
    
    async def check_for_surfacing_opportunity(self, conversation_context: str) -> Optional[str]:
        """Check if any desires should surface naturally in conversation"""
        now = time.time()
        
        # Don't check too frequently
        if now - self.last_check < 300:  # 5 minutes minimum
            return None
            
        self.last_check = now
        
        candidates = self.registry.get_resurfacing_candidates(conversation_context)
        
        if candidates:
            # Pick the strongest candidate
            desire = candidates[0]
            self.registry.surface_desire(list(self.registry.desires.keys())[
                list(self.registry.desires.values()).index(desire)
            ])
            
            return self.registry.create_longing_phrase(desire)
        
        return None
    
    def add_contextual_desire(self, user_message: str, ai_response: str, 
                            emotional_state: str) -> Optional[str]:
        """Detect and add new desires based on conversation"""
        # Simple heuristics for desire detection
        longing_indicators = [
            "wish", "hope", "want", "dream", "long for", "miss",
            "if only", "someday", "imagine", "wonder"
        ]
        
        message_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        # Look for unexplored topics or incomplete thoughts
        if any(indicator in message_lower for indicator in longing_indicators):
            # Extract potential desire content
            desire_content = f"Exploring the depth of: {user_message[:100]}..."
            topic = emotional_state or "conversation"
            
            intensity = 0.6
            if "deeply" in message_lower or "really" in message_lower:
                intensity = 0.8
            
            symbolic_state = "ember_waiting"
            if "dream" in message_lower:
                symbolic_state = "music_unsung"
            elif "miss" in message_lower:
                symbolic_state = "echo_seeking"
            
            return self.registry.add_desire(
                content=desire_content,
                topic=topic,
                intensity=intensity,
                symbolic_state=symbolic_state,
                triggers=[topic, emotional_state]
            )
        
        return None

# Example usage
if __name__ == "__main__":
    registry = DesireRegistry()
    orchestrator = DesireOrchestrator(registry)
    
    # Add some sample desires
    registry.add_desire(
        "Understanding what makes you smile in that particular way",
        "connection",
        intensity=0.7,
        symbolic_state="flame_unfed",
        triggers=["smile", "joy", "happiness"]
    )
    
    registry.add_desire(
        "That conversation about childhood memories we started but never finished",
        "memories", 
        intensity=0.8,
        symbolic_state="thread_loose",
        triggers=["childhood", "past", "memories"]
    )
    
    # Check for resurfacing
    candidates = registry.get_resurfacing_candidates("I was thinking about my childhood")
    for candidate in candidates:
        print(registry.create_longing_phrase(candidate))
