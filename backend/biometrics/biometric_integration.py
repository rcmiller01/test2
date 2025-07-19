# biometric_integration.py
# Biometric Integration system for heartbeat, motion, and other biometric data

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import random
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BiometricType(Enum):
    HEART_RATE = "heart_rate"
    HEART_RATE_VARIABILITY = "hrv"
    MOTION = "motion"
    BREATHING_RATE = "breathing_rate"
    SKIN_CONDUCTANCE = "skin_conductance"
    TEMPERATURE = "temperature"
    BLOOD_PRESSURE = "blood_pressure"
    OXYGEN_SATURATION = "oxygen_saturation"

class MotionType(Enum):
    STILL = "still"
    WALKING = "walking"
    RUNNING = "running"
    SLEEPING = "sleeping"
    EXERCISING = "exercising"
    SITTING = "sitting"
    STANDING = "standing"
    GESTURING = "gesturing"

class EmotionalState(Enum):
    CALM = "calm"
    EXCITED = "excited"
    STRESSED = "stressed"
    RELAXED = "relaxed"
    ANXIOUS = "anxious"
    FOCUSED = "focused"
    TIRED = "tired"
    ENERGETIC = "energetic"

@dataclass
class BiometricReading:
    biometric_type: BiometricType
    value: float
    unit: str
    timestamp: datetime
    quality: float  # 0.0 to 1.0
    context: Dict[str, Any]

@dataclass
class MotionData:
    motion_type: MotionType
    intensity: float  # 0.0 to 1.0
    duration_seconds: float
    timestamp: datetime
    location: Optional[str] = None
    context: Dict[str, Any] = None

@dataclass
class EmotionalBiometricState:
    user_id: str
    timestamp: datetime
    heart_rate: Optional[float] = None
    hrv: Optional[float] = None
    breathing_rate: Optional[float] = None
    skin_conductance: Optional[float] = None
    temperature: Optional[float] = None
    motion_type: Optional[MotionType] = None
    motion_intensity: Optional[float] = None
    emotional_state: Optional[EmotionalState] = None
    confidence: float = 0.0
    context: Dict[str, Any] = None

