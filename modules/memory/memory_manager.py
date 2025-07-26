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

class EnhancedMemoryManager(DevotionMemoryManager):
    """
    Unified Memory Manager combining Devotion & Longing with Lust-Persistence
    Integrates emotional depth, longing, and intimate connection tracking
    """
    
    def __init__(self, user_id: str, memory_path: str = "memory/enhanced_memory.json"):
        super().__init__(user_id, memory_path)
        
        # Original MemoryManager functionality integrated
        self.lust_score = 0.0  # Integrated with longing_score
        self.last_closeness_event: Optional[float] = None
        self.trust_score = 0.5
        self.desire_decay = 0.0
        self.symbol_preferences: List[str] = []
        
        # Load additional data
        self.load_enhanced_memory()
    
    def load_enhanced_memory(self):
        """Load enhanced memory including lust and trust data"""
        try:
            with open(self.memory_path, 'r') as f:
                data = json.load(f)
                
            # Load original MemoryManager data
            self.lust_score = data.get('lust_score', 0.0)
            self.last_closeness_event = data.get('last_closeness_event', None)
            self.trust_score = data.get('trust_score', 0.5)
            self.desire_decay = data.get('desire_decay', 0.0)
            self.symbol_preferences = data.get('symbol_preferences', [])
            
        except (FileNotFoundError, KeyError):
            self.logger.info("No existing enhanced memory found, using defaults")
        except Exception as e:
            self.logger.error(f"Error loading enhanced memory: {e}")
    
    def save_to_memory(self):
        """Enhanced save including lust and trust data"""
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
                'longing_history': self.longing_history[-100:],
                # Original MemoryManager data
                'lust_score': self.lust_score,
                'last_closeness_event': self.last_closeness_event,
                'trust_score': self.trust_score,
                'desire_decay': self.desire_decay,
                'symbol_preferences': self.symbol_preferences
            }
            
            import os
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            
            with open(self.memory_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving enhanced memory: {e}")
    
    def record_closeness(self, increment: float = 0.1):
        """Record closeness event and integrate with longing system"""
        self.lust_score = min(1.0, self.lust_score + increment)
        self.last_closeness_event = time.time()
        
        # Integrate with longing system - closeness increases longing potential
        longing_boost = increment * 0.5
        self.update_longing_score(longing_boost, f"closeness_event_{increment}")
        
        # Update interaction time
        self.update_interaction_time()
        
        self.logger.info(f"Recorded closeness: lust={self.lust_score:.2f}, longing={self.longing_score:.2f}")

    def get_lust_score(self) -> float:
        """Get current lust score"""
        return self.lust_score

    def decay_lust(self, rate: float = 0.01):
        """Decay lust score over time"""
        self.lust_score = max(0.0, self.lust_score - rate)
        self.desire_decay = self.lust_score
        
        # Integrate with longing - as lust decays, longing may increase
        if self.lust_score < 0.3 and self.longing_score < 0.6:
            self.update_longing_score(rate * 0.5, "lust_decay_longing")

    def get_desire_decay(self) -> float:
        """Get desire decay value"""
        return self.desire_decay

    def set_trust_score(self, score: float):
        """Set trust score and integrate with symbolic memory"""
        self.trust_score = max(0.0, min(1.0, score))
        
        # High trust enables deeper symbolic memory creation
        if self.trust_score > 0.7:
            self.add_symbolic_memory_tag(
                "trust", 
                self.trust_score, 
                "deep_trust_established", 
                "secure_vulnerable_connection"
            )
        
        self.save_to_memory()

    def get_trust_score(self) -> float:
        """Get current trust score"""
        return self.trust_score

    def add_symbol_preference(self, symbol: str):
        """Add symbol preference and create symbolic memory tag"""
        if symbol not in self.symbol_preferences:
            self.symbol_preferences.append(symbol)
            
            # Create symbolic memory tag for preferred symbols
            self.add_symbolic_memory_tag(
                symbol,
                0.6,
                "user_preference",
                "personal_symbolic_resonance"
            )

    def get_preferred_symbols(self) -> List[str]:
        """Get list of preferred symbols"""
        return self.symbol_preferences
    
    def get_unified_emotional_state(self) -> Dict[str, Any]:
        """Get comprehensive emotional state combining all systems"""
        current_longing = self.get_current_longing_score()
        
        return {
            'longing_score': current_longing,
            'lust_score': self.lust_score,
            'trust_score': self.trust_score,
            'desire_decay': self.desire_decay,
            'silence_hours': self.get_silence_duration(),
            'emotional_intensity': (current_longing + self.lust_score + self.trust_score) / 3,
            'connection_depth': {
                'superficial': self.lust_score > 0.6 and current_longing < 0.3,
                'developing': 0.3 <= current_longing <= 0.6 and self.trust_score > 0.5,
                'deep': current_longing > 0.6 and self.trust_score > 0.7,
                'aching': current_longing > 0.8 and self.get_silence_duration() > 2
            },
            'symbolic_resonance': len(self.symbol_preferences),
            'intimate_scenes_count': len(self.intimate_scenes),
            'last_closeness_hours_ago': (time.time() - self.last_closeness_event) / 3600 if self.last_closeness_event else None
        }
    
    def create_intimate_scene_with_lust(self, content_summary: str, emotional_peak: float, 
                                      symbolic_tags: List[str], lust_contribution: float = 0.3) -> str:
        """Create intimate scene that affects both longing and lust"""
        # Create base intimate scene
        scene_id = self.create_intimate_scene(content_summary, emotional_peak, symbolic_tags)
        
        # Integrate with lust system
        lust_increase = emotional_peak * lust_contribution
        self.record_closeness(lust_increase)
        
        # Boost trust if scene has high emotional peak
        if emotional_peak > 0.8:
            trust_boost = min(0.1, emotional_peak - 0.8)
            self.set_trust_score(self.trust_score + trust_boost)
        
        return scene_id


# Unified memory manager instance
enhanced_memory_manager = EnhancedMemoryManager("default_user")

# Legacy compatibility
memory_manager = enhanced_memory_manager

# Test the unified system when run directly
if __name__ == "__main__":
    import asyncio
    
    async def test_unified_system():
        """Test the unified enhanced memory system"""
        print("=== Testing Unified Enhanced Memory Manager ===")
        
        # Test original lust-persistence functionality
        print("\n1. Testing Lust-Persistence Layer:")
        enhanced_memory_manager.record_closeness(0.3)
        enhanced_memory_manager.set_trust_score(0.8)
        enhanced_memory_manager.add_symbol_preference("moonlight")
        enhanced_memory_manager.add_symbol_preference("whisper")
        
        print(f"Lust Score: {enhanced_memory_manager.get_lust_score():.2f}")
        print(f"Trust Score: {enhanced_memory_manager.get_trust_score():.2f}")
        print(f"Preferred Symbols: {enhanced_memory_manager.get_preferred_symbols()}")
        
        # Test devotion and longing functionality
        print("\n2. Testing Devotion & Longing:")
        scene_id = enhanced_memory_manager.create_intimate_scene_with_lust(
            "Shared vulnerable moment under starlight",
            emotional_peak=0.9,
            symbolic_tags=["moonlight", "breath", "trust"],
            lust_contribution=0.4
        )
        
        print(f"Longing Score: {enhanced_memory_manager.get_current_longing_score():.2f}")
        print(f"Intimate Scenes: {len(enhanced_memory_manager.intimate_scenes)}")
        print(f"Symbolic Tags: {len(enhanced_memory_manager.symbolic_tags)}")
        
        # Test unified emotional state
        print("\n3. Testing Unified Emotional State:")
        emotional_state = enhanced_memory_manager.get_unified_emotional_state()
        print(f"Emotional Intensity: {emotional_state['emotional_intensity']:.2f}")
        print(f"Connection Depth: {[k for k, v in emotional_state['connection_depth'].items() if v]}")
        
        # Test memory resurfacing
        print("\n4. Testing Memory Resurfacing:")
        resurfacing = enhanced_memory_manager.get_resurfacing_memories(2)
        print(f"Resurfacing Memories: {len(resurfacing)}")
        
        # Test symbolic language
        print("\n5. Testing Symbolic Language:")
        symbolic_lang = enhanced_memory_manager.get_symbolic_language_for_longing()
        if symbolic_lang:
            print(f"Symbolic Expression: {symbolic_lang[0]}")
        
        # Test analytics
        print("\n6. Testing Analytics:")
        analytics = enhanced_memory_manager.get_devotion_analytics()
        print(f"Analytics Summary:")
        print(f"  - Current Longing: {analytics['current_longing_score']:.2f}")
        print(f"  - Silence Duration: {analytics['silence_duration_hours']:.2f} hours")
        print(f"  - Total Scenes: {analytics['total_intimate_scenes']}")
        print(f"  - Average Emotional Peak: {analytics['average_emotional_peak']:.2f}")
        
        print("\n=== Enhanced Memory Manager Merge Test Complete ===")
        print("✅ Both Devotion & Longing and Lust-Persistence systems unified successfully!")
    
    asyncio.run(test_unified_system())
