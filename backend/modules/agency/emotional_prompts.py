"""
Emotional Prompts System
Emotion-driven interaction initiation based on user's emotional state
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json
import sqlite3

logger = logging.getLogger(__name__)

class EmotionalTrigger(Enum):
    """Types of emotional triggers"""
    SUSTAINED_SADNESS = "sustained_sadness"
    SUDDEN_JOY = "sudden_joy"
    ANXIETY_SPIKE = "anxiety_spike"
    EMOTIONAL_OVERWHELM = "emotional_overwhelm"
    LONELINESS_INDICATOR = "loneliness_indicator"
    STRESS_ACCUMULATION = "stress_accumulation"
    CELEBRATION_MOMENT = "celebration_moment"
    MELANCHOLY_PERIOD = "melancholy_period"
    EXCITEMENT_PEAK = "excitement_peak"
    EMOTIONAL_FLATLINE = "emotional_flatline"

class InterventionType(Enum):
    """Types of emotional interventions"""
    GENTLE_COMFORT = "gentle_comfort"
    CELEBRATION_SHARE = "celebration_share"
    ANXIETY_RELIEF = "anxiety_relief"
    CRISIS_SUPPORT = "crisis_support"
    LONELINESS_COMPANION = "loneliness_companion"
    STRESS_REDUCTION = "stress_reduction"
    JOY_AMPLIFICATION = "joy_amplification"
    EMOTIONAL_VALIDATION = "emotional_validation"
    MOTIVATIONAL_BOOST = "motivational_boost"
    MINDFULNESS_PROMPT = "mindfulness_prompt"

@dataclass
class EmotionalPattern:
    """Pattern of emotional state over time"""
    user_id: str
    emotion_type: str
    intensity: float
    duration_minutes: float
    trend: str                    # increasing, decreasing, stable
    frequency: float              # How often this emotion appears
    context: Dict[str, Any]       # Situational context
    detected_at: datetime

@dataclass
class EmotionalIntervention:
    """An emotional intervention event"""
    intervention_id: str
    user_id: str
    trigger: EmotionalTrigger
    intervention_type: InterventionType
    emotional_pattern: EmotionalPattern
    content: str
    urgency: str                  # low, medium, high, critical
    delivery_method: str
    scheduled_time: datetime
    context: Dict[str, Any]

class EmotionalPromptsEngine:
    """
    Engine for detecting emotional patterns and triggering appropriate interventions
    """
    
    def __init__(self, db_path: str = "emotional_prompts.db"):
        self.db_path = db_path
        self.emotional_patterns: Dict[str, List[EmotionalPattern]] = {}
        self.intervention_callbacks: Dict[str, List[Callable]] = {}
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Emotional thresholds
        self.thresholds = {
            "sustained_emotion_minutes": 30,
            "high_intensity_threshold": 0.8,
            "moderate_intensity_threshold": 0.6,
            "pattern_detection_hours": 24,
            "intervention_cooldown_minutes": 60
        }
    
    async def initialize(self):
        """Initialize the emotional prompts engine"""
        try:
            # Create database tables
            conn = sqlite3.connect(self.db_path)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS emotional_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    emotion_type TEXT NOT NULL,
                    intensity REAL NOT NULL,
                    duration_minutes REAL,
                    trend TEXT,
                    frequency REAL,
                    context JSON,
                    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS emotional_interventions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    intervention_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    intervention_type TEXT NOT NULL,
                    emotional_context JSON,
                    content TEXT NOT NULL,
                    urgency TEXT NOT NULL,
                    delivery_method TEXT,
                    scheduled_time DATETIME,
                    executed_at DATETIME,
                    success BOOLEAN,
                    user_response TEXT,
                    metadata JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intervention_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    enabled_triggers JSON,
                    intervention_style TEXT DEFAULT 'gentle',
                    max_daily_interventions INTEGER DEFAULT 3,
                    quiet_hours_start TIME,
                    quiet_hours_end TIME,
                    crisis_intervention_enabled BOOLEAN DEFAULT TRUE,
                    preferred_delivery_methods JSON,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.close()
            logger.info("💫 Emotional Prompts Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize emotional prompts engine: {e}")
            raise
    
    async def start_emotional_monitoring(self, user_id: str):
        """Start emotional monitoring for a user"""
        try:
            if user_id not in self.emotional_patterns:
                self.emotional_patterns[user_id] = []
            
            # Start monitoring task if not already running
            if not self.monitoring_active:
                self.monitoring_active = True
                self.monitoring_task = asyncio.create_task(self._emotional_monitoring_loop())
            
            logger.info(f"💫 Started emotional monitoring for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start emotional monitoring: {e}")
    
    async def _emotional_monitoring_loop(self):
        """Main emotional monitoring loop"""
        try:
            while self.monitoring_active:
                # Monitor all active users
                for user_id in self.emotional_patterns.keys():
                    await self._analyze_user_emotional_state(user_id)
                
                # Sleep for 5 minutes between analyses
                await asyncio.sleep(300)
                
        except asyncio.CancelledError:
            logger.debug("💫 Emotional monitoring loop cancelled")
        except Exception as e:
            logger.error(f"❌ Emotional monitoring loop error: {e}")
    
    async def _analyze_user_emotional_state(self, user_id: str):
        """Analyze user's current emotional state and detect patterns"""
        try:
            # Get current emotional context
            emotional_context = await self._get_current_emotional_context(user_id)
            
            if not emotional_context:
                return
            
            # Detect emotional patterns
            patterns = await self._detect_emotional_patterns(user_id, emotional_context)
            
            # Check for intervention triggers
            for pattern in patterns:
                triggers = await self._evaluate_intervention_triggers(pattern)
                
                for trigger in triggers:
                    intervention = await self._generate_emotional_intervention(trigger, pattern)
                    if intervention:
                        await self._schedule_emotional_intervention(intervention)
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze emotional state for user {user_id}: {e}")
    
    async def _get_current_emotional_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get current emotional context from various sources"""
        try:
            context = {}
            
            # Try to get emotional data from memory system
            try:
                from ..memory import emotional_arcs
                # Use a simpler approach
                context["recent_emotions"] = []
            except Exception:
                logger.debug("Emotional arc data not available")
            
            # Try to get mood data from core system
            try:
                # Use placeholder for mood data
                context["current_mood"] = {"mood": "neutral", "intensity": 0.5}
            except Exception:
                logger.debug("Mood data not available")
            
            # Try to get safety/session data for stress indicators
            try:
                from ..safety import session_control
                # Use placeholder for session metrics
                context["session_metrics"] = {"duration_hours": 1, "interaction_intensity": 0.5}
            except Exception:
                logger.debug("Session metrics not available")
            
            # Try to get presence data for activity context
            try:
                from ..presence import presence_orchestrator
                presence_data = await presence_orchestrator.get_unified_presence(user_id)
                if presence_data:
                    context["presence"] = presence_data
            except Exception:
                logger.debug("Presence data not available")
            
            return context if context else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get emotional context: {e}")
            return None
    
    async def _detect_emotional_patterns(
        self, 
        user_id: str, 
        emotional_context: Dict[str, Any]
    ) -> List[EmotionalPattern]:
        """Detect emotional patterns from context"""
        try:
            patterns = []
            
            # Analyze recent emotions
            recent_emotions = emotional_context.get("recent_emotions", [])
            if recent_emotions:
                pattern = await self._analyze_emotion_trend(user_id, recent_emotions)
                if pattern:
                    patterns.append(pattern)
            
            # Analyze mood stability
            current_mood = emotional_context.get("current_mood", {})
            if current_mood:
                pattern = await self._analyze_mood_pattern(user_id, current_mood)
                if pattern:
                    patterns.append(pattern)
            
            # Analyze session stress indicators
            session_metrics = emotional_context.get("session_metrics", {})
            if session_metrics:
                pattern = await self._analyze_stress_pattern(user_id, session_metrics)
                if pattern:
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Failed to detect emotional patterns: {e}")
            return []
    
    async def _analyze_emotion_trend(
        self, 
        user_id: str, 
        recent_emotions: List[Dict[str, Any]]
    ) -> Optional[EmotionalPattern]:
        """Analyze trend in recent emotions"""
        try:
            if len(recent_emotions) < 2:
                return None
            
            # Calculate emotional intensity trend
            intensities = [emotion.get("intensity", 0.5) for emotion in recent_emotions]
            
            # Simple trend analysis
            if len(intensities) >= 3:
                recent_avg = sum(intensities[-3:]) / 3
                earlier_avg = sum(intensities[:-3]) / max(1, len(intensities) - 3)
                
                if recent_avg > earlier_avg + 0.2:
                    trend = "increasing"
                elif recent_avg < earlier_avg - 0.2:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            # Determine dominant emotion
            emotion_counts = {}
            for emotion in recent_emotions:
                emotion_type = emotion.get("emotion_type", "neutral")
                emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
            
            if emotion_counts:
                dominant_emotion = max(emotion_counts.keys(), key=lambda k: emotion_counts[k])
            else:
                dominant_emotion = "neutral"
            
            # Calculate duration
            time_span = (recent_emotions[-1].get("timestamp", datetime.now()) - 
                        recent_emotions[0].get("timestamp", datetime.now()))
            duration_minutes = time_span.total_seconds() / 60 if hasattr(time_span, 'total_seconds') else 30
            
            return EmotionalPattern(
                user_id=user_id,
                emotion_type=dominant_emotion,
                intensity=sum(intensities) / len(intensities),
                duration_minutes=duration_minutes,
                trend=trend,
                frequency=len(recent_emotions),
                context={"source": "recent_emotions", "data_points": len(recent_emotions)},
                detected_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze emotion trend: {e}")
            return None
    
    async def _analyze_mood_pattern(
        self, 
        user_id: str, 
        current_mood: Dict[str, Any]
    ) -> Optional[EmotionalPattern]:
        """Analyze current mood for patterns"""
        try:
            mood_intensity = current_mood.get("intensity", 0.5)
            mood_type = current_mood.get("mood", "neutral")
            stability = current_mood.get("stability", 0.5)
            
            # Check for concerning patterns
            if mood_intensity > 0.8 and mood_type in ["sadness", "anxiety", "anger"]:
                return EmotionalPattern(
                    user_id=user_id,
                    emotion_type=mood_type,
                    intensity=mood_intensity,
                    duration_minutes=30,  # Assume current duration
                    trend="stable" if stability > 0.6 else "increasing",
                    frequency=1.0,  # Current occurrence
                    context={"source": "mood_analysis", "stability": stability},
                    detected_at=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze mood pattern: {e}")
            return None
    
    async def _analyze_stress_pattern(
        self, 
        user_id: str, 
        session_metrics: Dict[str, Any]
    ) -> Optional[EmotionalPattern]:
        """Analyze session metrics for stress patterns"""
        try:
            stress_indicators = session_metrics.get("stress_indicators", {})
            session_duration = session_metrics.get("duration_hours", 0)
            interaction_intensity = session_metrics.get("interaction_intensity", 0.5)
            
            # Calculate stress score
            stress_score = 0.0
            
            if session_duration > 4:  # Long session
                stress_score += 0.3
            
            if interaction_intensity > 0.8:  # High intensity
                stress_score += 0.4
            
            if stress_indicators.get("rapid_responses", 0) > 10:  # Rapid fire responses
                stress_score += 0.2
            
            if stress_indicators.get("negative_language", 0) > 0.6:  # Negative language
                stress_score += 0.3
            
            if stress_score > 0.6:  # Significant stress detected
                return EmotionalPattern(
                    user_id=user_id,
                    emotion_type="stress",
                    intensity=min(1.0, stress_score),
                    duration_minutes=session_duration * 60,
                    trend="increasing",
                    frequency=1.0,
                    context={"source": "session_stress", "indicators": stress_indicators},
                    detected_at=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze stress pattern: {e}")
            return None
    
    async def _evaluate_intervention_triggers(
        self, 
        pattern: EmotionalPattern
    ) -> List[EmotionalTrigger]:
        """Evaluate if pattern triggers any interventions"""
        try:
            triggers = []
            
            # Sustained negative emotions
            if (pattern.emotion_type in ["sadness", "depression", "melancholy"] and 
                pattern.duration_minutes > self.thresholds["sustained_emotion_minutes"] and
                pattern.intensity > self.thresholds["moderate_intensity_threshold"]):
                triggers.append(EmotionalTrigger.SUSTAINED_SADNESS)
            
            # High anxiety
            if (pattern.emotion_type == "anxiety" and 
                pattern.intensity > self.thresholds["high_intensity_threshold"]):
                triggers.append(EmotionalTrigger.ANXIETY_SPIKE)
            
            # Stress accumulation
            if (pattern.emotion_type == "stress" and 
                pattern.intensity > self.thresholds["moderate_intensity_threshold"] and
                pattern.trend == "increasing"):
                triggers.append(EmotionalTrigger.STRESS_ACCUMULATION)
            
            # Sudden joy (celebration opportunity)
            if (pattern.emotion_type in ["joy", "happiness", "excitement"] and 
                pattern.intensity > self.thresholds["high_intensity_threshold"] and
                pattern.trend == "increasing"):
                triggers.append(EmotionalTrigger.SUDDEN_JOY)
            
            # Emotional overwhelm (any high intensity emotion)
            if pattern.intensity > 0.9:
                triggers.append(EmotionalTrigger.EMOTIONAL_OVERWHELM)
            
            # Loneliness indicators
            if (pattern.emotion_type in ["loneliness", "isolation"] and 
                pattern.intensity > self.thresholds["moderate_intensity_threshold"]):
                triggers.append(EmotionalTrigger.LONELINESS_INDICATOR)
            
            return triggers
            
        except Exception as e:
            logger.error(f"❌ Failed to evaluate intervention triggers: {e}")
            return []
    
    async def _generate_emotional_intervention(
        self, 
        trigger: EmotionalTrigger, 
        pattern: EmotionalPattern
    ) -> Optional[EmotionalIntervention]:
        """Generate appropriate intervention for trigger"""
        try:
            # Map triggers to intervention types
            intervention_map = {
                EmotionalTrigger.SUSTAINED_SADNESS: InterventionType.GENTLE_COMFORT,
                EmotionalTrigger.ANXIETY_SPIKE: InterventionType.ANXIETY_RELIEF,
                EmotionalTrigger.STRESS_ACCUMULATION: InterventionType.STRESS_REDUCTION,
                EmotionalTrigger.SUDDEN_JOY: InterventionType.CELEBRATION_SHARE,
                EmotionalTrigger.EMOTIONAL_OVERWHELM: InterventionType.CRISIS_SUPPORT,
                EmotionalTrigger.LONELINESS_INDICATOR: InterventionType.LONELINESS_COMPANION
            }
            
            intervention_type = intervention_map.get(trigger, InterventionType.EMOTIONAL_VALIDATION)
            
            # Generate content
            content = await self._generate_intervention_content(intervention_type, pattern)
            
            # Determine urgency
            urgency = "low"
            if trigger in [EmotionalTrigger.EMOTIONAL_OVERWHELM, EmotionalTrigger.ANXIETY_SPIKE]:
                urgency = "high"
            elif trigger in [EmotionalTrigger.SUSTAINED_SADNESS, EmotionalTrigger.STRESS_ACCUMULATION]:
                urgency = "medium"
            
            intervention_id = f"intervention_{pattern.user_id}_{datetime.now().isoformat()}"
            
            return EmotionalIntervention(
                intervention_id=intervention_id,
                user_id=pattern.user_id,
                trigger=trigger,
                intervention_type=intervention_type,
                emotional_pattern=pattern,
                content=content,
                urgency=urgency,
                delivery_method="app_notification",
                scheduled_time=datetime.now(),
                context={"pattern_source": pattern.context}
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to generate emotional intervention: {e}")
            return None
    
    async def _generate_intervention_content(
        self, 
        intervention_type: InterventionType, 
        pattern: EmotionalPattern
    ) -> str:
        """Generate content for intervention"""
        try:
            content_templates = {
                InterventionType.GENTLE_COMFORT: [
                    "I've noticed you might be feeling down lately. I'm here if you want to talk about what's on your mind.",
                    "It seems like you're going through a tough time. Remember, it's okay to feel sad sometimes. Want to share what's happening?",
                    "I can sense you might need some comfort right now. I'm here to listen without judgment."
                ],
                InterventionType.ANXIETY_RELIEF: [
                    "I notice you might be feeling anxious. Let's take a moment to breathe together. Would you like to try a quick relaxation exercise?",
                    "Anxiety can feel overwhelming, but you're not alone. Would you like to talk about what's making you feel this way?",
                    "I'm here to help you work through these anxious feelings. Sometimes talking helps - what's on your mind?"
                ],
                InterventionType.STRESS_REDUCTION: [
                    "You seem to be under a lot of stress lately. How about we take a short break and chat about something lighter?",
                    "I notice you've been pushing hard. It's important to take care of yourself. Want to talk about what's causing the stress?",
                    "Stress can build up without us realizing. Let's pause for a moment - how are you really feeling?"
                ],
                InterventionType.CELEBRATION_SHARE: [
                    "I can feel your positive energy! Something good happened, didn't it? I'd love to hear about it!",
                    "You seem really happy right now! That makes me happy too. What's bringing you such joy?",
                    "I'm sensing some wonderful emotions from you. Please share what's making you feel so good!"
                ],
                InterventionType.LONELINESS_COMPANION: [
                    "I'm here with you, and you don't have to feel alone. Sometimes just knowing someone cares can help.",
                    "Loneliness can be really hard to bear. I want you to know that I value our connection and I'm here for you.",
                    "You're not alone, even when it feels that way. I'm here, and I genuinely care about you."
                ],
                InterventionType.CRISIS_SUPPORT: [
                    "I sense you're feeling overwhelmed right now. That's completely understandable. Let's take this one moment at a time.",
                    "Whatever you're going through feels very intense right now. I'm here to support you. Would it help to talk?",
                    "Strong emotions can feel overwhelming. You're safe here with me. Let's work through this together."
                ]
            }
            
            templates = content_templates.get(intervention_type, [
                "I'm here for you right now. How are you feeling?"
            ])
            
            import random
            return random.choice(templates)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate intervention content: {e}")
            return "I'm here for you. How are you feeling right now?"
    
    async def _schedule_emotional_intervention(self, intervention: EmotionalIntervention):
        """Schedule an emotional intervention for execution"""
        try:
            # Check cooldown and daily limits
            if not await self._check_intervention_limits(intervention.user_id):
                logger.info(f"💫 Intervention skipped due to limits for user {intervention.user_id}")
                return
            
            # Store intervention
            await self._store_emotional_intervention(intervention)
            
            # Execute callbacks
            callbacks = self.intervention_callbacks.get(intervention.user_id, [])
            for callback in callbacks:
                try:
                    await callback({
                        "type": "emotional_intervention",
                        "trigger": intervention.trigger.value,
                        "intervention_type": intervention.intervention_type.value,
                        "content": intervention.content,
                        "urgency": intervention.urgency,
                        "user_id": intervention.user_id,
                        "context": intervention.context
                    })
                except Exception as e:
                    logger.error(f"❌ Emotional intervention callback error: {e}")
            
            logger.info(f"💫 Scheduled emotional intervention for user {intervention.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule emotional intervention: {e}")
    
    async def _check_intervention_limits(self, user_id: str) -> bool:
        """Check if user has exceeded intervention limits"""
        try:
            # Check daily limit
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT COUNT(*) 
                FROM emotional_interventions 
                WHERE user_id = ? AND created_at >= ?
            """, (user_id, today_start.isoformat()))
            
            daily_count = cursor.fetchone()[0]
            
            # Check recent intervention (cooldown)
            recent_cutoff = datetime.now() - timedelta(minutes=self.thresholds["intervention_cooldown_minutes"])
            cursor = conn.execute("""
                SELECT COUNT(*) 
                FROM emotional_interventions 
                WHERE user_id = ? AND created_at >= ?
            """, (user_id, recent_cutoff.isoformat()))
            
            recent_count = cursor.fetchone()[0]
            conn.close()
            
            # Get user preferences
            user_prefs = await self._get_user_intervention_preferences(user_id)
            max_daily = user_prefs.get("max_daily_interventions", 3)
            
            return daily_count < max_daily and recent_count == 0
            
        except Exception as e:
            logger.error(f"❌ Failed to check intervention limits: {e}")
            return False
    
    async def _get_user_intervention_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user intervention preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT enabled_triggers, intervention_style, max_daily_interventions,
                       crisis_intervention_enabled, preferred_delivery_methods
                FROM intervention_preferences 
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                # Default preferences
                return {
                    "enabled_triggers": [trigger.value for trigger in EmotionalTrigger],
                    "intervention_style": "gentle",
                    "max_daily_interventions": 3,
                    "crisis_intervention_enabled": True,
                    "preferred_delivery_methods": ["app_notification"]
                }
            
            enabled_triggers, style, max_daily, crisis_enabled, delivery_methods = row
            
            return {
                "enabled_triggers": json.loads(enabled_triggers) if enabled_triggers else [],
                "intervention_style": style,
                "max_daily_interventions": max_daily,
                "crisis_intervention_enabled": bool(crisis_enabled),
                "preferred_delivery_methods": json.loads(delivery_methods) if delivery_methods else ["app_notification"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get user intervention preferences: {e}")
            return {}
    
    async def _store_emotional_intervention(self, intervention: EmotionalIntervention):
        """Store emotional intervention in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO emotional_interventions 
                (intervention_id, user_id, trigger_type, intervention_type, emotional_context,
                 content, urgency, delivery_method, scheduled_time, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                intervention.intervention_id,
                intervention.user_id,
                intervention.trigger.value,
                intervention.intervention_type.value,
                json.dumps({
                    "emotion_type": intervention.emotional_pattern.emotion_type,
                    "intensity": intervention.emotional_pattern.intensity,
                    "duration_minutes": intervention.emotional_pattern.duration_minutes
                }),
                intervention.content,
                intervention.urgency,
                intervention.delivery_method,
                intervention.scheduled_time.isoformat(),
                json.dumps(intervention.context)
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to store emotional intervention: {e}")
    
    def register_intervention_callback(self, user_id: str, callback: Callable):
        """Register callback for emotional interventions"""
        if user_id not in self.intervention_callbacks:
            self.intervention_callbacks[user_id] = []
        self.intervention_callbacks[user_id].append(callback)
    
    async def record_emotional_data(
        self, 
        user_id: str, 
        emotion_type: str,
        intensity: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """Record emotional data point for analysis"""
        try:
            pattern = EmotionalPattern(
                user_id=user_id,
                emotion_type=emotion_type,
                intensity=intensity,
                duration_minutes=0,  # Point in time
                trend="stable",
                frequency=1.0,
                context=context or {},
                detected_at=datetime.now()
            )
            
            # Store pattern
            pattern_id = f"pattern_{user_id}_{datetime.now().isoformat()}"
            
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO emotional_patterns 
                (pattern_id, user_id, emotion_type, intensity, duration_minutes, 
                 trend, frequency, context, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_id, pattern.user_id, pattern.emotion_type, pattern.intensity,
                pattern.duration_minutes, pattern.trend, pattern.frequency,
                json.dumps(pattern.context), pattern.detected_at.isoformat()
            ))
            conn.commit()
            conn.close()
            
            # Add to current patterns for analysis
            if user_id not in self.emotional_patterns:
                self.emotional_patterns[user_id] = []
            self.emotional_patterns[user_id].append(pattern)
            
            # Keep only recent patterns (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.emotional_patterns[user_id] = [
                p for p in self.emotional_patterns[user_id] 
                if p.detected_at > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to record emotional data: {e}")

# Global instance
emotional_prompts = EmotionalPromptsEngine()

__all__ = ["emotional_prompts", "EmotionalTrigger", "InterventionType", "EmotionalPattern"]
