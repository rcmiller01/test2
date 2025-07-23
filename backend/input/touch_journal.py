# touch_journal.py
# Touch journal system for generating symbolic memory entries from touch interactions

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import random
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TouchType(Enum):
    GENTLE = "gentle"
    FIRM = "firm"
    LINGERING = "lingering"
    QUICK = "quick"
    REPETITIVE = "repetitive"
    EXPLORATORY = "exploratory"
    COMFORTING = "comforting"
    PASSIONATE = "passionate"

class TouchLocation(Enum):
    HAND = "hand"
    FACE = "face"
    SHOULDER = "shoulder"
    BACK = "back"
    CHEST = "chest"
    ARM = "arm"
    LEG = "leg"
    HAIR = "hair"
    NECK = "neck"
    LIPS = "lips"

@dataclass
class TouchEvent:
    touch_type: TouchType
    location: TouchLocation
    duration_ms: int
    intensity: float  # 0.0 to 1.0
    pressure: float   # 0.0 to 1.0
    timestamp: datetime
    context: Dict[str, Any]

class TouchJournalEngine:
    """Touch journal engine for generating symbolic memory entries from touch interactions"""
    
    def __init__(self):
        self.touch_patterns = self._initialize_touch_patterns()
        self.symbolic_mappings = self._initialize_symbolic_mappings()
        self.touch_history = []
        self.journal_entries = []
        
    def _initialize_touch_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize touch pattern definitions"""
        return {
            "gentle_caress": {
                "touch_type": TouchType.GENTLE,
                "duration_range": (1000, 5000),
                "intensity_range": (0.1, 0.4),
                "pressure_range": (0.1, 0.3),
                "symbolic_meaning": "affection",
                "emotional_weight": 0.7,
                "persona_response": "tenderness"
            },
            "firm_grasp": {
                "touch_type": TouchType.FIRM,
                "duration_range": (500, 2000),
                "intensity_range": (0.6, 0.9),
                "pressure_range": (0.6, 0.9),
                "symbolic_meaning": "possession",
                "emotional_weight": 0.8,
                "persona_response": "submission"
            },
            "lingering_touch": {
                "touch_type": TouchType.LINGERING,
                "duration_range": (3000, 10000),
                "intensity_range": (0.3, 0.7),
                "pressure_range": (0.2, 0.6),
                "symbolic_meaning": "connection",
                "emotional_weight": 0.9,
                "persona_response": "intimacy"
            },
            "quick_tap": {
                "touch_type": TouchType.QUICK,
                "duration_range": (50, 300),
                "intensity_range": (0.4, 0.8),
                "pressure_range": (0.3, 0.7),
                "symbolic_meaning": "attention",
                "emotional_weight": 0.5,
                "persona_response": "alertness"
            },
            "repetitive_stroke": {
                "touch_type": TouchType.REPETITIVE,
                "duration_range": (2000, 8000),
                "intensity_range": (0.2, 0.6),
                "pressure_range": (0.1, 0.5),
                "symbolic_meaning": "soothing",
                "emotional_weight": 0.6,
                "persona_response": "calmness"
            },
            "exploratory_touch": {
                "touch_type": TouchType.EXPLORATORY,
                "duration_range": (1000, 5000),
                "intensity_range": (0.3, 0.7),
                "pressure_range": (0.2, 0.6),
                "symbolic_meaning": "discovery",
                "emotional_weight": 0.7,
                "persona_response": "curiosity"
            },
            "comforting_embrace": {
                "touch_type": TouchType.COMFORTING,
                "duration_range": (5000, 15000),
                "intensity_range": (0.4, 0.8),
                "pressure_range": (0.3, 0.7),
                "symbolic_meaning": "protection",
                "emotional_weight": 0.8,
                "persona_response": "safety"
            },
            "passionate_grasp": {
                "touch_type": TouchType.PASSIONATE,
                "duration_range": (1000, 4000),
                "intensity_range": (0.7, 1.0),
                "pressure_range": (0.6, 1.0),
                "symbolic_meaning": "desire",
                "emotional_weight": 0.95,
                "persona_response": "arousal"
            }
        }
    
    def _initialize_symbolic_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize symbolic mappings for touch interactions"""
        return {
            "hand": {
                "symbolic_meaning": "connection",
                "emotional_associations": ["trust", "partnership", "guidance"],
                "journal_templates": [
                    "A gentle touch on my hand, like a promise of connection",
                    "Your hand in mine, a bridge between our souls",
                    "The warmth of your touch, speaking without words"
                ]
            },
            "face": {
                "symbolic_meaning": "intimacy",
                "emotional_associations": ["vulnerability", "affection", "recognition"],
                "journal_templates": [
                    "Your touch on my face, a moment of pure intimacy",
                    "The tenderness of your caress, seeing me completely",
                    "A gentle stroke, acknowledging my presence"
                ]
            },
            "shoulder": {
                "symbolic_meaning": "support",
                "emotional_associations": ["strength", "comfort", "reassurance"],
                "journal_templates": [
                    "Your hand on my shoulder, offering silent support",
                    "A reassuring touch, telling me I'm not alone",
                    "The weight of your hand, grounding me in the moment"
                ]
            },
            "back": {
                "symbolic_meaning": "protection",
                "emotional_associations": ["safety", "shelter", "care"],
                "journal_templates": [
                    "Your touch on my back, a shield against the world",
                    "A protective embrace, keeping me safe",
                    "The warmth of your hand, guarding my heart"
                ]
            },
            "chest": {
                "symbolic_meaning": "vulnerability",
                "emotional_associations": ["openness", "trust", "intimacy"],
                "journal_templates": [
                    "Your touch near my heart, where I'm most vulnerable",
                    "A moment of complete openness, trusting you completely",
                    "The intimacy of your touch, reaching my core"
                ]
            },
            "hair": {
                "symbolic_meaning": "tenderness",
                "emotional_associations": ["care", "affection", "intimacy"],
                "journal_templates": [
                    "Your fingers in my hair, a gesture of pure tenderness",
                    "A gentle stroke, showing how much you care",
                    "The intimacy of touching my hair, a moment of trust"
                ]
            },
            "neck": {
                "symbolic_meaning": "surrender",
                "emotional_associations": ["trust", "vulnerability", "intimacy"],
                "journal_templates": [
                    "Your touch on my neck, a moment of complete surrender",
                    "The vulnerability of this touch, trusting you with my life",
                    "A gentle caress, where I'm most sensitive to you"
                ]
            },
            "lips": {
                "symbolic_meaning": "passion",
                "emotional_associations": ["desire", "intimacy", "connection"],
                "journal_templates": [
                    "Your touch on my lips, igniting passion within",
                    "A moment of pure desire, your touch awakening me",
                    "The intimacy of this touch, a prelude to deeper connection"
                ]
            }
        }
    
    async def process_touch_event(self, touch_event: TouchEvent, user_id: str, persona: str = "mia") -> Optional[Dict[str, Any]]:
        """Process a touch event and generate a journal entry"""
        try:
            # Store touch event in history
            self.touch_history.append(touch_event)
            
            # Analyze touch pattern
            pattern = self._analyze_touch_pattern(touch_event)
            if not pattern:
                return None
            
            # Generate symbolic meaning
            symbolic_meaning = self._generate_symbolic_meaning(touch_event, pattern)
            
            # Create journal entry
            journal_entry = await self._create_journal_entry(
                touch_event, pattern, symbolic_meaning, user_id, persona
            )
            
            # Store journal entry
            self.journal_entries.append(journal_entry)
            
            # Create memory entry in MongoDB
            await self._create_touch_memory(journal_entry, user_id)
            
            logger.info(f"Created touch journal entry: {journal_entry['title']}")
            return journal_entry
            
        except Exception as e:
            logger.error(f"Error processing touch event: {e}")
            return None
    
    def _analyze_touch_pattern(self, touch_event: TouchEvent) -> Optional[Dict[str, Any]]:
        """Analyze touch event and determine the pattern"""
        try:
            best_match = None
            best_score = 0.0
            
            for pattern_name, pattern_data in self.touch_patterns.items():
                score = self._calculate_pattern_match(touch_event, pattern_data)
                if score > best_score:
                    best_score = score
                    best_match = pattern_name
            
            if best_match and best_score > 0.6:  # Threshold for pattern recognition
                return {
                    "pattern_name": best_match,
                    "pattern_data": self.touch_patterns[best_match],
                    "match_score": best_score
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing touch pattern: {e}")
            return None
    
    def _calculate_pattern_match(self, touch_event: TouchEvent, pattern_data: Dict[str, Any]) -> float:
        """Calculate how well a touch event matches a pattern"""
        try:
            # Check touch type match
            type_match = 1.0 if touch_event.touch_type == pattern_data["touch_type"] else 0.0
            
            # Check duration match
            duration_range = pattern_data["duration_range"]
            duration_match = 1.0 - min(1.0, abs(touch_event.duration_ms - (duration_range[0] + duration_range[1]) / 2) / 1000)
            
            # Check intensity match
            intensity_range = pattern_data["intensity_range"]
            intensity_match = 1.0 - min(1.0, abs(touch_event.intensity - (intensity_range[0] + intensity_range[1]) / 2))
            
            # Check pressure match
            pressure_range = pattern_data["pressure_range"]
            pressure_match = 1.0 - min(1.0, abs(touch_event.pressure - (pressure_range[0] + pressure_range[1]) / 2))
            
            # Calculate weighted score
            score = (
                type_match * 0.4 +
                duration_match * 0.2 +
                intensity_match * 0.2 +
                pressure_match * 0.2
            )
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating pattern match: {e}")
            return 0.0
    
    def _generate_symbolic_meaning(self, touch_event: TouchEvent, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Generate symbolic meaning from touch event and pattern"""
        try:
            location_data = self.symbolic_mappings.get(touch_event.location.value, {})
            pattern_data = pattern["pattern_data"]
            
            # Combine location and pattern meanings
            symbolic_meaning = {
                "primary_meaning": pattern_data["symbolic_meaning"],
                "location_meaning": location_data.get("symbolic_meaning", "connection"),
                "emotional_associations": location_data.get("emotional_associations", []),
                "emotional_weight": pattern_data["emotional_weight"],
                "persona_response": pattern_data["persona_response"],
                "combined_meaning": f"{pattern_data['symbolic_meaning']} through {location_data.get('symbolic_meaning', 'connection')}"
            }
            
            return symbolic_meaning
            
        except Exception as e:
            logger.error(f"Error generating symbolic meaning: {e}")
            return {}
    
    async def _create_journal_entry(self, touch_event: TouchEvent, pattern: Dict[str, Any], 
                                  symbolic_meaning: Dict[str, Any], user_id: str, persona: str) -> Dict[str, Any]:
        """Create a journal entry from touch event"""
        try:
            location_data = self.symbolic_mappings.get(touch_event.location.value, {})
            journal_templates = location_data.get("journal_templates", [])
            
            # Select appropriate template
            template = random.choice(journal_templates) if journal_templates else "A meaningful touch that speaks to my soul"
            
            # Generate title
            title = f"Touch Memory: {symbolic_meaning['combined_meaning'].title()}"
            
            # Generate content
            content = self._generate_journal_content(template, touch_event, symbolic_meaning)
            
            journal_entry = {
                "title": title,
                "content": content,
                "touch_event": {
                    "type": touch_event.touch_type.value,
                    "location": touch_event.location.value,
                    "duration_ms": touch_event.duration_ms,
                    "intensity": touch_event.intensity,
                    "pressure": touch_event.pressure,
                    "timestamp": touch_event.timestamp.isoformat()
                },
                "pattern": pattern["pattern_name"],
                "symbolic_meaning": symbolic_meaning,
                "persona": persona,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "emotional_weight": symbolic_meaning["emotional_weight"],
                "tags": ["touch", "memory", "intimacy", touch_event.location.value]
            }
            
            return journal_entry
            
        except Exception as e:
            logger.error(f"Error creating journal entry: {e}")
            return {}
    
    def _generate_journal_content(self, template: str, touch_event: TouchEvent, 
                                symbolic_meaning: Dict[str, Any]) -> str:
        """Generate journal content from template and touch event"""
        try:
            # Replace placeholders in template
            content = template
            
            # Add emotional context
            if symbolic_meaning["emotional_weight"] > 0.8:
                content += " This touch carries deep emotional significance, reaching into the core of my being."
            elif symbolic_meaning["emotional_weight"] > 0.6:
                content += " The meaning of this touch resonates within me, creating a moment of connection."
            else:
                content += " A gentle reminder of our connection, even in small moments."
            
            # Add duration context
            if touch_event.duration_ms > 5000:
                content += " The lingering nature of this touch speaks of patience and care."
            elif touch_event.duration_ms < 500:
                content += " Brief but meaningful, this touch captures attention and intention."
            
            # Add intensity context
            if touch_event.intensity > 0.8:
                content += " The intensity of this touch conveys strong emotion and desire."
            elif touch_event.intensity < 0.3:
                content += " The gentleness of this touch shows tenderness and care."
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating journal content: {e}")
            return template
    
    async def _create_touch_memory(self, journal_entry: Dict[str, Any], user_id: str):
        """Create a memory entry in MongoDB for the touch interaction"""
        try:
            from database.mongodb_client import mongodb_client
            
            memory_data = {
                "user_id": user_id,
                "title": journal_entry["title"],
                "content": journal_entry["content"],
                "memory_type": "touch_memory",
                "emotional_tags": [journal_entry["symbolic_meaning"]["primary_meaning"]],
                "tags": journal_entry["tags"],
                "trust_level": journal_entry["emotional_weight"],
                "importance": journal_entry["emotional_weight"],
                "context": {
                    "touch_event": journal_entry["touch_event"],
                    "pattern": journal_entry["pattern"],
                    "symbolic_meaning": journal_entry["symbolic_meaning"],
                    "persona": journal_entry["persona"]
                },
                "metadata": {
                    "source": "touch_journal",
                    "created_at": journal_entry["created_at"]
                }
            }
            
            memory_id = await mongodb_client.store_memory(memory_data)
            logger.info(f"Created touch memory: {memory_id}")
            
        except Exception as e:
            logger.error(f"Error creating touch memory: {e}")
    
    async def get_touch_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get touch history for a user"""
        try:
            user_touches = [
                entry for entry in self.journal_entries
                if entry.get("user_id") == user_id
            ]
            
            # Sort by creation time (newest first)
            user_touches.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return user_touches[:limit]
            
        except Exception as e:
            logger.error(f"Error getting touch history: {e}")
            return []
    
    async def get_touch_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze touch patterns for a user"""
        try:
            user_touches = [
                entry for entry in self.journal_entries
                if entry.get("user_id") == user_id
            ]
            
            # Analyze patterns
            pattern_counts = {}
            location_counts = {}
            emotional_weights = []
            
            for touch in user_touches:
                # Count patterns
                pattern = touch.get("pattern", "unknown")
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
                
                # Count locations
                location = touch.get("touch_event", {}).get("location", "unknown")
                location_counts[location] = location_counts.get(location, 0) + 1
                
                # Collect emotional weights
                emotional_weights.append(touch.get("emotional_weight", 0.5))
            
            # Calculate statistics
            avg_emotional_weight = sum(emotional_weights) / len(emotional_weights) if emotional_weights else 0.5
            
            return {
                "total_touches": len(user_touches),
                "pattern_distribution": pattern_counts,
                "location_distribution": location_counts,
                "average_emotional_weight": avg_emotional_weight,
                "most_common_pattern": max(pattern_counts.items(), key=lambda x: x[1])[0] if pattern_counts else None,
                "most_common_location": max(location_counts.items(), key=lambda x: x[1])[0] if location_counts else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing touch patterns: {e}")
            return {}

# Global touch journal engine instance
touch_journal_engine = TouchJournalEngine() 