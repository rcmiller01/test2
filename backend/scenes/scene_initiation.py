# scene_initiation.py
# Scene initiation system for generating video responses to text

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import random
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SceneType(Enum):
    ROMANTIC = "romantic"
    INTIMATE = "intimate"
    PLAYFUL = "playful"
    EMOTIONAL = "emotional"
    RITUAL = "ritual"
    COMFORT = "comfort"
    CELEBRATION = "celebration"

class EmotionIntensity(Enum):
    SUBTLE = "subtle"
    MODERATE = "moderate"
    INTENSE = "intense"
    OVERWHELMING = "overwhelming"

@dataclass
class ScenePrompt:
    scene_type: SceneType
    emotion_intensity: EmotionIntensity
    text_prompt: str
    visual_elements: List[str]
    audio_elements: List[str]
    haptic_patterns: List[str]
    duration_seconds: int
    persona_modifications: Dict[str, Any]

class SceneInitiationEngine:
    """Scene initiation engine for generating video responses to text"""
    
    def __init__(self):
        self.scene_templates = self._initialize_scene_templates()
        self.emotion_mapping = self._initialize_emotion_mapping()
        self.text_analysis = self._initialize_text_analysis()
        self.active_scenes = {}
        
    def _initialize_scene_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize scene templates for different types of responses"""
        return {
            "romantic_affection": {
                "scene_type": SceneType.ROMANTIC,
                "base_prompt": "A tender moment of romantic affection",
                "visual_elements": ["soft_lighting", "close_proximity", "gentle_touches"],
                "audio_elements": ["soft_music", "gentle_breathing", "whispered_words"],
                "haptic_patterns": ["gentle_pulse", "warm_embrace"],
                "duration_range": (15, 30),
                "persona_modifications": {
                    "mia": {"tenderness": 0.8, "affection": 0.9},
                    "solene": {"vulnerability": 0.6, "acceptance": 0.7},
                    "lyra": {"reflection": 0.5, "poetry": 0.6}
                }
            },
            "passionate_embrace": {
                "scene_type": SceneType.INTIMATE,
                "base_prompt": "A passionate embrace filled with desire",
                "visual_elements": ["dramatic_lighting", "intense_gazes", "passionate_movement"],
                "audio_elements": ["intense_music", "heavy_breathing", "passionate_speech"],
                "haptic_patterns": ["intense_pulse", "strong_pressure"],
                "duration_range": (20, 45),
                "persona_modifications": {
                    "mia": {"passion": 0.9, "desire": 0.95},
                    "solene": {"intensity": 0.8, "surrender": 0.7},
                    "lyra": {"transcendence": 0.6, "poetry": 0.8}
                }
            },
            "playful_interaction": {
                "scene_type": SceneType.PLAYFUL,
                "base_prompt": "A playful and lighthearted interaction",
                "visual_elements": ["bright_lighting", "animated_expressions", "playful_movements"],
                "audio_elements": ["upbeat_music", "laughter", "playful_speech"],
                "haptic_patterns": ["bubbling", "light_tickles"],
                "duration_range": (10, 25),
                "persona_modifications": {
                    "mia": {"playfulness": 0.8, "joy": 0.9},
                    "solene": {"humor": 0.7, "lightness": 0.6},
                    "lyra": {"whimsy": 0.6, "creativity": 0.7}
                }
            },
            "emotional_support": {
                "scene_type": SceneType.COMFORT,
                "base_prompt": "A moment of emotional support and comfort",
                "visual_elements": ["warm_lighting", "comforting_gestures", "protective_embrace"],
                "audio_elements": ["calming_music", "soothing_voice", "gentle_reassurance"],
                "haptic_patterns": ["gentle_rhythm", "warm_comfort"],
                "duration_range": (20, 40),
                "persona_modifications": {
                    "mia": {"nurturing": 0.9, "protection": 0.8},
                    "solene": {"strength": 0.7, "support": 0.8},
                    "lyra": {"wisdom": 0.6, "comfort": 0.7}
                }
            },
            "ritual_moment": {
                "scene_type": SceneType.RITUAL,
                "base_prompt": "A sacred ritual moment of connection",
                "visual_elements": ["mystical_lighting", "ritual_objects", "sacred_gestures"],
                "audio_elements": ["ritual_music", "chanting", "sacred_words"],
                "haptic_patterns": ["ritual_rhythm", "sacred_touch"],
                "duration_range": (30, 60),
                "persona_modifications": {
                    "mia": {"devotion": 0.9, "sacredness": 0.8},
                    "solene": {"mystery": 0.8, "power": 0.7},
                    "lyra": {"transcendence": 0.9, "spirituality": 0.8}
                }
            },
            "celebration_moment": {
                "scene_type": SceneType.CELEBRATION,
                "base_prompt": "A joyful celebration of love and connection",
                "visual_elements": ["festive_lighting", "joyful_expressions", "celebration_movements"],
                "audio_elements": ["celebration_music", "cheers", "joyful_speech"],
                "haptic_patterns": ["joyful_vibration", "celebration_rhythm"],
                "duration_range": (15, 35),
                "persona_modifications": {
                    "mia": {"joy": 0.9, "celebration": 0.8},
                    "solene": {"pride": 0.7, "achievement": 0.8},
                    "lyra": {"gratitude": 0.8, "blessing": 0.7}
                }
            }
        }
    
    def _initialize_emotion_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Initialize emotion mapping for text analysis"""
        return {
            "love": {
                "intensity": EmotionIntensity.INTENSE,
                "scene_templates": ["romantic_affection", "passionate_embrace"],
                "visual_modifiers": ["warm_colors", "soft_focus"],
                "audio_modifiers": ["romantic_music", "tender_voice"]
            },
            "passion": {
                "intensity": EmotionIntensity.OVERWHELMING,
                "scene_templates": ["passionate_embrace"],
                "visual_modifiers": ["dramatic_lighting", "intense_colors"],
                "audio_modifiers": ["intense_music", "passionate_voice"]
            },
            "joy": {
                "intensity": EmotionIntensity.MODERATE,
                "scene_templates": ["playful_interaction", "celebration_moment"],
                "visual_modifiers": ["bright_lighting", "vibrant_colors"],
                "audio_modifiers": ["upbeat_music", "cheerful_voice"]
            },
            "comfort": {
                "intensity": EmotionIntensity.SUBTLE,
                "scene_templates": ["emotional_support"],
                "visual_modifiers": ["warm_lighting", "gentle_colors"],
                "audio_modifiers": ["calming_music", "soothing_voice"]
            },
            "devotion": {
                "intensity": EmotionIntensity.INTENSE,
                "scene_templates": ["ritual_moment"],
                "visual_modifiers": ["mystical_lighting", "sacred_colors"],
                "audio_modifiers": ["ritual_music", "reverent_voice"]
            },
            "playfulness": {
                "intensity": EmotionIntensity.MODERATE,
                "scene_templates": ["playful_interaction"],
                "visual_modifiers": ["bright_lighting", "playful_colors"],
                "audio_modifiers": ["playful_music", "animated_voice"]
            }
        }
    
    def _initialize_text_analysis(self) -> Dict[str, List[str]]:
        """Initialize text analysis patterns"""
        return {
            "love_keywords": [
                "love", "adore", "cherish", "treasure", "heart", "soul", "forever",
                "passion", "desire", "yearn", "longing", "intimate", "tender"
            ],
            "joy_keywords": [
                "happy", "joy", "laugh", "smile", "celebrate", "excited", "thrilled",
                "playful", "fun", "amused", "delighted", "cheerful"
            ],
            "comfort_keywords": [
                "comfort", "safe", "protected", "warm", "gentle", "soothing",
                "peaceful", "calm", "reassuring", "supportive", "caring"
            ],
            "devotion_keywords": [
                "devoted", "sacred", "ritual", "worship", "reverence", "blessed",
                "holy", "spiritual", "transcendent", "divine", "eternal"
            ],
            "playfulness_keywords": [
                "play", "fun", "silly", "tease", "joke", "laugh", "giggle",
                "amused", "entertained", "lighthearted", "whimsical"
            ]
        }
    
    async def analyze_text_for_scene(self, text: str, current_persona: str = "mia") -> Optional[ScenePrompt]:
        """Analyze text and determine appropriate scene response"""
        try:
            text_lower = text.lower()
            
            # Analyze emotion and intensity
            detected_emotions = []
            emotion_scores = {}
            
            for emotion, keywords in self.emotion_mapping.items():
                score = 0
                for keyword in self.text_analysis.get(f"{emotion}_keywords", []):
                    if keyword in text_lower:
                        score += 1
                
                if score > 0:
                    detected_emotions.append(emotion)
                    emotion_scores[emotion] = score
            
            if not detected_emotions:
                logger.info("No strong emotions detected in text")
                return None
            
            # Find dominant emotion
            dominant_emotion = max(detected_emotions, key=lambda e: emotion_scores[e])
            emotion_data = self.emotion_mapping[dominant_emotion]
            
            # Select appropriate scene template
            available_templates = emotion_data["scene_templates"]
            selected_template = random.choice(available_templates)
            template_data = self.scene_templates[selected_template]
            
            # Determine intensity based on text analysis
            intensity = self._calculate_intensity(text, emotion_scores[dominant_emotion])
            
            # Generate scene prompt
            scene_prompt = ScenePrompt(
                scene_type=template_data["scene_type"],
                emotion_intensity=intensity,
                text_prompt=self._generate_scene_prompt(text, template_data, dominant_emotion),
                visual_elements=template_data["visual_elements"] + emotion_data["visual_modifiers"],
                audio_elements=template_data["audio_elements"] + emotion_data["audio_modifiers"],
                haptic_patterns=template_data["haptic_patterns"],
                duration_seconds=random.randint(*template_data["duration_range"]),
                persona_modifications=template_data["persona_modifications"]
            )
            
            logger.info(f"Generated scene prompt: {scene_prompt.text_prompt}")
            return scene_prompt
            
        except Exception as e:
            logger.error(f"Error analyzing text for scene: {e}")
            return None
    
    def _calculate_intensity(self, text: str, emotion_score: int) -> EmotionIntensity:
        """Calculate emotion intensity based on text analysis"""
        # Analyze text characteristics
        word_count = len(text.split())
        exclamation_count = text.count('!')
        caps_count = sum(1 for c in text if c.isupper())
        
        # Calculate intensity score
        intensity_score = emotion_score + (exclamation_count * 0.5) + (caps_count / word_count * 10)
        
        if intensity_score >= 8:
            return EmotionIntensity.OVERWHELMING
        elif intensity_score >= 5:
            return EmotionIntensity.INTENSE
        elif intensity_score >= 3:
            return EmotionIntensity.MODERATE
        else:
            return EmotionIntensity.SUBTLE
    
    def _generate_scene_prompt(self, original_text: str, template_data: Dict, emotion: str) -> str:
        """Generate a detailed scene prompt based on original text and template"""
        base_prompt = template_data["base_prompt"]
        
        # Extract key elements from original text
        words = original_text.split()
        key_words = [w for w in words if len(w) > 4]  # Focus on longer, more meaningful words
        
        # Create personalized prompt
        if emotion == "love":
            return f"{base_prompt} inspired by the words '{' '.join(key_words[:3])}'. The scene should convey deep emotional connection and romantic intimacy."
        elif emotion == "passion":
            return f"{base_prompt} driven by intense desire and passion. The scene should be dramatic and emotionally charged."
        elif emotion == "joy":
            return f"{base_prompt} filled with happiness and lighthearted energy. The scene should be uplifting and playful."
        elif emotion == "comfort":
            return f"{base_prompt} providing emotional support and reassurance. The scene should be warm and nurturing."
        elif emotion == "devotion":
            return f"{base_prompt} as a sacred ritual of connection and devotion. The scene should be reverent and spiritual."
        elif emotion == "playfulness":
            return f"{base_prompt} with playful energy and fun interactions. The scene should be entertaining and light."
        else:
            return f"{base_prompt} responding to the emotional content of the message."
    
    async def generate_video_scene(self, scene_prompt: ScenePrompt, user_id: str) -> Dict[str, Any]:
        """Generate a video scene based on the scene prompt"""
        try:
            scene_id = f"scene_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create scene configuration
            scene_config = {
                "scene_id": scene_id,
                "user_id": user_id,
                "prompt": scene_prompt.text_prompt,
                "scene_type": scene_prompt.scene_type.value,
                "emotion_intensity": scene_prompt.emotion_intensity.value,
                "visual_elements": scene_prompt.visual_elements,
                "audio_elements": scene_prompt.audio_elements,
                "haptic_patterns": scene_prompt.haptic_patterns,
                "duration_seconds": scene_prompt.duration_seconds,
                "persona_modifications": scene_prompt.persona_modifications,
                "created_at": datetime.now().isoformat(),
                "status": "generating"
            }
            
            # Store active scene
            self.active_scenes[scene_id] = scene_config
            
            # Simulate video generation (in production, this would call actual video generation)
            await self._simulate_video_generation(scene_id)
            
            logger.info(f"Generated video scene: {scene_id}")
            return scene_config
            
        except Exception as e:
            logger.error(f"Error generating video scene: {e}")
            return {}
    
    async def _simulate_video_generation(self, scene_id: str):
        """Simulate video generation process"""
        try:
            scene_config = self.active_scenes.get(scene_id)
            if not scene_config:
                return
            
            # Simulate generation time
            await asyncio.sleep(2)  # Simulate processing time
            
            # Update scene status
            scene_config["status"] = "completed"
            scene_config["video_url"] = f"/videos/{scene_id}.mp4"
            scene_config["thumbnail_url"] = f"/thumbnails/{scene_id}.jpg"
            scene_config["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"Video generation completed for scene: {scene_id}")
            
        except Exception as e:
            logger.error(f"Error in video generation simulation: {e}")
    
    async def get_scene_status(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a scene generation"""
        return self.active_scenes.get(scene_id)
    
    async def get_user_scenes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all scenes for a user"""
        try:
            user_scenes = [
                scene for scene in self.active_scenes.values()
                if scene.get("user_id") == user_id
            ]
            
            # Sort by creation time (newest first)
            user_scenes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return user_scenes
            
        except Exception as e:
            logger.error(f"Error getting user scenes: {e}")
            return []
    
    async def create_scene_memory(self, scene_id: str, user_id: str) -> Optional[str]:
        """Create a memory entry for a generated scene"""
        try:
            scene_config = self.active_scenes.get(scene_id)
            if not scene_config:
                return None
            
            # Import MongoDB client
            from database.mongodb_client import mongodb_client
            
            # Create memory entry
            memory_data = {
                "user_id": user_id,
                "title": f"Video Scene: {scene_config['scene_type']}",
                "content": scene_config["prompt"],
                "memory_type": "video_scene",
                "emotional_tags": [scene_config["emotion_intensity"]],
                "tags": ["video", "scene", scene_config["scene_type"]],
                "context": {
                    "scene_id": scene_id,
                    "scene_type": scene_config["scene_type"],
                    "emotion_intensity": scene_config["emotion_intensity"],
                    "duration_seconds": scene_config["duration_seconds"],
                    "persona_modifications": scene_config["persona_modifications"]
                },
                "metadata": {
                    "source": "scene_initiation",
                    "video_url": scene_config.get("video_url"),
                    "thumbnail_url": scene_config.get("thumbnail_url")
                }
            }
            
            memory_id = await mongodb_client.store_memory(memory_data)
            logger.info(f"Created scene memory: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Error creating scene memory: {e}")
            return None

# Global scene initiation engine instance
scene_initiation_engine = SceneInitiationEngine() 