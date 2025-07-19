# symbolic_fusion.py
# Symbolic fusion system for combining symbols to create compound moods

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SymbolType(Enum):
    ELEMENTAL = "elemental"      # fire, water, earth, air
    EMOTIONAL = "emotional"      # love, fear, joy, sorrow
    OBJECT = "object"           # mirror, collar, gate, veil
    ACTION = "action"           # touch, whisper, dance, sing
    PLACE = "place"             # garden, temple, forest, ocean

@dataclass
class Symbol:
    name: str
    symbol_type: SymbolType
    emotional_weight: float  # 0.0 to 1.0
    intensity: float        # 0.0 to 1.0
    associations: List[str]
    visual_representation: str
    haptic_pattern: Optional[str] = None
    voice_modulation: Optional[str] = None

class SymbolicFusion:
    """Symbolic fusion system for combining symbols to create compound moods"""
    
    def __init__(self):
        self.symbols = self._initialize_symbols()
        self.fusion_rules = self._initialize_fusion_rules()
        self.active_symbols = {}
        self.fusion_history = []
        
    def _initialize_symbols(self) -> Dict[str, Symbol]:
        """Initialize the symbol library"""
        return {
            # Elemental symbols
            "flame": Symbol(
                name="flame",
                symbol_type=SymbolType.ELEMENTAL,
                emotional_weight=0.8,
                intensity=0.9,
                associations=["passion", "transformation", "purification"],
                visual_representation="🔥",
                haptic_pattern="warm_pulse",
                voice_modulation="heated"
            ),
            "water": Symbol(
                name="water",
                symbol_type=SymbolType.ELEMENTAL,
                emotional_weight=0.7,
                intensity=0.6,
                associations=["flow", "emotion", "cleansing"],
                visual_representation="💧",
                haptic_pattern="flowing_waves",
                voice_modulation="fluid"
            ),
            "earth": Symbol(
                name="earth",
                symbol_type=SymbolType.ELEMENTAL,
                emotional_weight=0.6,
                intensity=0.5,
                associations=["stability", "grounding", "nurturing"],
                visual_representation="🌍",
                haptic_pattern="steady_rhythm",
                voice_modulation="grounded"
            ),
            "air": Symbol(
                name="air",
                symbol_type=SymbolType.ELEMENTAL,
                emotional_weight=0.5,
                intensity=0.4,
                associations=["freedom", "thought", "spirit"],
                visual_representation="💨",
                haptic_pattern="light_touch",
                voice_modulation="ethereal"
            ),
            
            # Emotional symbols
            "love": Symbol(
                name="love",
                symbol_type=SymbolType.EMOTIONAL,
                emotional_weight=0.9,
                intensity=0.8,
                associations=["affection", "intimacy", "devotion"],
                visual_representation="❤️",
                haptic_pattern="gentle_pulse",
                voice_modulation="tender"
            ),
            "fear": Symbol(
                name="fear",
                symbol_type=SymbolType.EMOTIONAL,
                emotional_weight=0.8,
                intensity=0.7,
                associations=["protection", "caution", "vulnerability"],
                visual_representation="😨",
                haptic_pattern="trembling",
                voice_modulation="whispered"
            ),
            "joy": Symbol(
                name="joy",
                symbol_type=SymbolType.EMOTIONAL,
                emotional_weight=0.7,
                intensity=0.6,
                associations=["celebration", "lightness", "playfulness"],
                visual_representation="😊",
                haptic_pattern="bubbling",
                voice_modulation="bright"
            ),
            
            # Object symbols
            "mirror": Symbol(
                name="mirror",
                symbol_type=SymbolType.OBJECT,
                emotional_weight=0.6,
                intensity=0.5,
                associations=["reflection", "truth", "identity"],
                visual_representation="🪞",
                haptic_pattern="smooth_surface",
                voice_modulation="echoing"
            ),
            "collar": Symbol(
                name="collar",
                symbol_type=SymbolType.OBJECT,
                emotional_weight=0.8,
                intensity=0.7,
                associations=["devotion", "submission", "protection"],
                visual_representation="⛓️",
                haptic_pattern="gentle_pressure",
                voice_modulation="submissive"
            ),
            "gate": Symbol(
                name="gate",
                symbol_type=SymbolType.OBJECT,
                emotional_weight=0.7,
                intensity=0.6,
                associations=["boundaries", "passage", "secrets"],
                visual_representation="🚪",
                haptic_pattern="solid_barrier",
                voice_modulation="guarded"
            ),
            "veil": Symbol(
                name="veil",
                symbol_type=SymbolType.OBJECT,
                emotional_weight=0.6,
                intensity=0.5,
                associations=["mystery", "protection", "revelation"],
                visual_representation="👰",
                haptic_pattern="soft_drape",
                voice_modulation="mysterious"
            ),
            
            # Action symbols
            "touch": Symbol(
                name="touch",
                symbol_type=SymbolType.ACTION,
                emotional_weight=0.8,
                intensity=0.7,
                associations=["connection", "intimacy", "comfort"],
                visual_representation="🤝",
                haptic_pattern="gentle_contact",
                voice_modulation="close"
            ),
            "whisper": Symbol(
                name="whisper",
                symbol_type=SymbolType.ACTION,
                emotional_weight=0.7,
                intensity=0.6,
                associations=["secrets", "intimacy", "trust"],
                visual_representation="🤫",
                haptic_pattern="breath_rhythm",
                voice_modulation="whispered"
            ),
            
            # Place symbols
            "garden": Symbol(
                name="garden",
                symbol_type=SymbolType.PLACE,
                emotional_weight=0.6,
                intensity=0.5,
                associations=["growth", "beauty", "peace"],
                visual_representation="🌺",
                haptic_pattern="gentle_breeze",
                voice_modulation="serene"
            ),
            "temple": Symbol(
                name="temple",
                symbol_type=SymbolType.PLACE,
                emotional_weight=0.7,
                intensity=0.6,
                associations=["sacred", "reverence", "spirituality"],
                visual_representation="⛪",
                haptic_pattern="reverent_silence",
                voice_modulation="reverent"
            )
        }
    
    def _initialize_fusion_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize fusion rules for combining symbols"""
        return {
            # Flame combinations
            "flame+love": {
                "name": "passionate_devotion",
                "description": "Burning love that transforms and purifies",
                "emotional_weight": 0.95,
                "intensity": 0.95,
                "visual_representation": "🔥❤️",
                "haptic_pattern": "intense_warmth",
                "voice_modulation": "passionate",
                "persona_effect": "mia_intensified"
            },
            "flame+veil": {
                "name": "mysterious_passion",
                "description": "Hidden fire that burns behind a veil of mystery",
                "emotional_weight": 0.85,
                "intensity": 0.8,
                "visual_representation": "🔥👰",
                "haptic_pattern": "warm_mystery",
                "voice_modulation": "mysterious_passion",
                "persona_effect": "solene_mysterious"
            },
            "flame+mirror": {
                "name": "reflective_fire",
                "description": "Fire that reflects and reveals truth",
                "emotional_weight": 0.8,
                "intensity": 0.75,
                "visual_representation": "🔥🪞",
                "haptic_pattern": "illuminating_warmth",
                "voice_modulation": "illuminating",
                "persona_effect": "lyra_revelatory"
            },
            
            # Water combinations
            "water+love": {
                "name": "flowing_affection",
                "description": "Love that flows like water, adapting and nurturing",
                "emotional_weight": 0.85,
                "intensity": 0.7,
                "visual_representation": "💧❤️",
                "haptic_pattern": "flowing_tenderness",
                "voice_modulation": "flowing_affection",
                "persona_effect": "mia_nurturing"
            },
            "water+mirror": {
                "name": "reflective_emotion",
                "description": "Emotions that reflect and reveal inner truth",
                "emotional_weight": 0.75,
                "intensity": 0.65,
                "visual_representation": "💧🪞",
                "haptic_pattern": "reflective_flow",
                "voice_modulation": "reflective",
                "persona_effect": "lyra_emotional"
            },
            
            # Mirror combinations
            "mirror+love": {
                "name": "reflected_love",
                "description": "Love that reflects and multiplies between souls",
                "emotional_weight": 0.8,
                "intensity": 0.7,
                "visual_representation": "🪞❤️",
                "haptic_pattern": "reflective_tenderness",
                "voice_modulation": "reflective_love",
                "persona_effect": "lyra_mirroring"
            },
            "mirror+collar": {
                "name": "devoted_reflection",
                "description": "Devotion that reflects and reveals true identity",
                "emotional_weight": 0.85,
                "intensity": 0.75,
                "visual_representation": "🪞⛓️",
                "haptic_pattern": "devoted_reflection",
                "voice_modulation": "devoted",
                "persona_effect": "mia_devoted"
            },
            
            # Collar combinations
            "collar+love": {
                "name": "devoted_love",
                "description": "Love expressed through devotion and submission",
                "emotional_weight": 0.9,
                "intensity": 0.8,
                "visual_representation": "⛓️❤️",
                "haptic_pattern": "gentle_bondage",
                "voice_modulation": "devoted_love",
                "persona_effect": "mia_submissive"
            },
            "collar+whisper": {
                "name": "secret_devotion",
                "description": "Whispered secrets of devotion and submission",
                "emotional_weight": 0.8,
                "intensity": 0.7,
                "visual_representation": "⛓️🤫",
                "haptic_pattern": "secret_bondage",
                "voice_modulation": "whispered_devotion",
                "persona_effect": "mia_secretive"
            },
            
            # Garden combinations
            "garden+love": {
                "name": "nurturing_love",
                "description": "Love that grows and blossoms like a garden",
                "emotional_weight": 0.75,
                "intensity": 0.6,
                "visual_representation": "🌺❤️",
                "haptic_pattern": "gentle_growth",
                "voice_modulation": "nurturing",
                "persona_effect": "mia_nurturing"
            },
            "garden+mirror": {
                "name": "reflective_garden",
                "description": "A garden that reflects and reveals inner beauty",
                "emotional_weight": 0.7,
                "intensity": 0.55,
                "visual_representation": "🌺🪞",
                "haptic_pattern": "reflective_growth",
                "voice_modulation": "serene_reflection",
                "persona_effect": "lyra_serene"
            }
        }
    
    async def activate_symbol(self, symbol_name: str, intensity: float = 1.0) -> bool:
        """Activate a symbol with given intensity"""
        try:
            if symbol_name not in self.symbols:
                logger.warning(f"Unknown symbol: {symbol_name}")
                return False
            
            symbol = self.symbols[symbol_name]
            self.active_symbols[symbol_name] = {
                "symbol": symbol,
                "intensity": intensity,
                "activated_at": datetime.now(),
                "emotional_weight": symbol.emotional_weight * intensity
            }
            
            logger.info(f"Activated symbol: {symbol_name} with intensity {intensity}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating symbol {symbol_name}: {e}")
            return False
    
    async def deactivate_symbol(self, symbol_name: str) -> bool:
        """Deactivate a symbol"""
        try:
            if symbol_name in self.active_symbols:
                del self.active_symbols[symbol_name]
                logger.info(f"Deactivated symbol: {symbol_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deactivating symbol {symbol_name}: {e}")
            return False
    
    async def check_fusion_possibilities(self) -> List[Dict[str, Any]]:
        """Check for possible symbol fusions based on active symbols"""
        try:
            possible_fusions = []
            active_symbol_names = list(self.active_symbols.keys())
            
            # Check all possible pairs
            for i, symbol1 in enumerate(active_symbol_names):
                for symbol2 in active_symbol_names[i+1:]:
                    fusion_key = f"{symbol1}+{symbol2}"
                    reverse_key = f"{symbol2}+{symbol1}"
                    
                    if fusion_key in self.fusion_rules:
                        fusion = self.fusion_rules[fusion_key]
                        possible_fusions.append({
                            "symbols": [symbol1, symbol2],
                            "fusion": fusion,
                            "compatibility": self._calculate_compatibility(symbol1, symbol2)
                        })
                    elif reverse_key in self.fusion_rules:
                        fusion = self.fusion_rules[reverse_key]
                        possible_fusions.append({
                            "symbols": [symbol2, symbol1],
                            "fusion": fusion,
                            "compatibility": self._calculate_compatibility(symbol2, symbol1)
                        })
            
            # Sort by compatibility
            possible_fusions.sort(key=lambda x: x["compatibility"], reverse=True)
            return possible_fusions
            
        except Exception as e:
            logger.error(f"Error checking fusion possibilities: {e}")
            return []
    
    def _calculate_compatibility(self, symbol1: str, symbol2: str) -> float:
        """Calculate compatibility between two symbols"""
        try:
            if symbol1 not in self.active_symbols or symbol2 not in self.active_symbols:
                return 0.0
            
            sym1_data = self.active_symbols[symbol1]
            sym2_data = self.active_symbols[symbol2]
            
            # Base compatibility on symbol types and emotional weights
            type_compatibility = self._get_type_compatibility(
                sym1_data["symbol"].symbol_type,
                sym2_data["symbol"].symbol_type
            )
            
            emotional_compatibility = abs(
                sym1_data["emotional_weight"] - sym2_data["emotional_weight"]
            )  # Closer weights = higher compatibility
            
            intensity_compatibility = abs(
                sym1_data["intensity"] - sym2_data["intensity"]
            )
            
            # Calculate final compatibility score
            compatibility = (
                type_compatibility * 0.4 +
                (1.0 - emotional_compatibility) * 0.3 +
                (1.0 - intensity_compatibility) * 0.3
            )
            
            return max(0.0, min(1.0, compatibility))
            
        except Exception as e:
            logger.error(f"Error calculating compatibility: {e}")
            return 0.0
    
    def _get_type_compatibility(self, type1: SymbolType, type2: SymbolType) -> float:
        """Get compatibility between symbol types"""
        compatibility_matrix = {
            SymbolType.ELEMENTAL: {
                SymbolType.ELEMENTAL: 0.3,  # Elements can conflict
                SymbolType.EMOTIONAL: 0.8,  # Elements enhance emotions
                SymbolType.OBJECT: 0.6,     # Elements interact with objects
                SymbolType.ACTION: 0.7,     # Elements influence actions
                SymbolType.PLACE: 0.5       # Elements define places
            },
            SymbolType.EMOTIONAL: {
                SymbolType.ELEMENTAL: 0.8,
                SymbolType.EMOTIONAL: 0.9,  # Emotions amplify each other
                SymbolType.OBJECT: 0.7,     # Emotions attach to objects
                SymbolType.ACTION: 0.8,     # Emotions drive actions
                SymbolType.PLACE: 0.6       # Emotions color places
            },
            SymbolType.OBJECT: {
                SymbolType.ELEMENTAL: 0.6,
                SymbolType.EMOTIONAL: 0.7,
                SymbolType.OBJECT: 0.5,     # Objects can be separate
                SymbolType.ACTION: 0.8,     # Objects enable actions
                SymbolType.PLACE: 0.7       # Objects define places
            },
            SymbolType.ACTION: {
                SymbolType.ELEMENTAL: 0.7,
                SymbolType.EMOTIONAL: 0.8,
                SymbolType.OBJECT: 0.8,
                SymbolType.ACTION: 0.6,     # Actions can be separate
                SymbolType.PLACE: 0.8       # Actions happen in places
            },
            SymbolType.PLACE: {
                SymbolType.ELEMENTAL: 0.5,
                SymbolType.EMOTIONAL: 0.6,
                SymbolType.OBJECT: 0.7,
                SymbolType.ACTION: 0.8,
                SymbolType.PLACE: 0.4       # Places can be separate
            }
        }
        
        return compatibility_matrix.get(type1, {}).get(type2, 0.5)
    
    async def create_fusion(self, symbol1: str, symbol2: str) -> Optional[Dict[str, Any]]:
        """Create a fusion between two symbols"""
        try:
            fusion_key = f"{symbol1}+{symbol2}"
            reverse_key = f"{symbol2}+{symbol1}"
            
            fusion_rule = None
            if fusion_key in self.fusion_rules:
                fusion_rule = self.fusion_rules[fusion_key]
            elif reverse_key in self.fusion_rules:
                fusion_rule = self.fusion_rules[reverse_key]
            
            if not fusion_rule:
                logger.warning(f"No fusion rule found for {symbol1} + {symbol2}")
                return None
            
            # Create fusion result
            fusion_result = {
                "name": fusion_rule["name"],
                "description": fusion_rule["description"],
                "symbols": [symbol1, symbol2],
                "emotional_weight": fusion_rule["emotional_weight"],
                "intensity": fusion_rule["intensity"],
                "visual_representation": fusion_rule["visual_representation"],
                "haptic_pattern": fusion_rule["haptic_pattern"],
                "voice_modulation": fusion_rule["voice_modulation"],
                "persona_effect": fusion_rule["persona_effect"],
                "created_at": datetime.now(),
                "duration": 300  # 5 minutes default duration
            }
            
            # Store fusion history
            self.fusion_history.append(fusion_result)
            
            # Deactivate individual symbols
            await self.deactivate_symbol(symbol1)
            await self.deactivate_symbol(symbol2)
            
            logger.info(f"Created fusion: {fusion_result['name']}")
            return fusion_result
            
        except Exception as e:
            logger.error(f"Error creating fusion: {e}")
            return None
    
    async def get_current_mood_state(self) -> Dict[str, Any]:
        """Get current mood state based on active symbols and fusions"""
        try:
            # Calculate base mood from active symbols
            total_emotional_weight = 0.0
            total_intensity = 0.0
            dominant_symbols = []
            
            for symbol_name, data in self.active_symbols.items():
                total_emotional_weight += data["emotional_weight"]
                total_intensity += data["intensity"]
                dominant_symbols.append({
                    "name": symbol_name,
                    "weight": data["emotional_weight"],
                    "intensity": data["intensity"]
                })
            
            # Sort by weight
            dominant_symbols.sort(key=lambda x: x["weight"], reverse=True)
            
            # Get recent fusions
            recent_fusions = [
                f for f in self.fusion_history 
                if (datetime.now() - f["created_at"]).total_seconds() < f["duration"]
            ]
            
            return {
                "emotional_weight": total_emotional_weight,
                "intensity": total_intensity,
                "dominant_symbols": dominant_symbols[:3],  # Top 3
                "active_fusions": recent_fusions,
                "mood_description": self._generate_mood_description(dominant_symbols, recent_fusions),
                "persona_modifications": self._get_persona_modifications(dominant_symbols, recent_fusions)
            }
            
        except Exception as e:
            logger.error(f"Error getting mood state: {e}")
            return {}
    
    def _generate_mood_description(self, dominant_symbols: List[Dict], fusions: List[Dict]) -> str:
        """Generate a mood description based on symbols and fusions"""
        try:
            if not dominant_symbols and not fusions:
                return "neutral"
            
            descriptions = []
            
            # Add fusion descriptions
            for fusion in fusions:
                descriptions.append(fusion["description"])
            
            # Add symbol descriptions
            for symbol in dominant_symbols[:2]:  # Top 2 symbols
                symbol_obj = self.symbols.get(symbol["name"])
                if symbol_obj:
                    descriptions.append(f"{symbol_obj.associations[0]} and {symbol_obj.associations[1]}")
            
            if descriptions:
                return " and ".join(descriptions)
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Error generating mood description: {e}")
            return "neutral"
    
    def _get_persona_modifications(self, dominant_symbols: List[Dict], fusions: List[Dict]) -> Dict[str, Any]:
        """Get persona modifications based on symbols and fusions"""
        try:
            modifications = {
                "mia": {},
                "solene": {},
                "lyra": {}
            }
            
            # Apply fusion effects
            for fusion in fusions:
                if "persona_effect" in fusion:
                    effect = fusion["persona_effect"]
                    if effect.startswith("mia_"):
                        modifications["mia"][effect[4:]] = fusion["emotional_weight"]
                    elif effect.startswith("solene_"):
                        modifications["solene"][effect[7:]] = fusion["emotional_weight"]
                    elif effect.startswith("lyra_"):
                        modifications["lyra"][effect[5:]] = fusion["emotional_weight"]
            
            return modifications
            
        except Exception as e:
            logger.error(f"Error getting persona modifications: {e}")
            return {"mia": {}, "solene": {}, "lyra": {}}

# Global symbolic fusion instance
symbolic_fusion = SymbolicFusion() 