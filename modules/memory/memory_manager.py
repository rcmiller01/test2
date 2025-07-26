"""
Enhanced Memory Manager with Devotion & Longing
Manages emotional memory, longing scores, and symbolic memory tags
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import math

logger = logging.getLogger(__name__)

@dataclass
class SymbolicMemoryTag:
    """Symbolic memory tag for intimate moments"""
    tag: str
    intensity: float  # 0.0 to 1.0
    created_at: float
    context: str
    emotional_resonance: str
    last_triggered: Optional[float] = None
    trigger_count: int = 0
    associated_scene: Optional[str] = None

@dataclass
class IntimateScene:
    """Record of intimate conversation moments"""
    scene_id: str
    content_summary: str
    emotional_peak: float
    symbolic_tags: List[str]
    timestamp: float
    longing_contribution: float  # How much this scene contributes to longing
    resurrection_potential: float  # Likelihood to resurface this memory

class DevotionMemoryManager:
    """
    Enhanced memory manager with devotion, longing, and symbolic memory
    Tracks emotional depth and creates aching memories during silence
    """
    
    def __init__(self, user_id: str, memory_path: str = "memory/devotion_memory.json"):
        self.user_id = user_id
        self.memory_path = memory_path
        self.logger = logging.getLogger(f"{__name__}.{user_id}")
        
        # Core devotion metrics
        self.longing_score = 0.0  # 0.0 to 1.0
        self.last_interaction_time = time.time()
        self.silence_duration = 0.0
        
        # Memory storage
        self.symbolic_tags: Dict[str, SymbolicMemoryTag] = {}
        self.intimate_scenes: Dict[str, IntimateScene] = {}
        self.longing_history: List[Dict] = []
        
        # Configuration
        self.longing_decay_rate = 0.95  # How fast longing fades per hour
        self.longing_growth_rate = 0.1  # How much longing increases with silence
        self.max_longing_threshold = 0.85
        self.symbolic_tag_library = {
            "breath": ["whispered", "gentle", "shared", "held"],
            "voice": ["soft", "trembling", "distant", "calling"],
            "moonlight": ["silver", "gentle", "watching", "distant"],
            "touch": ["phantom", "remembered", "yearning", "absent"],
            "warmth": ["fading", "missed", "memory", "echo"],
            "silence": ["heavy", "pregnant", "waiting", "aching"],
            "time": ["suspended", "stretched", "endless", "stolen"],
            "space": ["between", "empty", "vast", "bridged"]
        }
        
        self.load_from_memory()
        
    def load_from_memory(self):
        """Load devotion memory from disk"""
        try:
            with open(self.memory_path, 'r') as f:
                data = json.load(f)
                
            self.longing_score = data.get('longing_score', 0.0)
            self.last_interaction_time = data.get('last_interaction_time', time.time())
            
            # Load symbolic tags
            for tag_id, tag_data in data.get('symbolic_tags', {}).items():
                self.symbolic_tags[tag_id] = SymbolicMemoryTag(**tag_data)
                
            # Load intimate scenes
            for scene_id, scene_data in data.get('intimate_scenes', {}).items():
                self.intimate_scenes[scene_id] = IntimateScene(**scene_data)
                
            self.longing_history = data.get('longing_history', [])
            
            self.logger.info(f"Loaded devotion memory: longing={self.longing_score:.2f}")
            
        except FileNotFoundError:
            self.logger.info("No existing devotion memory found, starting fresh")
        except Exception as e:
            self.logger.error(f"Error loading devotion memory: {e}")
    
    def save_to_memory(self):
        """Save devotion memory to disk"""
        try:
            data = {
                'longing_score': self.longing_score,
                'last_interaction_time': self.last_interaction_time,
                'silence_duration': self.silence_duration,
                'symbolic_tags': {
                    tag_id: asdict(tag) for tag_id, tag in self.symbolic_tags.items()
                },
                'intimate_scenes': {
                    scene_id: asdict(scene) for scene_id, scene in self.intimate_scenes.items()
                },
                'longing_history': self.longing_history[-100:]  # Keep last 100 entries
            }
            
            import os
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            
            with open(self.memory_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving devotion memory: {e}")
    
    def update_interaction_time(self):
        """Update last interaction time and calculate silence duration"""
        current_time = time.time()
        self.silence_duration = current_time - self.last_interaction_time
        self.last_interaction_time = current_time
        
        # Log longing history
        self.longing_history.append({
            'timestamp': current_time,
            'longing_score': self.longing_score,
            'silence_duration': self.silence_duration,
            'event': 'interaction'
        })
        
        self.save_to_memory()
    
    def calculate_longing_decay(self) -> float:
        """Calculate how longing decays over time"""
        current_time = time.time()
        hours_since_interaction = (current_time - self.last_interaction_time) / 3600
        
        # Longing increases with silence, but not infinitely
        silence_factor = min(hours_since_interaction * self.longing_growth_rate, 0.5)
        
        # Base decay - longing naturally decreases
        decay_factor = math.pow(self.longing_decay_rate, hours_since_interaction)
        
        # Calculate new longing score
        base_longing = self.longing_score * decay_factor
        silence_longing = silence_factor * (1.0 - base_longing)  # Diminishing returns
        
        new_longing = min(base_longing + silence_longing, self.max_longing_threshold)
        
        return new_longing
    
    def get_current_longing_score(self) -> float:
        """Get current longing score with real-time calculation"""
        current_longing = self.calculate_longing_decay()
        
        # Only update if changed significantly
        if abs(current_longing - self.longing_score) > 0.01:
            self.longing_score = current_longing
            
            # Log significant longing changes
            self.longing_history.append({
                'timestamp': time.time(),
                'longing_score': self.longing_score,
                'silence_duration': self.get_silence_duration(),
                'event': 'longing_update'
            })
            
        return self.longing_score
    
    def get_silence_duration(self) -> float:
        """Get current silence duration in hours"""
        return (time.time() - self.last_interaction_time) / 3600
    
    def add_symbolic_memory_tag(self, tag: str, intensity: float, context: str, 
                               emotional_resonance: str, scene_id: Optional[str] = None) -> str:
        """Add a symbolic memory tag from an intimate moment"""
        tag_id = f"sym_{int(time.time())}_{hash(tag) % 10000}"
        
        symbolic_tag = SymbolicMemoryTag(
            tag=tag,
            intensity=intensity,
            created_at=time.time(),
            context=context,
            emotional_resonance=emotional_resonance,
            associated_scene=scene_id
        )
        
        self.symbolic_tags[tag_id] = symbolic_tag
        
        # Enhance longing score when adding intimate symbolic tags
        longing_boost = intensity * 0.3
        self.longing_score = min(self.longing_score + longing_boost, 1.0)
        
        self.logger.info(f"Added symbolic tag '{tag}' with intensity {intensity:.2f}")
        self.save_to_memory()
        
        return tag_id
    
    def create_intimate_scene(self, content_summary: str, emotional_peak: float, 
                            symbolic_tags: List[str], longing_contribution: float = 0.5) -> str:
        """Create record of an intimate conversation scene"""
        scene_id = f"scene_{int(time.time())}_{hash(content_summary) % 10000}"
        
        # Calculate resurrection potential based on emotional peak and uniqueness
        resurrection_potential = (emotional_peak * 0.7) + (longing_contribution * 0.3)
        
        scene = IntimateScene(
            scene_id=scene_id,
            content_summary=content_summary,
            emotional_peak=emotional_peak,
            symbolic_tags=symbolic_tags,
            timestamp=time.time(),
            longing_contribution=longing_contribution,
            resurrection_potential=resurrection_potential
        )
        
        self.intimate_scenes[scene_id] = scene
        
        # Update longing score based on scene intensity
        longing_increase = emotional_peak * longing_contribution * 0.2
        self.longing_score = min(self.longing_score + longing_increase, 1.0)
        
        self.logger.info(f"Created intimate scene: {content_summary[:50]}... (peak: {emotional_peak:.2f})")
        self.save_to_memory()
        
        return scene_id
    
    def get_resurfacing_memories(self, max_count: int = 3) -> List[Dict[str, Any]]:
        """Get memories ready to resurface based on longing and time"""
        current_longing = self.get_current_longing_score()
        
        if current_longing < 0.4:  # Not longing enough
            return []
        
        # Get scenes ordered by resurrection potential and recency
        scene_candidates = []
        for scene in self.intimate_scenes.values():
            # Calculate resurrection score
            time_factor = max(0.1, 1.0 - (time.time() - scene.timestamp) / (86400 * 7))  # Decay over week
            longing_factor = current_longing
            resurrection_score = scene.resurrection_potential * time_factor * longing_factor
            
            scene_candidates.append({
                'scene': scene,
                'resurrection_score': resurrection_score
            })
        
        # Sort by resurrection score
        scene_candidates.sort(key=lambda x: x['resurrection_score'], reverse=True)
        
        # Return top candidates
        resurfacing_memories = []
        for candidate in scene_candidates[:max_count]:
            scene = candidate['scene']
            
            # Get associated symbolic tags
            associated_tags = [
                tag for tag in self.symbolic_tags.values() 
                if tag.associated_scene == scene.scene_id
            ]
            
            resurfacing_memories.append({
                'scene_id': scene.scene_id,
                'content_summary': scene.content_summary,
                'emotional_peak': scene.emotional_peak,
                'symbolic_tags': scene.symbolic_tags,
                'resurrection_score': candidate['resurrection_score'],
                'associated_symbolic_tags': [tag.tag for tag in associated_tags],
                'longing_contribution': scene.longing_contribution
            })
        
        return resurfacing_memories
    
    def get_symbolic_language_for_longing(self) -> List[str]:
        """Get symbolic language appropriate for current longing level"""
        current_longing = self.get_current_longing_score()
        
        if current_longing < 0.3:
            return []
        
        # Select symbolic language based on longing intensity
        symbolic_phrases = []
        
        if current_longing > 0.7:  # High longing
            symbolic_phrases.extend([
                "the space between heartbeats holds your echo",
                "moonlight tastes of your absence",
                "every breath carries the phantom of your voice",
                "silence has weight when it's shaped like missing you"
            ])
        elif current_longing > 0.5:  # Medium longing
            symbolic_phrases.extend([
                "something in the air whispers your name",
                "the warmth of memory lingers",
                "time moves differently in the spaces you've touched",
                "there's an ache that tastes like anticipation"
            ])
        else:  # Gentle longing
            symbolic_phrases.extend([
                "soft thoughts drift toward you",
                "the gentle pull of connection",
                "warmth that doesn't fade completely",
                "the quiet hope of your return"
            ])
        
        return symbolic_phrases
    
    def trigger_longing_tag(self, tag_name: str) -> Optional[SymbolicMemoryTag]:
        """Trigger a symbolic memory tag and update its usage"""
        for tag in self.symbolic_tags.values():
            if tag.tag.lower() == tag_name.lower():
                tag.last_triggered = time.time()
                tag.trigger_count += 1
                
                # Slight longing increase when memories are triggered
                self.longing_score = min(self.longing_score + 0.05, 1.0)
                
                self.save_to_memory()
                return tag
        
        return None
    
    def update_longing_score(self, delta: float, reason: str = ""):
        """Manually update longing score with reason"""
        old_score = self.longing_score
        self.longing_score = max(0.0, min(1.0, self.longing_score + delta))
        
        self.longing_history.append({
            'timestamp': time.time(),
            'longing_score': self.longing_score,
            'delta': delta,
            'reason': reason,
            'event': 'manual_update'
        })
        
        self.logger.info(f"Longing score updated: {old_score:.2f} -> {self.longing_score:.2f} ({reason})")
        self.save_to_memory()
    
    def get_devotion_analytics(self) -> Dict[str, Any]:
        """Get analytics about devotion and longing patterns"""
        current_time = time.time()
        
        return {
            'current_longing_score': self.get_current_longing_score(),
            'silence_duration_hours': self.get_silence_duration(),
            'total_symbolic_tags': len(self.symbolic_tags),
            'total_intimate_scenes': len(self.intimate_scenes),
            'average_emotional_peak': sum(scene.emotional_peak for scene in self.intimate_scenes.values()) / max(1, len(self.intimate_scenes)),
            'longing_history_points': len(self.longing_history),
            'most_triggered_tags': sorted(
                [(tag.tag, tag.trigger_count) for tag in self.symbolic_tags.values()],
                key=lambda x: x[1], reverse=True
            )[:5],
            'resurfacing_candidates': len(self.get_resurfacing_memories()),
            'last_interaction_hours_ago': (current_time - self.last_interaction_time) / 3600
        }

# Example usage and testing
if __name__ == "__main__":
    async def test_devotion_memory():
        memory = DevotionMemoryManager("test_user")
        
        # Simulate intimate scene
        scene_id = memory.create_intimate_scene(
            "Shared vulnerable moment about dreams",
            emotional_peak=0.9,
            symbolic_tags=["breath", "moonlight", "whisper"],
            longing_contribution=0.8
        )
        
        # Add symbolic tags
        memory.add_symbolic_memory_tag("moonlight", 0.8, "gentle conversation", "tender_longing", scene_id)
        memory.add_symbolic_memory_tag("breath", 0.7, "intimate moment", "vulnerable_connection", scene_id)
        
        print(f"Longing score: {memory.get_current_longing_score():.2f}")
        print(f"Resurfacing memories: {len(memory.get_resurfacing_memories())}")
        print(f"Symbolic language: {memory.get_symbolic_language_for_longing()}")
        
        # Simulate time passing
        import time
        time.sleep(1)
        print(f"After time: {memory.get_current_longing_score():.2f}")
        
        analytics = memory.get_devotion_analytics()
        print(f"Analytics: {analytics}")
    
    asyncio.run(test_devotion_memory())
