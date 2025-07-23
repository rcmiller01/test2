"""
Narrative Agency Orchestrator
Central coordinator for all proactive character interactions
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json

from .proactive_triggers import proactive_triggers, TriggerEvent, TriggerType
from .sms_integration import sms_integration, SMSType
from .scheduled_interactions import scheduled_interactions, ScheduleType
from .emotional_prompts import emotional_prompts, EmotionalTrigger

logger = logging.getLogger(__name__)

class AgencyEventType(Enum):
    """Types of agency events"""
    PROACTIVE_TRIGGER = "proactive_trigger"
    SCHEDULED_INTERACTION = "scheduled_interaction"
    EMOTIONAL_INTERVENTION = "emotional_intervention"
    SMS_MESSAGE = "sms_message"

class DeliveryChannel(Enum):
    """Available delivery channels"""
    APP_NOTIFICATION = "app_notification"
    IN_APP_MESSAGE = "in_app_message"
    SMS = "sms"
    EMAIL = "email"
    PUSH_NOTIFICATION = "push_notification"

@dataclass
class AgencyEvent:
    """Unified agency event"""
    event_id: str
    user_id: str
    event_type: AgencyEventType
    content: str
    priority: str
    delivery_channels: List[DeliveryChannel]
    scheduled_time: datetime
    source_system: str
    metadata: Dict[str, Any]
    executed: bool = False
    execution_time: Optional[datetime] = None

class NarrativeAgencyOrchestrator:
    """
    Central orchestrator for all proactive narrative interactions
    """
    
    def __init__(self):
        self.active_users: Dict[str, Dict[str, Any]] = {}
        self.event_queue: List[AgencyEvent] = []
        self.delivery_callbacks: Dict[str, List[Callable]] = {}
        self.orchestrator_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Integration settings
        self.integration_weights = {
            "proactive_triggers": 0.4,
            "emotional_prompts": 0.3,
            "scheduled_interactions": 0.2,
            "sms_integration": 0.1
        }
    
    async def initialize(self):
        """Initialize the narrative agency orchestrator"""
        try:
            # Initialize all subsystems
            await proactive_triggers.initialize()
            await sms_integration.initialize()
            await scheduled_interactions.initialize()
            await emotional_prompts.initialize()
            
            logger.info("🎭 Narrative Agency Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize narrative agency orchestrator: {e}")
            raise
    
    async def start_user_agency(self, user_id: str, session_id: str, preferences: Optional[Dict[str, Any]] = None):
        """Start comprehensive narrative agency for a user"""
        try:
            # Initialize user preferences
            user_prefs = preferences or {}
            self.active_users[user_id] = {
                "session_id": session_id,
                "preferences": user_prefs,
                "start_time": datetime.now(),
                "last_interaction": datetime.now(),
                "agency_events_count": 0
            }
            
            # Register callbacks with subsystems
            proactive_triggers.register_trigger_callback(user_id, self._handle_proactive_trigger)
            scheduled_interactions.register_execution_callback(user_id, self._handle_scheduled_interaction)
            emotional_prompts.register_intervention_callback(user_id, self._handle_emotional_intervention)
            
            # Start monitoring systems
            await emotional_prompts.start_emotional_monitoring(user_id)
            
            # Start orchestrator if not running
            if not self.running:
                await self.start_orchestrator()
            
            logger.info(f"🎭 Started narrative agency for user {user_id}")
            
            return {
                "user_id": user_id,
                "session_id": session_id,
                "agency_active": True,
                "available_channels": [channel.value for channel in DeliveryChannel],
                "subsystems": {
                    "proactive_triggers": "active",
                    "emotional_prompts": "active", 
                    "scheduled_interactions": "active",
                    "sms_integration": "active" if sms_integration.enabled else "disabled"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start user agency: {e}")
            raise
    
    async def start_orchestrator(self):
        """Start the main orchestration loop"""
        try:
            if self.running:
                logger.warning("🎭 Orchestrator already running")
                return
            
            self.running = True
            
            # Start scheduled interactions scheduler
            await scheduled_interactions.start_scheduler()
            
            # Start main orchestration task
            self.orchestrator_task = asyncio.create_task(self._orchestration_loop())
            
            logger.info("🎭 Narrative agency orchestrator started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start orchestrator: {e}")
    
    async def _orchestration_loop(self):
        """Main orchestration loop"""
        try:
            while self.running:
                # Process all active users
                for user_id in list(self.active_users.keys()):
                    await self._process_user_agency(user_id)
                
                # Process scheduled SMS messages
                await sms_integration.process_scheduled_messages()
                
                # Process event queue
                await self._process_event_queue()
                
                # Sleep for 30 seconds between cycles
                await asyncio.sleep(30)
                
        except asyncio.CancelledError:
            logger.debug("🎭 Orchestration loop cancelled")
        except Exception as e:
            logger.error(f"❌ Orchestration loop error: {e}")
    
    async def _process_user_agency(self, user_id: str):
        """Process agency events for a specific user"""
        try:
            # Evaluate proactive triggers
            trigger_events = await proactive_triggers.evaluate_triggers_for_user(user_id)
            
            for trigger_event in trigger_events:
                agency_event = await self._convert_trigger_to_agency_event(trigger_event)
                if agency_event:
                    self.event_queue.append(agency_event)
            
        except Exception as e:
            logger.error(f"❌ Failed to process user agency for {user_id}: {e}")
    
    async def _convert_trigger_to_agency_event(self, trigger_event: TriggerEvent) -> Optional[AgencyEvent]:
        """Convert trigger event to unified agency event"""
        try:
            # Determine delivery channels based on priority and user preferences
            delivery_channels = await self._determine_delivery_channels(
                trigger_event.user_id, 
                trigger_event.trigger.priority.value,
                trigger_event.delivery_method
            )
            
            agency_event = AgencyEvent(
                event_id=trigger_event.event_id,
                user_id=trigger_event.user_id,
                event_type=AgencyEventType.PROACTIVE_TRIGGER,
                content=trigger_event.generated_content,
                priority=trigger_event.trigger.priority.value,
                delivery_channels=delivery_channels,
                scheduled_time=trigger_event.scheduled_time,
                source_system="proactive_triggers",
                metadata={
                    "trigger_type": trigger_event.trigger.trigger_type.value,
                    "confidence": trigger_event.confidence,
                    "context": trigger_event.context
                }
            )
            
            return agency_event
            
        except Exception as e:
            logger.error(f"❌ Failed to convert trigger to agency event: {e}")
            return None
    
    async def _determine_delivery_channels(
        self, 
        user_id: str, 
        priority: str,
        preferred_method: str
    ) -> List[DeliveryChannel]:
        """Determine appropriate delivery channels"""
        try:
            channels = []
            
            # Always include in-app as primary channel
            channels.append(DeliveryChannel.IN_APP_MESSAGE)
            
            # Add additional channels based on priority
            if priority in ["high", "urgent", "critical"]:
                channels.append(DeliveryChannel.APP_NOTIFICATION)
                
                # Add SMS for urgent/critical if enabled and configured
                if (priority in ["urgent", "critical"] and 
                    sms_integration.enabled and
                    preferred_method == "sms"):
                    channels.append(DeliveryChannel.SMS)
            
            # Add push notification for medium+ priority
            if priority in ["medium", "high", "urgent", "critical"]:
                channels.append(DeliveryChannel.PUSH_NOTIFICATION)
            
            return channels
            
        except Exception as e:
            logger.error(f"❌ Failed to determine delivery channels: {e}")
            return [DeliveryChannel.IN_APP_MESSAGE]
    
    async def _process_event_queue(self):
        """Process queued agency events"""
        try:
            current_time = datetime.now()
            
            # Get events ready for execution
            ready_events = [
                event for event in self.event_queue
                if not event.executed and event.scheduled_time <= current_time
            ]
            
            # Sort by priority
            priority_order = {"critical": 0, "urgent": 1, "high": 2, "medium": 3, "low": 4}
            ready_events.sort(key=lambda e: priority_order.get(e.priority, 5))
            
            for event in ready_events:
                await self._execute_agency_event(event)
            
        except Exception as e:
            logger.error(f"❌ Failed to process event queue: {e}")
    
    async def _execute_agency_event(self, event: AgencyEvent):
        """Execute an agency event"""
        try:
            success = False
            
            # Execute via delivery channels
            for channel in event.delivery_channels:
                if channel == DeliveryChannel.SMS:
                    # Send via SMS
                    sms_type = self._map_event_to_sms_type(event)
                    result = await sms_integration.send_proactive_sms(
                        user_id=event.user_id,
                        content=event.content,
                        sms_type=sms_type,
                        priority=event.priority
                    )
                    if result:
                        success = True
                
                elif channel in [DeliveryChannel.IN_APP_MESSAGE, 
                               DeliveryChannel.APP_NOTIFICATION,
                               DeliveryChannel.PUSH_NOTIFICATION]:
                    # Execute via registered callbacks
                    callbacks = self.delivery_callbacks.get(event.user_id, [])
                    for callback in callbacks:
                        try:
                            result = await callback({
                                "type": "agency_event",
                                "event_type": event.event_type.value,
                                "content": event.content,
                                "priority": event.priority,
                                "delivery_channel": channel.value,
                                "source_system": event.source_system,
                                "metadata": event.metadata
                            })
                            if result:
                                success = True
                        except Exception as e:
                            logger.error(f"❌ Agency event callback error: {e}")
            
            # Mark as executed
            event.executed = True
            event.execution_time = datetime.now()
            
            # Update user stats
            if event.user_id in self.active_users:
                self.active_users[event.user_id]["agency_events_count"] += 1
                self.active_users[event.user_id]["last_interaction"] = datetime.now()
            
            logger.info(f"🎭 Executed agency event {event.event_id} with success: {success}")
            
        except Exception as e:
            logger.error(f"❌ Failed to execute agency event: {e}")
    
    def _map_event_to_sms_type(self, event: AgencyEvent) -> SMSType:
        """Map agency event to SMS type"""
        try:
            if event.event_type == AgencyEventType.EMOTIONAL_INTERVENTION:
                return SMSType.EMOTIONAL_SUPPORT
            elif event.event_type == AgencyEventType.SCHEDULED_INTERACTION:
                trigger = event.metadata.get("schedule_type")
                if trigger == "daily_greeting":
                    return SMSType.DAILY_GREETING
                else:
                    return SMSType.PROACTIVE_CHECKIN
            else:
                return SMSType.CARING_MESSAGE
                
        except Exception as e:
            logger.error(f"❌ Failed to map event to SMS type: {e}")
            return SMSType.PROACTIVE_CHECKIN
    
    # Subsystem event handlers
    async def _handle_proactive_trigger(self, trigger_event: TriggerEvent) -> bool:
        """Handle proactive trigger event"""
        try:
            # Convert to agency event and queue
            agency_event = await self._convert_trigger_to_agency_event(trigger_event)
            if agency_event:
                self.event_queue.append(agency_event)
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to handle proactive trigger: {e}")
            return False
    
    async def _handle_scheduled_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """Handle scheduled interaction event"""
        try:
            user_id = interaction_data.get("user_id")
            content = interaction_data.get("content")
            schedule_type = interaction_data.get("schedule_type")
            
            if not user_id or not content:
                return False
            
            # Create agency event
            event_id = f"scheduled_{user_id}_{datetime.now().isoformat()}"
            
            agency_event = AgencyEvent(
                event_id=event_id,
                user_id=user_id,
                event_type=AgencyEventType.SCHEDULED_INTERACTION,
                content=content,
                priority="medium",
                delivery_channels=[DeliveryChannel.IN_APP_MESSAGE, DeliveryChannel.APP_NOTIFICATION],
                scheduled_time=datetime.now(),
                source_system="scheduled_interactions",
                metadata={
                    "schedule_type": schedule_type,
                    "interaction_data": interaction_data
                }
            )
            
            self.event_queue.append(agency_event)
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to handle scheduled interaction: {e}")
            return False
    
    async def _handle_emotional_intervention(self, intervention_data: Dict[str, Any]) -> bool:
        """Handle emotional intervention event"""
        try:
            user_id = intervention_data.get("user_id")
            content = intervention_data.get("content")
            urgency = intervention_data.get("urgency", "medium")
            
            if not user_id or not content:
                return False
            
            # Create agency event
            event_id = f"emotional_{user_id}_{datetime.now().isoformat()}"
            
            # Map urgency to priority
            priority_map = {
                "low": "low",
                "medium": "medium", 
                "high": "high",
                "critical": "urgent"
            }
            
            agency_event = AgencyEvent(
                event_id=event_id,
                user_id=user_id,
                event_type=AgencyEventType.EMOTIONAL_INTERVENTION,
                content=content,
                priority=priority_map.get(urgency, "medium"),
                delivery_channels=await self._determine_delivery_channels(user_id, urgency, "app_notification"),
                scheduled_time=datetime.now(),
                source_system="emotional_prompts",
                metadata={
                    "urgency": urgency,
                    "trigger": intervention_data.get("trigger"),
                    "intervention_type": intervention_data.get("intervention_type")
                }
            )
            
            self.event_queue.append(agency_event)
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to handle emotional intervention: {e}")
            return False
    
    # Public interface methods
    def register_delivery_callback(self, user_id: str, callback: Callable):
        """Register callback for agency event delivery"""
        if user_id not in self.delivery_callbacks:
            self.delivery_callbacks[user_id] = []
        self.delivery_callbacks[user_id].append(callback)
    
    async def record_user_interaction(
        self, 
        user_id: str, 
        interaction_type: str,
        emotional_data: Optional[Dict[str, Any]] = None
    ):
        """Record user interaction and emotional data"""
        try:
            # Update user activity
            if user_id in self.active_users:
                self.active_users[user_id]["last_interaction"] = datetime.now()
            
            # Record emotional data if provided
            if emotional_data:
                emotion_type = emotional_data.get("emotion_type", "neutral")
                intensity = emotional_data.get("intensity", 0.5)
                context = emotional_data.get("context", {})
                
                await emotional_prompts.record_emotional_data(
                    user_id=user_id,
                    emotion_type=emotion_type,
                    intensity=intensity,
                    context=context
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to record user interaction: {e}")
    
    async def get_user_agency_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get agency status for user"""
        try:
            if user_id not in self.active_users:
                return None
            
            user_data = self.active_users[user_id]
            
            # Get pending events
            pending_events = [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "priority": event.priority,
                    "scheduled_time": event.scheduled_time.isoformat(),
                    "source_system": event.source_system
                }
                for event in self.event_queue
                if event.user_id == user_id and not event.executed
            ]
            
            return {
                "user_id": user_id,
                "session_id": user_data["session_id"],
                "agency_active": True,
                "start_time": user_data["start_time"].isoformat(),
                "last_interaction": user_data["last_interaction"].isoformat(),
                "events_delivered": user_data["agency_events_count"],
                "pending_events": pending_events,
                "subsystem_status": {
                    "proactive_triggers": "active",
                    "emotional_prompts": "active",
                    "scheduled_interactions": "active",
                    "sms_integration": "active" if sms_integration.enabled else "disabled"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get user agency status: {e}")
            return None
    
    async def stop_user_agency(self, user_id: str):
        """Stop narrative agency for a user"""
        try:
            # Remove from active users
            if user_id in self.active_users:
                del self.active_users[user_id]
            
            # Clean up callbacks
            if user_id in self.delivery_callbacks:
                del self.delivery_callbacks[user_id]
            
            # Remove pending events
            self.event_queue = [
                event for event in self.event_queue
                if event.user_id != user_id or event.executed
            ]
            
            logger.info(f"🎭 Stopped narrative agency for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop user agency: {e}")
    
    async def stop_orchestrator(self):
        """Stop the orchestrator"""
        try:
            self.running = False
            
            if self.orchestrator_task:
                self.orchestrator_task.cancel()
                try:
                    await self.orchestrator_task
                except asyncio.CancelledError:
                    pass
            
            await scheduled_interactions.stop_scheduler()
            
            logger.info("🎭 Narrative agency orchestrator stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop orchestrator: {e}")

# Global instance
narrative_agency = NarrativeAgencyOrchestrator()

__all__ = ["narrative_agency", "AgencyEventType", "DeliveryChannel"]
