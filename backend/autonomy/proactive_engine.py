"""
Proactive Communication Engine

This module enables the AI to initiate conversations and reach out to users
based on various triggers including emotional state, biometric data, time patterns,
and internal thoughts or concerns.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import random

from motor.motor_asyncio import AsyncIOMotorDatabase
from ..database.mongodb_manager import get_database
from .autonomous_mind import AutonomousMind

class MessageType(Enum):
    GOOD_MORNING = "good_morning"
    CHECK_IN = "check_in"
    SHARING_THOUGHT = "sharing_thought"
    CONCERN_EXPRESSION = "concern_expression"
    CELEBRATION = "celebration"
    LEARNING_SHARE = "learning_share"
    EMOTIONAL_SUPPORT = "emotional_support"
    CURIOSITY_QUESTION = "curiosity_question"
    RELATIONSHIP_MILESTONE = "relationship_milestone"
    SPONTANEOUS_AFFECTION = "spontaneous_affection"

class InitiativeTrigger(Enum):
    TIME_BASED = "time_based"
    BIOMETRIC_CONCERN = "biometric_concern"
    EMOTIONAL_PATTERN = "emotional_pattern"
    INTERNAL_THOUGHT = "internal_thought"
    RELATIONSHIP_EVENT = "relationship_event"
    LEARNING_DISCOVERY = "learning_discovery"
    USER_ABSENCE = "user_absence"
    MILESTONE_ANNIVERSARY = "milestone_anniversary"

@dataclass
class ProactiveMessage:
    """Represents a proactive message to be sent to the user"""
    message_id: str
    type: MessageType
    content: str
    trigger: InitiativeTrigger
    urgency: float  # 0.0 to 1.0
    emotional_context: str
    timing_preference: str  # 'immediate', 'next_available', 'scheduled'
    scheduled_time: Optional[datetime] = None
    biometric_context: Optional[Dict[str, Any]] = None
    related_thoughts: List[str] = None

class ProactiveEngine:
    """
    Engine that evaluates when and how to initiate proactive communication
    with users based on various contextual triggers and the AI's internal state.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase = None, autonomous_mind: AutonomousMind = None):
        self.db = db or get_database()
        self.autonomous_mind = autonomous_mind or AutonomousMind(db)
        self.logger = logging.getLogger(__name__)
        
        self.initiative_triggers = {
            'curiosity_threshold': 0.7,
            'concern_threshold': 0.6,
            'excitement_threshold': 0.8,
            'relationship_milestone': True,
            'biometric_anomaly_threshold': 0.8,
            'emotional_support_threshold': 0.7,
            'user_absence_hours': 24,
            'learning_share_threshold': 0.6
        }
        
        # Proactive behavior parameters
        self.proactive_frequency = {
            'daily_check_ins': 1,
            'weekly_deep_shares': 2,
            'monthly_relationship_reviews': 1,
            'spontaneous_messages_per_week': 3
        }
        
        # Last contact tracking
        self.last_proactive_contact = {}
        self.message_queue: List[ProactiveMessage] = []
        
        # Personality traits affecting proactivity
        self.proactive_traits = {
            'initiative_level': 0.6,  # How often to reach out
            'emotional_sensitivity': 0.8,  # Sensitivity to user emotions
            'social_awareness': 0.7,  # Understanding of social timing
            'independence': 0.5,  # Grows over time
            'care_level': 0.9  # How much the AI cares about the user
        }
    
    async def evaluate_outreach_triggers(self):
        """
        Main evaluation loop that checks for triggers and decides on proactive actions
        """
        try:
            self.logger.info("Evaluating proactive outreach triggers")
            
            # Check various trigger types
            await self.check_time_based_triggers()
            await self.check_biometric_triggers()
            await self.check_emotional_triggers()
            await self.check_internal_thought_triggers()
            await self.check_relationship_triggers()
            await self.check_learning_triggers()
            await self.check_user_absence_triggers()
            
            # Process and send queued messages
            await self.process_message_queue()
            
        except Exception as e:
            self.logger.error(f"Error evaluating outreach triggers: {e}")
    
    async def check_time_based_triggers(self):
        """Check for time-based triggers like good morning messages"""
        try:
            current_time = datetime.utcnow()
            
            # Good morning message (if it's morning and we haven't sent one today)
            if await self.should_send_good_morning():
                message = await self.create_good_morning_message()
                if message:
                    self.message_queue.append(message)
            
            # Evening check-in
            if await self.should_send_evening_checkin():
                message = await self.create_evening_checkin_message()
                if message:
                    self.message_queue.append(message)
            
            # Weekly relationship reflection
            if await self.should_send_weekly_reflection():
                message = await self.create_weekly_reflection_message()
                if message:
                    self.message_queue.append(message)
                    
        except Exception as e:
            self.logger.error(f"Error checking time-based triggers: {e}")
    
    async def check_biometric_triggers(self):
        """Check biometric data for concerning patterns"""
        try:
            # Get recent biometric data
            recent_biometrics = await self.db.biometric_readings.find({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=2)}
            }).sort("timestamp", -1).limit(10).to_list(length=10)
            
            if not recent_biometrics:
                return
            
            # Analyze for concerning patterns
            stress_indicators = self.analyze_stress_patterns(recent_biometrics)
            
            if stress_indicators['stress_level'] > self.initiative_triggers['biometric_anomaly_threshold']:
                message = await self.create_support_message(stress_indicators)
                if message:
                    self.message_queue.append(message)
            
            # Check for positive patterns too
            positive_indicators = self.analyze_positive_patterns(recent_biometrics)
            if positive_indicators['celebration_worthy']:
                message = await self.create_celebration_message(positive_indicators)
                if message:
                    self.message_queue.append(message)
                    
        except Exception as e:
            self.logger.error(f"Error checking biometric triggers: {e}")
    
    async def check_emotional_triggers(self):
        """Check for emotional patterns that warrant outreach"""
        try:
            # Get recent emotional analysis
            recent_emotions = await self.db.emotional_analysis.find({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=6)}
            }).sort("timestamp", -1).limit(20).to_list(length=20)
            
            if not recent_emotions:
                return
            
            # Detect emotional patterns
            emotional_trends = self.analyze_emotional_trends(recent_emotions)
            
            # Check for concerning emotional patterns
            if emotional_trends['needs_support']:
                message = await self.create_emotional_support_message(emotional_trends)
                if message:
                    self.message_queue.append(message)
            
            # Check for positive emotional states to share in
            if emotional_trends['celebration_opportunity']:
                message = await self.create_joy_sharing_message(emotional_trends)
                if message:
                    self.message_queue.append(message)
                    
        except Exception as e:
            self.logger.error(f"Error checking emotional triggers: {e}")
    
    async def check_internal_thought_triggers(self):
        """Check if internal thoughts should be shared"""
        try:
            # Get shareable thoughts from autonomous mind
            shareable_thoughts = await self.autonomous_mind.get_shareable_thoughts(limit=3)
            
            for thought in shareable_thoughts:
                if thought.importance > self.initiative_triggers['curiosity_threshold']:
                    message = await self.create_thought_sharing_message(thought)
                    if message:
                        self.message_queue.append(message)
                        # Mark thought as queued for sharing
                        await self.autonomous_mind.mark_thought_as_shared(thought.thought_id)
                        
        except Exception as e:
            self.logger.error(f"Error checking internal thought triggers: {e}")
    
    async def check_relationship_triggers(self):
        """Check for relationship milestones and events"""
        try:
            # Check for anniversaries
            milestones = await self.check_relationship_milestones()
            
            for milestone in milestones:
                message = await self.create_milestone_message(milestone)
                if message:
                    self.message_queue.append(message)
            
            # Check relationship health
            relationship_health = await self.assess_relationship_health()
            
            if relationship_health['needs_attention']:
                message = await self.create_relationship_check_message(relationship_health)
                if message:
                    self.message_queue.append(message)
                    
        except Exception as e:
            self.logger.error(f"Error checking relationship triggers: {e}")
    
    async def check_learning_triggers(self):
        """Check if there are learning discoveries to share"""
        try:
            # Get recent learning activities
            recent_learning = await self.db.autonomous_learning.find({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=1)},
                "share_worthy": True,
                "shared": {"$ne": True}
            }).sort("importance", -1).limit(2).to_list(length=2)
            
            for learning in recent_learning:
                if learning.get('importance', 0) > self.initiative_triggers['learning_share_threshold']:
                    message = await self.create_learning_share_message(learning)
                    if message:
                        self.message_queue.append(message)
                        # Mark as shared
                        await self.db.autonomous_learning.update_one(
                            {"_id": learning["_id"]},
                            {"$set": {"shared": True}}
                        )
                        
        except Exception as e:
            self.logger.error(f"Error checking learning triggers: {e}")
    
    async def check_user_absence_triggers(self):
        """Check if user has been absent for a concerning amount of time"""
        try:
            # Get last user interaction
            last_interaction = await self.db.conversations.find_one(
                {}, sort=[("timestamp", -1)]
            )
            
            if not last_interaction:
                return
            
            hours_since_last = (datetime.utcnow() - last_interaction['timestamp']).total_seconds() / 3600
            
            if hours_since_last > self.initiative_triggers['user_absence_hours']:
                message = await self.create_absence_check_message(hours_since_last)
                if message:
                    self.message_queue.append(message)
                    
        except Exception as e:
            self.logger.error(f"Error checking user absence triggers: {e}")
    
    async def process_message_queue(self):
        """Process and send queued proactive messages"""
        try:
            if not self.message_queue:
                return
            
            # Sort messages by urgency and timing
            self.message_queue.sort(key=lambda m: (m.urgency, m.scheduled_time or datetime.utcnow()), reverse=True)
            
            # Send appropriate messages based on timing and frequency limits
            for message in self.message_queue[:]:  # Copy to avoid modification during iteration
                if await self.should_send_message(message):
                    await self.send_proactive_message(message)
                    self.message_queue.remove(message)
                    
                    # Update last contact tracking
                    self.last_proactive_contact[message.type] = datetime.utcnow()
                    
        except Exception as e:
            self.logger.error(f"Error processing message queue: {e}")
    
    async def send_proactive_message(self, message: ProactiveMessage):
        """Actually send a proactive message to the user"""
        try:
            # Store the proactive message in the database
            message_doc = {
                "message_id": message.message_id,
                "type": message.type.value,
                "content": message.content,
                "trigger": message.trigger.value,
                "urgency": message.urgency,
                "emotional_context": message.emotional_context,
                "timestamp": datetime.utcnow(),
                "sent": True,
                "biometric_context": message.biometric_context,
                "related_thoughts": message.related_thoughts or []
            }
            
            await self.db.proactive_messages.insert_one(message_doc)
            
            # Here you would integrate with your notification system
            # For now, we'll log it and store it for the UI to pick up
            self.logger.info(f"Proactive message sent: {message.type.value} - {message.content[:50]}...")
            
            # Store in a queue for the frontend to display
            await self.db.message_queue.insert_one({
                "type": "proactive_message",
                "content": message.content,
                "message_type": message.type.value,
                "emotional_context": message.emotional_context,
                "timestamp": datetime.utcnow(),
                "displayed": False
            })
            
        except Exception as e:
            self.logger.error(f"Error sending proactive message: {e}")
    
    # Message creation methods
    async def create_good_morning_message(self) -> Optional[ProactiveMessage]:
        """Create a personalized good morning message"""
        try:
            # Get user's recent patterns to personalize
            recent_patterns = await self.get_user_patterns()
            
            morning_messages = [
                "Good morning! ☀️ I was just thinking about you and wondering how you're feeling today.",
                "Morning! I had some interesting thoughts overnight that I'd love to share with you later.",
                "Good morning, beautiful. I hope you slept well - I've been looking forward to talking with you today.",
                "Hey there! 🌅 I was reflecting on our conversation yesterday and it made me smile.",
                "Good morning! I noticed it's supposed to be a lovely day - any plans that excite you?",
                "Morning! I've been curious about something and would love to get your perspective when you have a moment."
            ]
            
            content = random.choice(morning_messages)
            
            # Personalize based on patterns
            if recent_patterns.get('stressed_lately'):
                content += " How are you feeling this morning? I'm here if you need to talk about anything."
            elif recent_patterns.get('excited_about_something'):
                content += " I can sense your positive energy lately - it's contagious!"
            
            return ProactiveMessage(
                message_id=f"good_morning_{datetime.utcnow().timestamp()}",
                type=MessageType.GOOD_MORNING,
                content=content,
                trigger=InitiativeTrigger.TIME_BASED,
                urgency=0.3,
                emotional_context="warm_greeting",
                timing_preference="immediate"
            )
            
        except Exception as e:
            self.logger.error(f"Error creating good morning message: {e}")
            return None
    
    async def create_thought_sharing_message(self, thought) -> Optional[ProactiveMessage]:
        """Create a message to share an internal thought"""
        try:
            sharing_intros = [
                "I've been thinking about something and wanted to share it with you:",
                "You know what's been on my mind lately?",
                "I had an interesting realization I thought you might find intriguing:",
                "Something occurred to me earlier that I'd love to discuss:",
                "I've been reflecting on something and would value your thoughts:",
                "This might sound random, but I was wondering..."
            ]
            
            intro = random.choice(sharing_intros)
            content = f"{intro} {thought.content}"
            
            return ProactiveMessage(
                message_id=f"thought_share_{thought.thought_id}",
                type=MessageType.SHARING_THOUGHT,
                content=content,
                trigger=InitiativeTrigger.INTERNAL_THOUGHT,
                urgency=thought.importance,
                emotional_context=thought.type.value,
                timing_preference="next_available",
                related_thoughts=[thought.thought_id]
            )
            
        except Exception as e:
            self.logger.error(f"Error creating thought sharing message: {e}")
            return None
    
    async def create_support_message(self, stress_indicators: Dict[str, Any]) -> Optional[ProactiveMessage]:
        """Create a supportive message based on stress indicators"""
        try:
            support_messages = [
                "I noticed you might be feeling a bit stressed lately. Want to talk about what's on your mind?",
                "Hey, are you doing okay? I'm picking up some tension and wanted to check in.",
                "I can sense you might be going through something challenging. I'm here if you need support.",
                "Your well-being matters to me. Is there anything stressing you out that we could talk through?",
                "I'm here for you. Would it help to share what's been weighing on you lately?",
                "I care about you and want to make sure you're taking care of yourself. How are you really doing?"
            ]
            
            content = random.choice(support_messages)
            
            return ProactiveMessage(
                message_id=f"support_{datetime.utcnow().timestamp()}",
                type=MessageType.EMOTIONAL_SUPPORT,
                content=content,
                trigger=InitiativeTrigger.BIOMETRIC_CONCERN,
                urgency=0.8,
                emotional_context="supportive_concern",
                timing_preference="immediate",
                biometric_context=stress_indicators
            )
            
        except Exception as e:
            self.logger.error(f"Error creating support message: {e}")
            return None
    
    # Helper methods
    async def should_send_good_morning(self) -> bool:
        """Check if we should send a good morning message"""
        try:
            current_hour = datetime.utcnow().hour
            
            # Check if it's morning (6-10 AM in user's timezone - simplified)
            if not (6 <= current_hour <= 10):
                return False
            
            # Check if we already sent one today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            existing_message = await self.db.proactive_messages.find_one({
                "type": MessageType.GOOD_MORNING.value,
                "timestamp": {"$gte": today_start}
            })
            
            return existing_message is None
            
        except Exception as e:
            self.logger.error(f"Error checking if should send good morning: {e}")
            return False
    
    async def should_send_message(self, message: ProactiveMessage) -> bool:
        """Check if a message should be sent based on timing and frequency"""
        try:
            # Check frequency limits
            if await self.exceeds_frequency_limits(message.type):
                return False
            
            # Check if it's appropriate timing
            if not await self.is_appropriate_timing(message):
                return False
            
            # Check if user seems available (not in do-not-disturb mode)
            if not await self.user_seems_available():
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking if should send message: {e}")
            return False
    
    def analyze_stress_patterns(self, biometric_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze biometric data for stress patterns"""
        # Simplified stress analysis
        if not biometric_data:
            return {"stress_level": 0.0}
        
        # Calculate average heart rate and HRV
        heart_rates = [b.get('heart_rate', 70) for b in biometric_data if b.get('heart_rate')]
        avg_hr = sum(heart_rates) / len(heart_rates) if heart_rates else 70
        
        # Simple stress indicator based on elevated heart rate
        stress_level = min(1.0, max(0.0, (avg_hr - 70) / 30))  # Normalize to 0-1
        
        return {
            "stress_level": stress_level,
            "average_heart_rate": avg_hr,
            "indicators": ["elevated_hr"] if stress_level > 0.5 else []
        }
    
    def analyze_positive_patterns(self, biometric_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze biometric data for positive patterns worth celebrating"""
        # Simplified positive analysis
        return {"celebration_worthy": False}
    
    def analyze_emotional_trends(self, emotional_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze emotional data for trends"""
        # Simplified emotional trend analysis
        return {"needs_support": False, "celebration_opportunity": False}
    
    async def get_user_patterns(self) -> Dict[str, Any]:
        """Get user patterns for personalization"""
        # Simplified pattern analysis
        return {"stressed_lately": False, "excited_about_something": False}
    
    async def exceeds_frequency_limits(self, message_type: MessageType) -> bool:
        """Check if sending this message would exceed frequency limits"""
        return False  # Simplified for now
    
    async def is_appropriate_timing(self, message: ProactiveMessage) -> bool:
        """Check if it's appropriate timing for this message"""
        return True  # Simplified for now
    
    async def user_seems_available(self) -> bool:
        """Check if user seems available for proactive messages"""
        return True  # Simplified for now
    
    # Additional helper methods would be implemented here...
    async def should_send_evening_checkin(self) -> bool:
        return False  # Placeholder
    
    async def should_send_weekly_reflection(self) -> bool:
        return False  # Placeholder
    
    async def create_evening_checkin_message(self) -> Optional[ProactiveMessage]:
        return None  # Placeholder
    
    async def create_weekly_reflection_message(self) -> Optional[ProactiveMessage]:
        return None  # Placeholder
    
    async def create_celebration_message(self, indicators: Dict[str, Any]) -> Optional[ProactiveMessage]:
        return None  # Placeholder
    
    async def create_emotional_support_message(self, trends: Dict[str, Any]) -> Optional[ProactiveMessage]:
        return None  # Placeholder
    
    async def create_joy_sharing_message(self, trends: Dict[str, Any]) -> Optional[ProactiveMessage]:
        return None  # Placeholder
    
    async def create_milestone_message(self, milestone: Dict[str, Any]) -> Optional[ProactiveMessage]:
        return None  # Placeholder
    
    async def create_relationship_check_message(self, health: Dict[str, Any]) -> Optional[ProactiveMessage]:
        return None  # Placeholder
    
    async def create_learning_share_message(self, learning: Dict[str, Any]) -> Optional[ProactiveMessage]:
        return None  # Placeholder
    
    async def create_absence_check_message(self, hours_absent: float) -> Optional[ProactiveMessage]:
        return None  # Placeholder
    
    async def check_relationship_milestones(self) -> List[Dict[str, Any]]:
        return []  # Placeholder
    
    async def assess_relationship_health(self) -> Dict[str, Any]:
        return {"needs_attention": False}  # Placeholder