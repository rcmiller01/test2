# haptic_system.py
# Phase 3: Advanced haptic integration for physical connection simulation

import json
import time
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

class HapticPattern(Enum):
    HEARTBEAT = "heartbeat"
    BREATHING = "breathing"
    TOUCH = "touch"
    EMBRACE = "embrace"
    KISS = "kiss"
    STROKE = "stroke"
    PULSE = "pulse"
    WAVE = "wave"
    RHYTHM = "rhythm"
    INTIMATE = "intimate"

class HapticIntensity(Enum):
    SUBTLE = 0.2
    GENTLE = 0.4
    MODERATE = 0.6
    STRONG = 0.8
    INTENSE = 1.0

@dataclass
class HapticFeedback:
    pattern: HapticPattern
    intensity: HapticIntensity
    duration: float  # seconds
    location: str = "general"  # heart, hands, full_body, etc.
    emotional_context: str = "neutral"

class HapticSystem:
    def __init__(self):
        self.is_active = False
        self.current_pattern = None
        self.device_support = self._detect_haptic_devices()
        self.pattern_definitions = self._load_pattern_definitions()
        self.emotional_mappings = self._load_emotional_mappings()
        
    def _detect_haptic_devices(self) -> Dict[str, bool]:
        """Detect available haptic devices and capabilities"""
        devices = {
            "mobile_vibration": True,  # Most mobile devices
            "gamepad_rumble": False,   # Game controllers
            "haptic_gloves": False,    # VR haptic gloves
            "smart_watch": False,      # Apple Watch, etc.
            "haptic_vest": False,      # Haptic feedback vest
            "desktop_haptic": False    # Desktop haptic devices
        }
        
        # Try to detect specific devices
        try:
            # Check for WebHaptics API support
            if hasattr(navigator, 'vibrate'):
                devices["mobile_vibration"] = True
            
            # Check for gamepad support
            if hasattr(navigator, 'getGamepads'):
                devices["gamepad_rumble"] = True
                
        except:
            pass
            
        return devices
    
    def _load_pattern_definitions(self) -> Dict[HapticPattern, List[Tuple[float, float]]]:
        """Load haptic pattern definitions (timing, intensity)"""
        return {
            HapticPattern.HEARTBEAT: [
                (0.0, 0.8), (0.1, 0.0), (0.3, 0.8), (0.4, 0.0), (1.0, 0.0)
            ],
            HapticPattern.BREATHING: [
                (0.0, 0.3), (0.5, 0.6), (1.0, 0.3), (1.5, 0.1), (2.0, 0.0)
            ],
            HapticPattern.TOUCH: [
                (0.0, 0.5), (0.2, 0.0)
            ],
            HapticPattern.EMBRACE: [
                (0.0, 0.4), (0.5, 0.7), (1.0, 0.4), (1.5, 0.2), (2.0, 0.0)
            ],
            HapticPattern.KISS: [
                (0.0, 0.6), (0.1, 0.0), (0.3, 0.4), (0.4, 0.0)
            ],
            HapticPattern.STROKE: [
                (0.0, 0.3), (0.2, 0.5), (0.4, 0.3), (0.6, 0.5), (0.8, 0.3), (1.0, 0.0)
            ],
            HapticPattern.PULSE: [
                (0.0, 0.4), (0.1, 0.0), (0.2, 0.4), (0.3, 0.0), (0.4, 0.4), (0.5, 0.0)
            ],
            HapticPattern.WAVE: [
                (0.0, 0.2), (0.25, 0.6), (0.5, 0.2), (0.75, 0.6), (1.0, 0.2)
            ],
            HapticPattern.RHYTHM: [
                (0.0, 0.5), (0.25, 0.0), (0.5, 0.5), (0.75, 0.0), (1.0, 0.5)
            ],
            HapticPattern.INTIMATE: [
                (0.0, 0.3), (0.2, 0.7), (0.4, 0.3), (0.6, 0.8), (0.8, 0.3), (1.0, 0.0)
            ]
        }
    
    def _load_emotional_mappings(self) -> Dict[str, HapticPattern]:
        """Map emotions to haptic patterns"""
        return {
            "love": HapticPattern.HEARTBEAT,
            "passion": HapticPattern.PULSE,
            "tenderness": HapticPattern.STROKE,
            "security": HapticPattern.BREATHING,
            "excitement": HapticPattern.RHYTHM,
            "intimacy": HapticPattern.INTIMATE,
            "comfort": HapticPattern.EMBRACE,
            "affection": HapticPattern.TOUCH,
            "romance": HapticPattern.WAVE,
            "desire": HapticPattern.PULSE
        }
    
    def start_haptic_feedback(self, feedback: HapticFeedback):
        """Start haptic feedback pattern"""
        if not self.device_support["mobile_vibration"]:
            print("[Haptic] No haptic device support detected")
            return False
            
        self.is_active = True
        self.current_pattern = feedback
        
        # Start pattern in background thread
        threading.Thread(
            target=self._execute_pattern,
            args=(feedback,),
            daemon=True
        ).start()
        
        print(f"[Haptic] Started {feedback.pattern.value} pattern")
        return True
    
    def _execute_pattern(self, feedback: HapticFeedback):
        """Execute haptic pattern with timing"""
        pattern = self.pattern_definitions[feedback.pattern]
        intensity_multiplier = feedback.intensity.value
        
        for timing, base_intensity in pattern:
            if not self.is_active:
                break
                
            # Calculate actual intensity
            actual_intensity = base_intensity * intensity_multiplier
            
            # Apply haptic feedback
            self._apply_haptic(actual_intensity, feedback.location)
            
            # Wait for next timing
            time.sleep(timing)
    
    def _apply_haptic(self, intensity: float, location: str):
        """Apply haptic feedback to specific location"""
        try:
            # Convert intensity to vibration duration/pattern
            if location == "heart":
                # Heart area - stronger, rhythmic
                vibration_pattern = [int(intensity * 200), int(intensity * 100)]
            elif location == "hands":
                # Hands - gentle, precise
                vibration_pattern = [int(intensity * 100)]
            elif location == "full_body":
                # Full body - immersive
                vibration_pattern = [int(intensity * 300), int(intensity * 150)]
            else:
                # General - balanced
                vibration_pattern = [int(intensity * 150)]
            
            # Apply vibration if supported
            if hasattr(navigator, 'vibrate'):
                navigator.vibrate(vibration_pattern)
                
        except Exception as e:
            print(f"[Haptic] Error applying feedback: {e}")
    
    def stop_haptic_feedback(self):
        """Stop current haptic feedback"""
        self.is_active = False
        self.current_pattern = None
        print("[Haptic] Stopped haptic feedback")
    
    def trigger_emotional_haptic(self, emotion: str, intensity: HapticIntensity = HapticIntensity.MODERATE):
        """Trigger haptic feedback based on emotion"""
        if emotion in self.emotional_mappings:
            pattern = self.emotional_mappings[emotion]
            feedback = HapticFeedback(
                pattern=pattern,
                intensity=intensity,
                duration=2.0,
                emotional_context=emotion
            )
            return self.start_haptic_feedback(feedback)
        return False
    
    def trigger_romantic_haptic(self, action: str, intensity: HapticIntensity = HapticIntensity.MODERATE):
        """Trigger romantic haptic feedback"""
        romantic_patterns = {
            "kiss": HapticPattern.KISS,
            "hug": HapticPattern.EMBRACE,
            "touch": HapticPattern.TOUCH,
            "stroke": HapticPattern.STROKE,
            "heartbeat": HapticPattern.HEARTBEAT,
            "breathing": HapticPattern.BREATHING
        }
        
        if action in romantic_patterns:
            feedback = HapticFeedback(
                pattern=romantic_patterns[action],
                intensity=intensity,
                duration=3.0,
                location="heart" if action in ["kiss", "heartbeat"] else "general",
                emotional_context="romantic"
            )
            return self.start_haptic_feedback(feedback)
        return False
    
    def get_haptic_status(self) -> Dict:
        """Get current haptic system status"""
        return {
            "active": self.is_active,
            "current_pattern": self.current_pattern.pattern.value if self.current_pattern else None,
            "device_support": self.device_support,
            "available_patterns": [p.value for p in HapticPattern],
            "emotional_mappings": {k: v.value for k, v in self.emotional_mappings.items()}
        }

# Global haptic system instance
haptic_system = HapticSystem()

def get_haptic_system() -> HapticSystem:
    """Get the global haptic system instance"""
    return haptic_system

def trigger_haptic_feedback(pattern: str, intensity: str = "moderate", duration: float = 2.0):
    """Convenience function to trigger haptic feedback"""
    try:
        haptic_pattern = HapticPattern(pattern)
        haptic_intensity = HapticIntensity(intensity.upper())
        
        feedback = HapticFeedback(
            pattern=haptic_pattern,
            intensity=haptic_intensity,
            duration=duration
        )
        
        return haptic_system.start_haptic_feedback(feedback)
    except Exception as e:
        print(f"[Haptic] Error triggering feedback: {e}")
        return False 