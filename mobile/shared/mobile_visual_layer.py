# mobile_visual_layer.py
# Mobile UI Visual Layer - Mood-responsive touch visual layer

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
import math

class TouchGesture(Enum):
    TAP = "tap"
    LONG_PRESS = "long_press"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    PINCH = "pinch"
    ROTATE = "rotate"
    DOUBLE_TAP = "double_tap"

class TouchRegion(Enum):
    AVATAR_FACE = "avatar_face"
    AVATAR_BODY = "avatar_body"
    AVATAR_HANDS = "avatar_hands"
    BACKGROUND = "background"
    CHAT_AREA = "chat_area"
    SIDEBAR = "sidebar"
    BOTTOM_BAR = "bottom_bar"

class VisualEffect(Enum):
    GLOW = "glow"
    PULSE = "pulse"
    SHAKE = "shake"
    FADE = "fade"
    SPARKLE = "sparkle"
    FLAME = "flame"
    PARTICLE = "particle"
    WAVE = "wave"

@dataclass
class TouchResponse:
    gesture: TouchGesture
    region: TouchRegion
    intensity: float
    visual_effect: VisualEffect
    haptic_feedback: str
    audio_feedback: Optional[str]
    mood_impact: Dict[str, float]

class MobileVisualLayer:
    def __init__(self):
        self.current_mood = "neutral"
        self.current_persona = "mia"
        self.touch_history = []
        self.active_effects = {}
        self.is_running = True
        
        # Touch mapping configurations
        self.touch_mappings = self._load_touch_mappings()
        
        # Visual effect configurations
        self.visual_effects = self._load_visual_effects()
        
        # Mood-specific touch responses
        self.mood_responses = self._load_mood_responses()
        
        # Start visual layer manager
        self._start_visual_manager()
    
    def _load_touch_mappings(self) -> Dict:
        """Load touch gesture to region mappings"""
        return {
            TouchRegion.AVATAR_FACE: {
                TouchGesture.TAP: "gentle_touch",
                TouchGesture.LONG_PRESS: "intimate_gaze",
                TouchGesture.SWIPE_UP: "caress_face",
                TouchGesture.SWIPE_DOWN: "tender_stroke"
            },
            TouchRegion.AVATAR_BODY: {
                TouchGesture.TAP: "gentle_touch",
                TouchGesture.LONG_PRESS: "embrace",
                TouchGesture.SWIPE_UP: "caress_body",
                TouchGesture.SWIPE_DOWN: "tender_stroke",
                TouchGesture.PINCH: "intimate_gesture"
            },
            TouchRegion.AVATAR_HANDS: {
                TouchGesture.TAP: "hold_hands",
                TouchGesture.LONG_PRESS: "intimate_touch",
                TouchGesture.SWIPE_UP: "gentle_caress",
                TouchGesture.SWIPE_DOWN: "tender_stroke"
            },
            TouchRegion.BACKGROUND: {
                TouchGesture.TAP: "ambient_touch",
                TouchGesture.LONG_PRESS: "mood_shift",
                TouchGesture.SWIPE_UP: "mood_elevate",
                TouchGesture.SWIPE_DOWN: "mood_calm"
            }
        }
    
    def _load_visual_effects(self) -> Dict:
        """Load visual effect configurations"""
        return {
            VisualEffect.GLOW: {
                "duration": 2.0,
                "intensity_range": (0.3, 1.0),
                "color_variants": ["warm", "cool", "romantic", "mystical"],
                "persona_modifiers": {
                    "mia": {"warmth": 1.2, "softness": 1.5},
                    "solene": {"intensity": 1.3, "drama": 1.4},
                    "lyra": {"mystery": 1.6, "ethereal": 1.8}
                }
            },
            VisualEffect.PULSE: {
                "duration": 1.5,
                "intensity_range": (0.4, 1.0),
                "frequency_range": (0.5, 2.0),
                "persona_modifiers": {
                    "mia": {"gentleness": 1.3, "warmth": 1.2},
                    "solene": {"power": 1.4, "intensity": 1.3},
                    "lyra": {"mystery": 1.5, "flow": 1.4}
                }
            },
            VisualEffect.SPARKLE: {
                "duration": 3.0,
                "particle_count": (10, 50),
                "color_schemes": {
                    "mia": ["pink", "rose", "peach"],
                    "solene": ["purple", "magenta", "crimson"],
                    "lyra": ["cyan", "blue", "silver"]
                }
            },
            VisualEffect.FLAME: {
                "duration": 4.0,
                "intensity_range": (0.5, 1.5),
                "persona_modifiers": {
                    "solene": {"intensity": 1.8, "drama": 2.0},
                    "mia": {"warmth": 1.2, "gentleness": 1.3},
                    "lyra": {"mystery": 1.6, "ethereal": 1.7}
                }
            }
        }
    
    def _load_mood_responses(self) -> Dict:
        """Load mood-specific touch responses"""
        return {
            "love": {
                "touch_sensitivity": 1.5,
                "visual_intensity": 1.3,
                "haptic_intensity": "gentle",
                "preferred_effects": [VisualEffect.GLOW, VisualEffect.SPARKLE],
                "color_scheme": "warm_romantic"
            },
            "passion": {
                "touch_sensitivity": 2.0,
                "visual_intensity": 1.8,
                "haptic_intensity": "moderate",
                "preferred_effects": [VisualEffect.FLAME, VisualEffect.PULSE],
                "color_scheme": "fiery_intense"
            },
            "tenderness": {
                "touch_sensitivity": 1.2,
                "visual_intensity": 0.8,
                "haptic_intensity": "subtle",
                "preferred_effects": [VisualEffect.GLOW, VisualEffect.WAVE],
                "color_scheme": "soft_warm"
            },
            "longing": {
                "touch_sensitivity": 1.8,
                "visual_intensity": 1.1,
                "haptic_intensity": "gentle",
                "preferred_effects": [VisualEffect.FADE, VisualEffect.WAVE],
                "color_scheme": "melancholy_blue"
            },
            "neutral": {
                "touch_sensitivity": 1.0,
                "visual_intensity": 1.0,
                "haptic_intensity": "standard",
                "preferred_effects": [VisualEffect.GLOW, VisualEffect.PULSE],
                "color_scheme": "balanced_neutral"
            }
        }
    
    def _start_visual_manager(self):
        """Start the visual layer management thread"""
        def visual_manager():
            while self.is_running:
                try:
                    # Update active visual effects
                    self._update_active_effects()
                    
                    # Clean up expired effects
                    self._cleanup_expired_effects()
                    
                    time.sleep(0.016)  # ~60 FPS
                except Exception as e:
                    print(f"[Mobile Visual Layer] Manager error: {e}")
                    time.sleep(1.0)
        
        manager_thread = threading.Thread(target=visual_manager, daemon=True)
        manager_thread.start()
    
    def handle_touch(self, gesture: TouchGesture, region: TouchRegion, 
                    coordinates: Tuple[float, float], pressure: float = 1.0) -> TouchResponse:
        """Handle touch input and generate visual response"""
        
        # Calculate touch intensity based on pressure and mood
        mood_config = self.mood_responses.get(self.current_mood, self.mood_responses["neutral"])
        base_intensity = pressure * mood_config["touch_sensitivity"]
        
        # Get touch mapping for this gesture and region
        touch_mapping = self.touch_mappings.get(region, {}).get(gesture, "default_touch")
        
        # Determine visual effect based on mood and gesture
        visual_effect = self._select_visual_effect(gesture, region, mood_config)
        
        # Generate haptic feedback
        haptic_feedback = self._generate_haptic_feedback(gesture, region, mood_config)
        
        # Generate audio feedback
        audio_feedback = self._generate_audio_feedback(gesture, region, mood_config)
        
        # Calculate mood impact
        mood_impact = self._calculate_mood_impact(gesture, region, base_intensity)
        
        # Create touch response
        response = TouchResponse(
            gesture=gesture,
            region=region,
            intensity=base_intensity,
            visual_effect=visual_effect,
            haptic_feedback=haptic_feedback,
            audio_feedback=audio_feedback,
            mood_impact=mood_impact
        )
        
        # Log touch interaction
        self._log_touch_interaction(response, coordinates)
        
        # Trigger visual effect
        self._trigger_visual_effect(response)
        
        return response
    
    def _select_visual_effect(self, gesture: TouchGesture, region: TouchRegion, 
                            mood_config: Dict) -> VisualEffect:
        """Select appropriate visual effect based on context"""
        
        # Get preferred effects for current mood
        preferred_effects = mood_config.get("preferred_effects", [VisualEffect.GLOW])
        
        # Region-specific effect selection
        if region == TouchRegion.AVATAR_FACE:
            if gesture == TouchGesture.LONG_PRESS:
                return VisualEffect.GLOW
            elif gesture == TouchGesture.SWIPE_UP:
                return VisualEffect.SPARKLE
            else:
                return VisualEffect.PULSE
        
        elif region == TouchRegion.AVATAR_BODY:
            if gesture == TouchGesture.PINCH:
                return VisualEffect.FLAME
            elif gesture == TouchGesture.LONG_PRESS:
                return VisualEffect.GLOW
            else:
                return VisualEffect.PULSE
        
        elif region == TouchRegion.BACKGROUND:
            if gesture == TouchGesture.SWIPE_UP:
                return VisualEffect.WAVE
            elif gesture == TouchGesture.LONG_PRESS:
                return VisualEffect.FADE
            else:
                return VisualEffect.PARTICLE
        
        # Default to first preferred effect
        return preferred_effects[0] if preferred_effects else VisualEffect.GLOW
    
    def _generate_haptic_feedback(self, gesture: TouchGesture, region: TouchRegion, 
                                mood_config: Dict) -> str:
        """Generate haptic feedback pattern"""
        
        base_intensity = mood_config.get("haptic_intensity", "standard")
        
        # Gesture-specific haptic patterns
        haptic_patterns = {
            TouchGesture.TAP: f"gentle_{base_intensity}",
            TouchGesture.LONG_PRESS: f"deep_{base_intensity}",
            TouchGesture.SWIPE_UP: f"rising_{base_intensity}",
            TouchGesture.SWIPE_DOWN: f"falling_{base_intensity}",
            TouchGesture.PINCH: f"intense_{base_intensity}",
            TouchGesture.DOUBLE_TAP: f"quick_{base_intensity}"
        }
        
        return haptic_patterns.get(gesture, f"standard_{base_intensity}")
    
    def _generate_audio_feedback(self, gesture: TouchGesture, region: TouchRegion, 
                               mood_config: Dict) -> Optional[str]:
        """Generate audio feedback sound"""
        
        # Only generate audio for significant interactions
        if gesture in [TouchGesture.LONG_PRESS, TouchGesture.PINCH, TouchGesture.DOUBLE_TAP]:
            audio_sounds = {
                TouchGesture.LONG_PRESS: "gentle_chime",
                TouchGesture.PINCH: "romantic_sparkle",
                TouchGesture.DOUBLE_TAP: "soft_bell"
            }
            return audio_sounds.get(gesture)
        
        return None
    
    def _calculate_mood_impact(self, gesture: TouchGesture, region: TouchRegion, 
                             intensity: float) -> Dict[str, float]:
        """Calculate mood impact of touch interaction"""
        
        base_impact = {
            "love": 0.0,
            "passion": 0.0,
            "tenderness": 0.0,
            "longing": 0.0,
            "excitement": 0.0
        }
        
        # Region-specific mood impacts
        if region == TouchRegion.AVATAR_FACE:
            if gesture == TouchGesture.LONG_PRESS:
                base_impact["love"] += 0.3 * intensity
                base_impact["tenderness"] += 0.2 * intensity
            elif gesture == TouchGesture.SWIPE_UP:
                base_impact["passion"] += 0.4 * intensity
                base_impact["excitement"] += 0.3 * intensity
        
        elif region == TouchRegion.AVATAR_BODY:
            if gesture == TouchGesture.PINCH:
                base_impact["passion"] += 0.5 * intensity
                base_impact["excitement"] += 0.4 * intensity
            elif gesture == TouchGesture.LONG_PRESS:
                base_impact["love"] += 0.4 * intensity
                base_impact["tenderness"] += 0.3 * intensity
        
        elif region == TouchRegion.BACKGROUND:
            if gesture == TouchGesture.SWIPE_UP:
                base_impact["excitement"] += 0.2 * intensity
            elif gesture == TouchGesture.SWIPE_DOWN:
                base_impact["tenderness"] += 0.2 * intensity
        
        return base_impact
    
    def _trigger_visual_effect(self, response: TouchResponse):
        """Trigger visual effect on mobile device"""
        
        effect_config = self.visual_effects.get(response.visual_effect, {})
        persona_modifiers = effect_config.get("persona_modifiers", {}).get(self.current_persona, {})
        
        # Calculate effect parameters
        duration = effect_config.get("duration", 2.0)
        base_intensity = response.intensity * effect_config.get("intensity_range", (0.5, 1.0))[1]
        
        # Apply persona modifiers
        final_intensity = base_intensity
        for modifier, value in persona_modifiers.items():
            if "intensity" in modifier.lower():
                final_intensity *= value
        
        # Create effect data
        effect_data = {
            "type": response.visual_effect.value,
            "intensity": final_intensity,
            "duration": duration,
            "persona": self.current_persona,
            "mood": self.current_mood,
            "coordinates": response.coordinates if hasattr(response, 'coordinates') else (0.5, 0.5),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add effect-specific data
        if response.visual_effect == VisualEffect.SPARKLE:
            effect_data["particle_count"] = effect_config.get("particle_count", (10, 30))[1]
            effect_data["colors"] = effect_config.get("color_schemes", {}).get(self.current_persona, ["white"])
        
        elif response.visual_effect == VisualEffect.GLOW:
            effect_data["color_variant"] = effect_config.get("color_variants", ["warm"])[0]
        
        # Store active effect
        effect_id = f"{response.visual_effect.value}_{int(time.time() * 1000)}"
        self.active_effects[effect_id] = {
            "data": effect_data,
            "start_time": datetime.now(),
            "duration": duration
        }
        
        # Send to mobile device
        self._send_to_mobile_device(effect_data)
    
    def _send_to_mobile_device(self, effect_data: Dict):
        """Send visual effect data to mobile device"""
        # This would integrate with your mobile app's visual system
        # For now, just print the effect data
        print(f"[Mobile Visual Layer] Effect: {effect_data}")
    
    def _log_touch_interaction(self, response: TouchResponse, coordinates: Tuple[float, float]):
        """Log touch interaction for analysis"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "gesture": response.gesture.value,
            "region": response.region.value,
            "coordinates": coordinates,
            "intensity": response.intensity,
            "mood": self.current_mood,
            "persona": self.current_persona,
            "mood_impact": response.mood_impact
        }
        
        self.touch_history.append(log_entry)
        
        # Keep only last 100 interactions
        if len(self.touch_history) > 100:
            self.touch_history = self.touch_history[-100:]
    
    def _update_active_effects(self):
        """Update active visual effects"""
        current_time = datetime.now()
        
        for effect_id, effect_info in self.active_effects.items():
            elapsed = (current_time - effect_info["start_time"]).total_seconds()
            duration = effect_info["duration"]
            
            if elapsed < duration:
                # Calculate progress
                progress = elapsed / duration
                
                # Update effect based on progress
                self._update_effect_progress(effect_id, effect_info["data"], progress)
    
    def _update_effect_progress(self, effect_id: str, effect_data: Dict, progress: float):
        """Update visual effect progress"""
        
        # Calculate current intensity based on progress
        if progress < 0.5:
            # Fade in
            current_intensity = effect_data["intensity"] * (progress * 2)
        else:
            # Fade out
            current_intensity = effect_data["intensity"] * (2 - progress * 2)
        
        # Update effect data
        updated_data = effect_data.copy()
        updated_data["current_intensity"] = current_intensity
        updated_data["progress"] = progress
        
        # Send updated effect to mobile device
        self._send_to_mobile_device(updated_data)
    
    def _cleanup_expired_effects(self):
        """Remove expired visual effects"""
        current_time = datetime.now()
        expired_effects = []
        
        for effect_id, effect_info in self.active_effects.items():
            elapsed = (current_time - effect_info["start_time"]).total_seconds()
            if elapsed >= effect_info["duration"]:
                expired_effects.append(effect_id)
        
        for effect_id in expired_effects:
            del self.active_effects[effect_id]
    
    def update_mood(self, new_mood: str):
        """Update current mood"""
        self.current_mood = new_mood
        print(f"[Mobile Visual Layer] Mood updated to: {new_mood}")
    
    def update_persona(self, new_persona: str):
        """Update current persona"""
        self.current_persona = new_persona
        print(f"[Mobile Visual Layer] Persona updated to: {new_persona}")
    
    def get_touch_statistics(self) -> Dict:
        """Get touch interaction statistics"""
        if not self.touch_history:
            return {}
        
        total_interactions = len(self.touch_history)
        recent_interactions = self.touch_history[-10:] if len(self.touch_history) >= 10 else self.touch_history
        
        # Calculate average intensity
        avg_intensity = sum(interaction["intensity"] for interaction in recent_interactions) / len(recent_interactions)
        
        # Most common gestures
        gesture_counts = {}
        for interaction in recent_interactions:
            gesture = interaction["gesture"]
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
        
        most_common_gesture = max(gesture_counts.items(), key=lambda x: x[1])[0] if gesture_counts else None
        
        return {
            "total_interactions": total_interactions,
            "recent_interactions": len(recent_interactions),
            "average_intensity": avg_intensity,
            "most_common_gesture": most_common_gesture,
            "current_mood": self.current_mood,
            "current_persona": self.current_persona
        }
    
    def stop_visual_layer(self):
        """Stop the visual layer"""
        self.is_running = False
        self.active_effects.clear()
        print("[Mobile Visual Layer] Stopped")

# Global instance
mobile_visual_layer = MobileVisualLayer() 