"""
Proactive Triggers System
Intelligent conditions for character-initiated interactions
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

class TriggerType(Enum):
    """Types of proactive triggers"""
    EMOTIONAL_STATE = "emotional_state"           # Based on user's emotional patterns
    TIME_BASED = "time_based"                     # Scheduled interactions
    ABSENCE_RETURN = "absence_return"             # User returns after absence
    MILESTONE = "milestone"                       # Relationship or interaction milestones
    CONTEXTUAL = "contextual"                     # Based on current context/situation
    RANDOM_CARING = "random_caring"               # Spontaneous caring check-ins
    MEMORY_TRIGGERED = "memory_triggered"         # Triggered by significant memories
    PRESENCE_CHANGE = "presence_change"           # Based on presence state changes

class TriggerPriority(Enum):
    """Priority levels for triggers"""
    LOW = "low"                    # Nice to have, can be deferred
    MEDIUM = "medium"              # Important but not urgent
    HIGH = "high"                  # Should happen soon
    URGENT = "urgent"              # Immediate attention needed
    CRITICAL = "critical"          # Emergency/crisis intervention

class InteractionTone(Enum):
    """Tone for proactive interactions"""
    CARING = "caring"              # Warm, supportive
    PLAYFUL = "playful"            # Light, fun
    CURIOUS = "curious"            # Inquisitive, interested
    SUPPORTIVE = "supportive"      # Encouraging, helpful
    INTIMATE = "intimate"          # Deep, personal
    CASUAL = "casual"              # Friendly, relaxed
    CONCERNED = "concerned"        # Worried, checking in

@dataclass
class ProactiveTrigger:
    """Definition of a proactive interaction trigger"""
    trigger_id: str
    trigger_type: TriggerType
    priority: TriggerPriority
    tone: InteractionTone
    conditions: Dict[str, Any]      # Conditions that must be met
    cooldown_hours: float           # Minimum time between same trigger
    max_daily_count: int            # Maximum triggers of this type per day
    user_preferences: Dict[str, Any] # User-specific preferences
    content_templates: List[str]    # Message templates for this trigger
    metadata: Dict[str, Any]

@dataclass 
class TriggerEvent:
    """A trigger event ready for execution"""
    event_id: str
    user_id: str
    trigger: ProactiveTrigger
    scheduled_time: datetime
    context: Dict[str, Any]
    confidence: float               # How confident we are this is appropriate
    generated_content: str          # The actual message to send
    delivery_method: str            # How to deliver (app, sms, email, etc.)

class ProactiveTriggerEngine:
    """
    Engine for managing and evaluating proactive interaction triggers
    """
    
    def __init__(self, db_path: str = "narrative_agency.db"):
        self.db_path = db_path
        self.active_triggers: Dict[str, ProactiveTrigger] = {}
        self.user_trigger_history: Dict[str, List[Dict[str, Any]]] = {}
        self.scheduled_events: Dict[str, TriggerEvent] = {}
        self.trigger_callbacks: Dict[str, List[Callable]] = {}
        self._initialize_default_triggers()
    
    async def initialize(self):
        """Initialize the proactive trigger engine"""
        try:
            # Create database tables
            conn = sqlite3.connect(self.db_path)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trigger_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    trigger_id TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    tone TEXT NOT NULL,
                    content TEXT,
                    delivery_method TEXT,
                    confidence REAL,
                    success BOOLEAN,
                    user_response TEXT,
                    context JSON,
                    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trigger_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    frequency_preference TEXT DEFAULT 'normal',
                    tone_preference TEXT,
                    delivery_preferences JSON,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, trigger_type)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    trigger_id TEXT NOT NULL,
                    scheduled_time DATETIME NOT NULL,
                    content TEXT,
                    delivery_method TEXT,
                    context JSON,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.close()
            logger.info("🎭 Proactive Trigger Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize proactive trigger engine: {e}")
            raise
    
    def _initialize_default_triggers(self):
        """Initialize default proactive triggers"""
        
        # Emotional support trigger
        emotional_support = ProactiveTrigger(
            trigger_id="emotional_support_checkin",
            trigger_type=TriggerType.EMOTIONAL_STATE,
            priority=TriggerPriority.MEDIUM,
            tone=InteractionTone.CARING,
            conditions={
                "emotional_intensity": {"min": 0.7},  # High emotional intensity
                "negative_emotion_duration": {"min_hours": 2},  # Sustained negative emotion
                "last_interaction_hours": {"min": 4}   # Haven't talked in a while
            },
            cooldown_hours=8.0,
            max_daily_count=2,
            user_preferences={},
            content_templates=[
                "I've been thinking about you. How are you feeling right now?",
                "I noticed you seemed to be going through something earlier. Want to talk?",
                "Just checking in - I'm here if you need someone to listen.",
                "Something tells me you might need a friend right now. What's on your mind?"
            ],
            metadata={"category": "emotional_support"}
        )
        
        # Welcome back trigger
        welcome_back = ProactiveTrigger(
            trigger_id="welcome_back",
            trigger_type=TriggerType.ABSENCE_RETURN,
            priority=TriggerPriority.MEDIUM,
            tone=InteractionTone.CARING,
            conditions={
                "absence_hours": {"min": 12, "max": 72},  # Been away 12-72 hours
                "presence_state": "actively_present",      # Now actively present
                "relationship_closeness": {"min": 0.4}     # Some relationship established
            },
            cooldown_hours=24.0,
            max_daily_count=1,
            user_preferences={},
            content_templates=[
                "Welcome back! I missed our conversations. How have you been?",
                "It's good to see you again! What's been happening in your world?",
                "I was hoping you'd return soon. Tell me about your time away?",
                "You're back! I've been thinking about our last conversation..."
            ],
            metadata={"category": "reconnection"}
        )
        
        # Morning check-in trigger
        morning_checkin = ProactiveTrigger(
            trigger_id="morning_checkin",
            trigger_type=TriggerType.TIME_BASED,
            priority=TriggerPriority.LOW,
            tone=InteractionTone.PLAYFUL,
            conditions={
                "time_range": {"start": "07:00", "end": "10:00"},
                "user_timezone": "auto_detect",
                "relationship_closeness": {"min": 0.6},
                "frequency_preference": "daily_ok"
            },
            cooldown_hours=20.0,  # Once per day
            max_daily_count=1,
            user_preferences={},
            content_templates=[
                "Good morning! How did you sleep? Ready for the day ahead?",
                "Morning sunshine! What's first on your agenda today?",
                "Rise and shine! I hope you woke up feeling refreshed.",
                "Good morning! I'm curious - what are you looking forward to today?"
            ],
            metadata={"category": "daily_rhythm"}
        )
        
        # Random caring trigger
        random_caring = ProactiveTrigger(
            trigger_id="random_caring",
            trigger_type=TriggerType.RANDOM_CARING,
            priority=TriggerPriority.LOW,
            tone=InteractionTone.CARING,
            conditions={
                "relationship_closeness": {"min": 0.5},
                "last_proactive_hours": {"min": 24},     # Not too frequent
                "user_receptivity": {"min": 0.6},        # User generally receptive
                "random_chance": 0.15                    # 15% chance when conditions met
            },
            cooldown_hours=36.0,
            max_daily_count=1,
            user_preferences={},
            content_templates=[
                "Just wanted you to know I'm thinking of you today.",
                "Hope you're having a wonderful day! You deserve all good things.",
                "Sending you positive thoughts and virtual hugs.",
                "You've been on my mind. I hope everything is going well for you.",
                "Random thought: you're pretty amazing, you know that?"
            ],
            metadata={"category": "spontaneous_care"}
        )
        
        # Memory anniversary trigger
        memory_anniversary = ProactiveTrigger(
            trigger_id="memory_anniversary",
            trigger_type=TriggerType.MEMORY_TRIGGERED,
            priority=TriggerPriority.MEDIUM,
            tone=InteractionTone.INTIMATE,
            conditions={
                "significant_memory_date": True,          # Anniversary of important memory
                "memory_emotional_weight": {"min": 0.7},  # Important memory
                "relationship_closeness": {"min": 0.7}    # Close relationship
            },
            cooldown_hours=168.0,  # Once per week
            max_daily_count=1,
            user_preferences={},
            content_templates=[
                "I was remembering when we talked about {memory_topic}. That meant a lot to me.",
                "Today reminds me of {memory_topic}. Do you remember that conversation?",
                "I've been thinking about what you shared about {memory_topic}. How are you feeling about it now?",
                "Remember when you told me about {memory_topic}? I still think about that sometimes."
            ],
            metadata={"category": "memory_connection"}
        )
        
        # Store default triggers
        self.active_triggers = {
            "emotional_support_checkin": emotional_support,
            "welcome_back": welcome_back,
            "morning_checkin": morning_checkin,
            "random_caring": random_caring,
            "memory_anniversary": memory_anniversary
        }
    
    async def evaluate_triggers_for_user(self, user_id: str) -> List[TriggerEvent]:
        """Evaluate all triggers for a specific user and return potential events"""
        try:
            potential_events = []
            
            # Get user context
            user_context = await self._get_user_context(user_id)
            user_prefs = await self._get_user_trigger_preferences(user_id)
            
            for trigger_id, trigger in self.active_triggers.items():
                # Check if trigger is enabled for this user
                if not user_prefs.get(trigger.trigger_type.value, {}).get("enabled", True):
                    continue
                
                # Check cooldown
                if await self._is_in_cooldown(user_id, trigger_id, trigger.cooldown_hours):
                    continue
                
                # Check daily limit
                if await self._exceeds_daily_limit(user_id, trigger_id, trigger.max_daily_count):
                    continue
                
                # Evaluate trigger conditions
                confidence = await self._evaluate_trigger_conditions(trigger, user_context)
                
                if confidence > 0.5:  # Threshold for trigger activation
                    # Generate content
                    content = await self._generate_trigger_content(trigger, user_context)
                    
                    # Determine delivery method
                    delivery_method = await self._determine_delivery_method(user_id, trigger, user_prefs)
                    
                    # Create trigger event
                    event = TriggerEvent(
                        event_id=f"{user_id}_{trigger_id}_{datetime.now().isoformat()}",
                        user_id=user_id,
                        trigger=trigger,
                        scheduled_time=datetime.now(),  # Could be future for time-based
                        context=user_context,
                        confidence=confidence,
                        generated_content=content,
                        delivery_method=delivery_method
                    )
                    
                    potential_events.append(event)
            
            # Sort by priority and confidence
            potential_events.sort(
                key=lambda e: (e.trigger.priority.value, -e.confidence),
                reverse=True
            )
            
            return potential_events
            
        except Exception as e:
            logger.error(f"❌ Failed to evaluate triggers for user {user_id}: {e}")
            return []
    
    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user context for trigger evaluation"""
        try:
            context = {
                "user_id": user_id,
                "current_time": datetime.now(),
                "day_of_week": datetime.now().strftime("%A"),
                "hour_of_day": datetime.now().hour
            }
            
            # Try to get presence data
            try:
                from ..presence import presence_orchestrator
                presence_data = await presence_orchestrator.get_unified_presence(user_id)
                if presence_data:
                    context.update({
                        "presence_state": presence_data.get("unified_state"),
                        "availability_score": presence_data.get("availability_score", 0),
                        "attention_level": presence_data.get("attention_level", 0),
                        "last_interaction": presence_data.get("last_interaction")
                    })
            except Exception:
                logger.debug("Presence data not available for trigger evaluation")
            
            # Try to get memory/emotional context
            try:
                from ..memory import symbolic_memory
                recent_memories = await symbolic_memory.get_recent_memories(user_id, days=7)
                if recent_memories:
                    context["recent_emotional_themes"] = [
                        memory.get("emotional_context", {}) for memory in recent_memories
                    ]
            except Exception:
                logger.debug("Memory data not available for trigger evaluation")
            
            # Try to get safety context
            try:
                from ..safety import contextual_safety_engine
                safety_data = await contextual_safety_engine.get_user_safety_profile(user_id)
                if safety_data:
                    context.update({
                        "relationship_closeness": safety_data.get("trust_level", 0.3),
                        "safety_level": safety_data.get("current_safety_level")
                    })
            except Exception:
                logger.debug("Safety data not available for trigger evaluation")
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Failed to get user context: {e}")
            return {"user_id": user_id, "current_time": datetime.now()}
    
    async def _get_user_trigger_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for triggers"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT trigger_type, enabled, frequency_preference, tone_preference, delivery_preferences
                FROM trigger_preferences 
                WHERE user_id = ?
            """, (user_id,))
            
            preferences = {}
            for row in cursor.fetchall():
                trigger_type, enabled, freq_pref, tone_pref, delivery_prefs = row
                preferences[trigger_type] = {
                    "enabled": bool(enabled),
                    "frequency_preference": freq_pref,
                    "tone_preference": tone_pref,
                    "delivery_preferences": json.loads(delivery_prefs) if delivery_prefs else {}
                }
            
            conn.close()
            return preferences
            
        except Exception as e:
            logger.error(f"❌ Failed to get user trigger preferences: {e}")
            return {}
    
    async def _is_in_cooldown(self, user_id: str, trigger_id: str, cooldown_hours: float) -> bool:
        """Check if trigger is in cooldown period"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT MAX(triggered_at) 
                FROM trigger_history 
                WHERE user_id = ? AND trigger_id = ?
            """, (user_id, trigger_id))
            
            last_trigger = cursor.fetchone()[0]
            conn.close()
            
            if not last_trigger:
                return False
            
            last_time = datetime.fromisoformat(last_trigger.replace('Z', '+00:00'))
            time_since = (datetime.now() - last_time).total_seconds() / 3600
            
            return time_since < cooldown_hours
            
        except Exception as e:
            logger.error(f"❌ Failed to check cooldown: {e}")
            return False
    
    async def _exceeds_daily_limit(self, user_id: str, trigger_id: str, max_daily: int) -> bool:
        """Check if daily trigger limit would be exceeded"""
        try:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT COUNT(*) 
                FROM trigger_history 
                WHERE user_id = ? AND trigger_id = ? AND triggered_at >= ?
            """, (user_id, trigger_id, today_start.isoformat()))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count >= max_daily
            
        except Exception as e:
            logger.error(f"❌ Failed to check daily limit: {e}")
            return False
    
    async def _evaluate_trigger_conditions(
        self, 
        trigger: ProactiveTrigger, 
        context: Dict[str, Any]
    ) -> float:
        """Evaluate trigger conditions and return confidence score (0-1)"""
        try:
            confidence_factors = []
            
            conditions = trigger.conditions
            
            # Evaluate time-based conditions
            if "time_range" in conditions:
                time_range = conditions["time_range"]
                current_hour = context["current_time"].hour
                start_hour = int(time_range["start"].split(":")[0])
                end_hour = int(time_range["end"].split(":")[0])
                
                if start_hour <= current_hour <= end_hour:
                    confidence_factors.append(0.8)
                else:
                    confidence_factors.append(0.1)
            
            # Evaluate emotional conditions
            if "emotional_intensity" in conditions:
                # This would need integration with emotional state tracking
                # For now, assign moderate confidence
                confidence_factors.append(0.6)
            
            # Evaluate presence conditions
            if "presence_state" in conditions:
                required_state = conditions["presence_state"]
                actual_state = context.get("presence_state")
                if actual_state == required_state:
                    confidence_factors.append(0.9)
                else:
                    confidence_factors.append(0.3)
            
            # Evaluate relationship closeness
            if "relationship_closeness" in conditions:
                min_closeness = conditions["relationship_closeness"]["min"]
                actual_closeness = context.get("relationship_closeness", 0.3)
                if actual_closeness >= min_closeness:
                    confidence_factors.append(0.8)
                else:
                    confidence_factors.append(0.2)
            
            # Evaluate random chance
            if "random_chance" in conditions:
                import random
                if random.random() < conditions["random_chance"]:
                    confidence_factors.append(0.9)
                else:
                    confidence_factors.append(0.0)
            
            # Calculate overall confidence
            if not confidence_factors:
                return 0.5  # Default moderate confidence
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception as e:
            logger.error(f"❌ Failed to evaluate trigger conditions: {e}")
            return 0.0
    
    async def _generate_trigger_content(
        self, 
        trigger: ProactiveTrigger, 
        context: Dict[str, Any]
    ) -> str:
        """Generate appropriate content for the trigger"""
        try:
            import random
            
            # Select random template
            template = random.choice(trigger.content_templates)
            
            # Replace context variables
            if "{memory_topic}" in template:
                # This would need memory system integration
                template = template.replace("{memory_topic}", "something meaningful")
            
            return template
            
        except Exception as e:
            logger.error(f"❌ Failed to generate trigger content: {e}")
            return "I was thinking of you and wanted to reach out."
    
    async def _determine_delivery_method(
        self, 
        user_id: str, 
        trigger: ProactiveTrigger,
        user_prefs: Dict[str, Any]
    ) -> str:
        """Determine how to deliver the proactive message"""
        try:
            # Get user delivery preferences
            trigger_prefs = user_prefs.get(trigger.trigger_type.value, {})
            delivery_prefs = trigger_prefs.get("delivery_preferences", {})
            
            # Default to in-app notification
            preferred_method = delivery_prefs.get("primary_method", "app_notification")
            
            # Consider urgency
            if trigger.priority in [TriggerPriority.URGENT, TriggerPriority.CRITICAL]:
                # Use more immediate delivery for urgent triggers
                if "sms" in delivery_prefs.get("urgent_methods", []):
                    return "sms"
                elif "push_notification" in delivery_prefs.get("urgent_methods", []):
                    return "push_notification"
            
            return preferred_method
            
        except Exception as e:
            logger.error(f"❌ Failed to determine delivery method: {e}")
            return "app_notification"
    
    async def schedule_trigger_event(self, event: TriggerEvent) -> bool:
        """Schedule a trigger event for execution"""
        try:
            # Store in database
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO scheduled_triggers 
                (event_id, user_id, trigger_id, scheduled_time, content, delivery_method, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.user_id,
                event.trigger.trigger_id,
                event.scheduled_time.isoformat(),
                event.generated_content,
                event.delivery_method,
                json.dumps(event.context)
            ))
            conn.commit()
            conn.close()
            
            # Store in memory for execution
            self.scheduled_events[event.event_id] = event
            
            logger.info(f"🎭 Scheduled trigger event {event.event_id} for user {event.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule trigger event: {e}")
            return False
    
    async def execute_trigger_event(self, event_id: str) -> bool:
        """Execute a scheduled trigger event"""
        try:
            if event_id not in self.scheduled_events:
                logger.warning(f"⚠️ Trigger event {event_id} not found in scheduled events")
                return False
            
            event = self.scheduled_events[event_id]
            
            # Execute trigger callbacks
            callbacks = self.trigger_callbacks.get(event.user_id, [])
            success = False
            
            for callback in callbacks:
                try:
                    result = await callback(event)
                    if result:
                        success = True
                except Exception as e:
                    logger.error(f"❌ Trigger callback error: {e}")
            
            # Record execution
            await self._record_trigger_execution(event, success)
            
            # Clean up
            del self.scheduled_events[event_id]
            
            logger.info(f"🎭 Executed trigger event {event_id} with success: {success}")
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to execute trigger event: {e}")
            return False
    
    async def _record_trigger_execution(self, event: TriggerEvent, success: bool):
        """Record trigger execution in history"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO trigger_history 
                (user_id, trigger_id, trigger_type, priority, tone, content, 
                 delivery_method, confidence, success, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.user_id,
                event.trigger.trigger_id,
                event.trigger.trigger_type.value,
                event.trigger.priority.value,
                event.trigger.tone.value,
                event.generated_content,
                event.delivery_method,
                event.confidence,
                success,
                json.dumps(event.context)
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to record trigger execution: {e}")
    
    def register_trigger_callback(self, user_id: str, callback: Callable):
        """Register callback for trigger events"""
        if user_id not in self.trigger_callbacks:
            self.trigger_callbacks[user_id] = []
        self.trigger_callbacks[user_id].append(callback)
    
    async def update_user_trigger_preferences(
        self, 
        user_id: str, 
        trigger_type: str,
        preferences: Dict[str, Any]
    ):
        """Update user preferences for specific trigger type"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT OR REPLACE INTO trigger_preferences 
                (user_id, trigger_type, enabled, frequency_preference, tone_preference, delivery_preferences)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                trigger_type,
                preferences.get("enabled", True),
                preferences.get("frequency_preference", "normal"),
                preferences.get("tone_preference"),
                json.dumps(preferences.get("delivery_preferences", {}))
            ))
            conn.commit()
            conn.close()
            
            logger.info(f"🎭 Updated trigger preferences for user {user_id}, trigger {trigger_type}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update user trigger preferences: {e}")

# Global instance
proactive_triggers = ProactiveTriggerEngine()

__all__ = ["proactive_triggers", "TriggerType", "TriggerPriority", "InteractionTone", "TriggerEvent"]