class BiometricIntegrationEngine:
    """Biometric Integration engine for processing health and motion data"""
    
    def __init__(self):
        self.biometric_history = []
        self.motion_history = []
        self.emotional_states = []
        self.biometric_ranges = self._initialize_biometric_ranges()
        self.emotional_mappings = self._initialize_emotional_mappings()
        self.motion_patterns = self._initialize_motion_patterns()
        self.active_sessions = {}
        
    def _initialize_biometric_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Initialize normal ranges for different biometrics"""
        return {
            "heart_rate": {
                "normal_min": 60,
                "normal_max": 100,
                "resting_min": 40,
                "resting_max": 80,
                "exercise_min": 100,
                "exercise_max": 180,
                "unit": "bpm",
                "emotional_sensitivity": 0.8
            },
            "hrv": {
                "normal_min": 20,
                "normal_max": 100,
                "high_stress_max": 30,
                "low_stress_min": 50,
                "unit": "ms",
                "emotional_sensitivity": 0.9
            },
            "breathing_rate": {
                "normal_min": 12,
                "normal_max": 20,
                "resting_min": 8,
                "resting_max": 16,
                "exercise_min": 20,
                "exercise_max": 40,
                "unit": "breaths/min",
                "emotional_sensitivity": 0.7
            },
            "skin_conductance": {
                "normal_min": 1.0,
                "normal_max": 20.0,
                "stress_threshold": 15.0,
                "unit": "μS",
                "emotional_sensitivity": 0.8
            },
            "temperature": {
                "normal_min": 36.5,
                "normal_max": 37.5,
                "fever_threshold": 38.0,
                "unit": "°C",
                "emotional_sensitivity": 0.4
            },
            "blood_pressure": {
                "systolic_normal_min": 90,
                "systolic_normal_max": 140,
                "diastolic_normal_min": 60,
                "diastolic_normal_max": 90,
                "unit": "mmHg",
                "emotional_sensitivity": 0.6
            },
            "oxygen_saturation": {
                "normal_min": 95,
                "normal_max": 100,
                "concern_threshold": 92,
                "unit": "%",
                "emotional_sensitivity": 0.3
            }
        }
    
    def _initialize_emotional_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize emotional state mappings from biometric patterns"""
        return {
            "calm": {
                "state": EmotionalState.CALM,
                "heart_rate_range": (60, 80),
                "hrv_range": (50, 100),
                "breathing_range": (12, 16),
                "motion_intensity": (0.0, 0.2),
                "confidence_threshold": 0.7,
                "persona_modifications": {"serenity": 0.8, "peace": 0.7}
            },
            "excited": {
                "state": EmotionalState.EXCITED,
                "heart_rate_range": (80, 120),
                "hrv_range": (20, 50),
                "breathing_range": (16, 25),
                "motion_intensity": (0.4, 0.8),
                "confidence_threshold": 0.7,
                "persona_modifications": {"energy": 0.8, "enthusiasm": 0.7}
            },
            "stressed": {
                "state": EmotionalState.STRESSED,
                "heart_rate_range": (80, 110),
                "hrv_range": (15, 35),
                "breathing_range": (18, 25),
                "motion_intensity": (0.1, 0.4),
                "confidence_threshold": 0.7,
                "persona_modifications": {"concern": 0.8, "support": 0.9}
            },
            "relaxed": {
                "state": EmotionalState.RELAXED,
                "heart_rate_range": (55, 75),
                "hrv_range": (60, 100),
                "breathing_range": (10, 14),
                "motion_intensity": (0.0, 0.1),
                "confidence_threshold": 0.7,
                "persona_modifications": {"gentleness": 0.8, "comfort": 0.7}
            },
            "anxious": {
                "state": EmotionalState.ANXIOUS,
                "heart_rate_range": (85, 115),
                "hrv_range": (10, 30),
                "breathing_range": (20, 30),
                "motion_intensity": (0.2, 0.5),
                "confidence_threshold": 0.7,
                "persona_modifications": {"reassurance": 0.9, "calmness": 0.8}
            },
            "focused": {
                "state": EmotionalState.FOCUSED,
                "heart_rate_range": (70, 90),
                "hrv_range": (40, 70),
                "breathing_range": (14, 18),
                "motion_intensity": (0.0, 0.3),
                "confidence_threshold": 0.7,
                "persona_modifications": {"attention": 0.8, "clarity": 0.7}
            },
            "tired": {
                "state": EmotionalState.TIRED,
                "heart_rate_range": (50, 70),
                "hrv_range": (30, 60),
                "breathing_range": (10, 15),
                "motion_intensity": (0.0, 0.2),
                "confidence_threshold": 0.7,
                "persona_modifications": {"gentleness": 0.9, "care": 0.8}
            },
            "energetic": {
                "state": EmotionalState.ENERGETIC,
                "heart_rate_range": (75, 100),
                "hrv_range": (45, 80),
                "breathing_range": (15, 20),
                "motion_intensity": (0.3, 0.7),
                "confidence_threshold": 0.7,
                "persona_modifications": {"vitality": 0.8, "joy": 0.7}
            }
        }
    
    def _initialize_motion_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize motion patterns and their emotional implications"""
        return {
            "still": {
                "motion_type": MotionType.STILL,
                "intensity_range": (0.0, 0.1),
                "emotional_implications": ["calm", "focused", "tired", "relaxed"],
                "persona_modifications": {"stillness": 0.8, "patience": 0.7}
            },
            "walking": {
                "motion_type": MotionType.WALKING,
                "intensity_range": (0.2, 0.4),
                "emotional_implications": ["calm", "energetic", "focused"],
                "persona_modifications": {"movement": 0.6, "flow": 0.7}
            },
            "running": {
                "motion_type": MotionType.RUNNING,
                "intensity_range": (0.7, 1.0),
                "emotional_implications": ["excited", "energetic", "stressed"],
                "persona_modifications": {"energy": 0.9, "intensity": 0.8}
            },
            "sleeping": {
                "motion_type": MotionType.SLEEPING,
                "intensity_range": (0.0, 0.05),
                "emotional_implications": ["tired", "relaxed", "calm"],
                "persona_modifications": {"gentleness": 0.9, "quiet": 0.8}
            },
            "exercising": {
                "motion_type": MotionType.EXERCISING,
                "intensity_range": (0.5, 0.9),
                "emotional_implications": ["energetic", "excited", "focused"],
                "persona_modifications": {"motivation": 0.8, "strength": 0.7}
            },
            "sitting": {
                "motion_type": MotionType.SITTING,
                "intensity_range": (0.0, 0.2),
                "emotional_implications": ["calm", "focused", "relaxed"],
                "persona_modifications": {"comfort": 0.7, "stability": 0.6}
            },
            "standing": {
                "motion_type": MotionType.STANDING,
                "intensity_range": (0.1, 0.3),
                "emotional_implications": ["focused", "energetic", "calm"],
                "persona_modifications": {"presence": 0.7, "awareness": 0.6}
            },
            "gesturing": {
                "motion_type": MotionType.GESTURING,
                "intensity_range": (0.3, 0.6),
                "emotional_implications": ["excited", "energetic", "focused"],
                "persona_modifications": {"expressiveness": 0.8, "engagement": 0.7}
            }
        }
    
    async def process_biometric_data(self, user_id: str, biometric_readings: List[BiometricReading],
                                   motion_data: Optional[MotionData] = None) -> Optional[EmotionalBiometricState]:
        """Process biometric data and determine emotional state"""
        try:
            # Store biometric readings
            for reading in biometric_readings:
                self.biometric_history.append({
                    "user_id": user_id,
                    "reading": reading,
                    "timestamp": reading.timestamp
                })
            
            # Store motion data if provided
            if motion_data:
                self.motion_history.append({
                    "user_id": user_id,
                    "motion": motion_data,
                    "timestamp": motion_data.timestamp
                })
            
            # Analyze biometric patterns
            biometric_analysis = await self._analyze_biometric_patterns(biometric_readings)
            
            # Analyze motion patterns
            motion_analysis = await self._analyze_motion_patterns(motion_data) if motion_data else {}
            
            # Determine emotional state
            emotional_state = await self._determine_emotional_state(biometric_analysis, motion_analysis)
            
            # Create emotional biometric state
            emotional_biometric = EmotionalBiometricState(
                user_id=user_id,
                timestamp=datetime.now(),
                heart_rate=biometric_analysis.get("heart_rate"),
                hrv=biometric_analysis.get("hrv"),
                breathing_rate=biometric_analysis.get("breathing_rate"),
                skin_conductance=biometric_analysis.get("skin_conductance"),
                temperature=biometric_analysis.get("temperature"),
                motion_type=motion_analysis.get("motion_type"),
                motion_intensity=motion_analysis.get("motion_intensity"),
                emotional_state=emotional_state["state"],
                confidence=emotional_state["confidence"],
                context={
                    "biometric_analysis": biometric_analysis,
                    "motion_analysis": motion_analysis,
                    "emotional_analysis": emotional_state
                }
            )
            
            # Store emotional state
            self.emotional_states.append(emotional_biometric)
            
            # Create memory entry
            await self._create_biometric_memory(emotional_biometric)
            
            logger.info(f"Processed biometric data for user {user_id}: {emotional_state['state'].value}")
            return emotional_biometric
            
        except Exception as e:
            logger.error(f"Error processing biometric data: {e}")
            return None
    
    async def _analyze_biometric_patterns(self, readings: List[BiometricReading]) -> Dict[str, Any]:
        """Analyze biometric patterns and extract meaningful data"""
        try:
            analysis = {}
            
            for reading in readings:
                biometric_type = reading.biometric_type.value
                value = reading.value
                quality = reading.quality
                
                # Only use high-quality readings
                if quality < 0.7:
                    continue
                
                # Store the reading
                analysis[biometric_type] = {
                    "value": value,
                    "quality": quality,
                    "unit": reading.unit,
                    "timestamp": reading.timestamp.isoformat()
                }
                
                # Check if value is within normal ranges
                ranges = self.biometric_ranges.get(biometric_type, {})
                if ranges:
                    normal_min = ranges.get("normal_min")
                    normal_max = ranges.get("normal_max")
                    
                    if normal_min is not None and normal_max is not None:
                        is_normal = normal_min <= value <= normal_max
                        analysis[biometric_type]["is_normal"] = is_normal
                        analysis[biometric_type]["normal_range"] = (normal_min, normal_max)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing biometric patterns: {e}")
            return {}
    
    async def _analyze_motion_patterns(self, motion_data: MotionData) -> Dict[str, Any]:
        """Analyze motion patterns and extract meaningful data"""
        try:
            if not motion_data:
                return {}
            
            analysis = {
                "motion_type": motion_data.motion_type.value,
                "intensity": motion_data.intensity,
                "duration_seconds": motion_data.duration_seconds,
                "timestamp": motion_data.timestamp.isoformat()
            }
            
            # Get motion pattern data
            pattern_data = self.motion_patterns.get(motion_data.motion_type.value, {})
            if pattern_data:
                intensity_range = pattern_data.get("intensity_range", (0.0, 1.0))
                emotional_implications = pattern_data.get("emotional_implications", [])
                
                analysis["intensity_range"] = intensity_range
                analysis["emotional_implications"] = emotional_implications
                analysis["persona_modifications"] = pattern_data.get("persona_modifications", {})
                
                # Check if intensity is within expected range
                min_intensity, max_intensity = intensity_range
                is_expected_intensity = min_intensity <= motion_data.intensity <= max_intensity
                analysis["is_expected_intensity"] = is_expected_intensity
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing motion patterns: {e}")
            return {}
    
    async def _determine_emotional_state(self, biometric_analysis: Dict[str, Any], 
                                       motion_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine emotional state based on biometric and motion analysis"""
        try:
            best_match = None
            best_confidence = 0.0
            
            for emotion_name, emotion_data in self.emotional_mappings.items():
                confidence = 0.0
                matches = 0
                total_checks = 0
                
                # Check heart rate
                if "heart_rate" in biometric_analysis:
                    hr_value = biometric_analysis["heart_rate"]["value"]
                    hr_range = emotion_data["heart_rate_range"]
                    if hr_range[0] <= hr_value <= hr_range[1]:
                        matches += 1
                    total_checks += 1
                
                # Check HRV
                if "hrv" in biometric_analysis:
                    hrv_value = biometric_analysis["hrv"]["value"]
                    hrv_range = emotion_data["hrv_range"]
                    if hrv_range[0] <= hrv_value <= hrv_range[1]:
                        matches += 1
                    total_checks += 1
                
                # Check breathing rate
                if "breathing_rate" in biometric_analysis:
                    br_value = biometric_analysis["breathing_rate"]["value"]
                    br_range = emotion_data["breathing_rate"]
                    if br_range[0] <= br_value <= br_range[1]:
                        matches += 1
                    total_checks += 1
                
                # Check motion intensity
                if "motion_intensity" in motion_analysis:
                    motion_intensity = motion_analysis["intensity"]
                    motion_range = emotion_data["motion_intensity"]
                    if motion_range[0] <= motion_intensity <= motion_range[1]:
                        matches += 1
                    total_checks += 1
                
                # Calculate confidence
                if total_checks > 0:
                    confidence = matches / total_checks
                    
                    # Apply quality weighting
                    quality_multiplier = 1.0
                    for biometric_type, data in biometric_analysis.items():
                        if "quality" in data:
                            quality_multiplier *= data["quality"]
                    
                    confidence *= quality_multiplier
                    
                    if confidence > best_confidence and confidence >= emotion_data["confidence_threshold"]:
                        best_confidence = confidence
                        best_match = emotion_data
            
            if best_match:
                return {
                    "state": best_match["state"],
                    "confidence": best_confidence,
                    "persona_modifications": best_match["persona_modifications"]
                }
            else:
                # Default to calm if no good match
                return {
                    "state": EmotionalState.CALM,
                    "confidence": 0.5,
                    "persona_modifications": {"neutral": 0.5}
                }
                
        except Exception as e:
            logger.error(f"Error determining emotional state: {e}")
            return {
                "state": EmotionalState.CALM,
                "confidence": 0.0,
                "persona_modifications": {"neutral": 0.5}
            }
    
    async def _create_biometric_memory(self, emotional_biometric: EmotionalBiometricState):
        """Create a memory entry in MongoDB for biometric data"""
        try:
            from database.mongodb_client import mongodb_client
            
            memory_data = {
                "user_id": emotional_biometric.user_id,
                "title": f"Biometric State: {emotional_biometric.emotional_state.value.title()}",
                "content": f"Emotional state determined from biometric data with {emotional_biometric.confidence:.2f} confidence",
                "memory_type": "biometric_state",
                "emotional_tags": [emotional_biometric.emotional_state.value],
                "tags": ["biometric", "health", "emotion", "motion"],
                "trust_level": 0.8,  # Biometric data is typically trustworthy
                "importance": 0.6,
                "context": {
                    "heart_rate": emotional_biometric.heart_rate,
                    "hrv": emotional_biometric.hrv,
                    "breathing_rate": emotional_biometric.breathing_rate,
                    "motion_type": emotional_biometric.motion_type.value if emotional_biometric.motion_type else None,
                    "motion_intensity": emotional_biometric.motion_intensity,
                    "confidence": emotional_biometric.confidence,
                    "biometric_analysis": emotional_biometric.context.get("biometric_analysis", {}),
                    "motion_analysis": emotional_biometric.context.get("motion_analysis", {})
                },
                "metadata": {
                    "source": "biometric_integration",
                    "created_at": emotional_biometric.timestamp.isoformat(),
                    "data_quality": "high"
                }
            }
            
            memory_id = await mongodb_client.store_memory(memory_data)
            logger.info(f"Created biometric memory: {memory_id}")
            
        except Exception as e:
            logger.error(f"Error creating biometric memory: {e}")
    
    async def get_user_biometric_history(self, user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get biometric history for a user"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            user_history = []
            
            # Get emotional states
            for state in self.emotional_states:
                if state.user_id == user_id and state.timestamp >= cutoff_time:
                    user_history.append({
                        "type": "emotional_state",
                        "timestamp": state.timestamp.isoformat(),
                        "emotional_state": state.emotional_state.value,
                        "confidence": state.confidence,
                        "heart_rate": state.heart_rate,
                        "hrv": state.hrv,
                        "motion_type": state.motion_type.value if state.motion_type else None,
                        "motion_intensity": state.motion_intensity
                    })
            
            # Get biometric readings
            for entry in self.biometric_history:
                if entry["user_id"] == user_id and entry["timestamp"] >= cutoff_time:
                    reading = entry["reading"]
                    user_history.append({
                        "type": "biometric_reading",
                        "timestamp": entry["timestamp"].isoformat(),
                        "biometric_type": reading.biometric_type.value,
                        "value": reading.value,
                        "unit": reading.unit,
                        "quality": reading.quality
                    })
            
            # Get motion data
            for entry in self.motion_history:
                if entry["user_id"] == user_id and entry["timestamp"] >= cutoff_time:
                    motion = entry["motion"]
                    user_history.append({
                        "type": "motion_data",
                        "timestamp": entry["timestamp"].isoformat(),
                        "motion_type": motion.motion_type.value,
                        "intensity": motion.intensity,
                        "duration_seconds": motion.duration_seconds
                    })
            
            # Sort by timestamp (newest first)
            user_history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return user_history
            
        except Exception as e:
            logger.error(f"Error getting biometric history: {e}")
            return []
    
    async def get_emotional_trends(self, user_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get emotional trends from biometric data"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_states = [
                state for state in self.emotional_states
                if state.user_id == user_id and state.timestamp >= cutoff_time
            ]
            
            if not recent_states:
                return {"message": "No recent biometric data available"}
            
            # Count emotional states
            emotion_counts = {}
            total_confidence = 0.0
            
            for state in recent_states:
                emotion = state.emotional_state.value
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                total_confidence += state.confidence
            
            # Find dominant emotion
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "unknown"
            
            # Calculate average confidence
            avg_confidence = total_confidence / len(recent_states) if recent_states else 0.0
            
            # Calculate trends
            trends = {
                "dominant_emotion": dominant_emotion,
                "emotion_distribution": emotion_counts,
                "average_confidence": avg_confidence,
                "total_readings": len(recent_states),
                "time_period_hours": hours
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting emotional trends: {e}")
            return {"error": str(e)}
    
    async def start_biometric_session(self, user_id: str, session_type: str = "continuous") -> str:
        """Start a biometric monitoring session"""
        try:
            session_id = f"biometric_session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "session_type": session_type,
                "started_at": datetime.now(),
                "status": "active",
                "readings_count": 0,
                "last_reading": None
            }
            
            self.active_sessions[session_id] = session_data
            
            logger.info(f"Started biometric session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting biometric session: {e}")
            return None
    
    async def end_biometric_session(self, session_id: str) -> bool:
        """End a biometric monitoring session"""
        try:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                session_data["status"] = "completed"
                session_data["ended_at"] = datetime.now()
                
                logger.info(f"Ended biometric session: {session_id}")
                return True
            else:
                logger.warning(f"Session {session_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error ending biometric session: {e}")
            return False

# Global biometric integration engine instance
biometric_integration_engine = BiometricIntegrationEngine() 