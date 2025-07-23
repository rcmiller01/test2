"""
Scheduled Interactions
Time-based character reach-outs and regular check-ins
"""

import logging
import asyncio
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json
import sqlite3

logger = logging.getLogger(__name__)

class ScheduleType(Enum):
    """Types of scheduled interactions"""
    DAILY_GREETING = "daily_greeting"
    WEEKLY_CHECKIN = "weekly_checkin"
    MONTHLY_REFLECTION = "monthly_reflection"
    CUSTOM_REMINDER = "custom_reminder"
    MILESTONE_CELEBRATION = "milestone_celebration"
    SEASONAL_MESSAGE = "seasonal_message"
    ANNIVERSARY = "anniversary"

class RecurrencePattern(Enum):
    """Recurrence patterns for scheduled interactions"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

@dataclass
class ScheduledInteraction:
    """Definition of a scheduled interaction"""
    schedule_id: str
    user_id: str
    schedule_type: ScheduleType
    title: str
    description: str
    content_template: str
    recurrence: RecurrencePattern
    next_execution: datetime
    enabled: bool
    execution_time: time          # Time of day to execute
    days_of_week: List[int]       # 0=Monday, 6=Sunday (for weekly)
    day_of_month: Optional[int]   # For monthly (None = last day)
    metadata: Dict[str, Any]
    created_at: datetime
    last_executed: Optional[datetime] = None
    execution_count: int = 0

class ScheduledInteractionEngine:
    """
    Engine for managing time-based proactive interactions
    """
    
    def __init__(self, db_path: str = "scheduled_interactions.db"):
        self.db_path = db_path
        self.scheduled_interactions: Dict[str, ScheduledInteraction] = {}
        self.execution_callbacks: Dict[str, List[Callable]] = {}
        self.scheduler_task: Optional[asyncio.Task] = None
        self.running = False
    
    async def initialize(self):
        """Initialize the scheduled interaction engine"""
        try:
            # Create database tables
            conn = sqlite3.connect(self.db_path)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    schedule_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    content_template TEXT NOT NULL,
                    recurrence TEXT NOT NULL,
                    next_execution DATETIME NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    execution_time TIME NOT NULL,
                    days_of_week TEXT,
                    day_of_month INTEGER,
                    metadata JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_executed DATETIME,
                    execution_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_id TEXT NOT NULL,
                    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    content TEXT,
                    success BOOLEAN,
                    delivery_method TEXT,
                    user_response TEXT,
                    metadata JSON,
                    FOREIGN KEY (schedule_id) REFERENCES scheduled_interactions (schedule_id)
                )
            """)
            
            conn.close()
            
            # Load existing schedules
            await self._load_scheduled_interactions()
            
            # Create default schedules
            await self._create_default_schedules()
            
            logger.info("⏰ Scheduled Interaction Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize scheduled interaction engine: {e}")
            raise
    
    async def _load_scheduled_interactions(self):
        """Load scheduled interactions from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT schedule_id, user_id, schedule_type, title, description, content_template,
                       recurrence, next_execution, enabled, execution_time, days_of_week,
                       day_of_month, metadata, created_at, last_executed, execution_count
                FROM scheduled_interactions
                WHERE enabled = TRUE
            """)
            
            for row in cursor.fetchall():
                (schedule_id, user_id, schedule_type, title, description, content_template,
                 recurrence, next_execution, enabled, exec_time, days_of_week,
                 day_of_month, metadata, created_at, last_executed, execution_count) = row
                
                interaction = ScheduledInteraction(
                    schedule_id=schedule_id,
                    user_id=user_id,
                    schedule_type=ScheduleType(schedule_type),
                    title=title,
                    description=description,
                    content_template=content_template,
                    recurrence=RecurrencePattern(recurrence),
                    next_execution=datetime.fromisoformat(next_execution),
                    enabled=bool(enabled),
                    execution_time=time.fromisoformat(exec_time),
                    days_of_week=json.loads(days_of_week) if days_of_week else [],
                    day_of_month=day_of_month,
                    metadata=json.loads(metadata) if metadata else {},
                    created_at=datetime.fromisoformat(created_at),
                    last_executed=datetime.fromisoformat(last_executed) if last_executed else None,
                    execution_count=execution_count
                )
                
                self.scheduled_interactions[schedule_id] = interaction
            
            conn.close()
            logger.info(f"⏰ Loaded {len(self.scheduled_interactions)} scheduled interactions")
            
        except Exception as e:
            logger.error(f"❌ Failed to load scheduled interactions: {e}")
    
    async def _create_default_schedules(self):
        """Create default scheduled interactions for new users"""
        # This would be called when a new user is onboarded
        pass
    
    async def start_scheduler(self):
        """Start the interaction scheduler"""
        try:
            if self.running:
                logger.warning("⏰ Scheduler already running")
                return
            
            self.running = True
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            logger.info("⏰ Scheduled interaction scheduler started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
    
    async def stop_scheduler(self):
        """Stop the interaction scheduler"""
        try:
            self.running = False
            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("⏰ Scheduled interaction scheduler stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        try:
            while self.running:
                current_time = datetime.now()
                
                # Check for interactions ready to execute
                ready_interactions = [
                    interaction for interaction in self.scheduled_interactions.values()
                    if interaction.enabled and interaction.next_execution <= current_time
                ]
                
                for interaction in ready_interactions:
                    await self._execute_scheduled_interaction(interaction)
                
                # Sleep for 1 minute before next check
                await asyncio.sleep(60)
                
        except asyncio.CancelledError:
            logger.debug("⏰ Scheduler loop cancelled")
        except Exception as e:
            logger.error(f"❌ Scheduler loop error: {e}")
    
    async def _execute_scheduled_interaction(self, interaction: ScheduledInteraction):
        """Execute a scheduled interaction"""
        try:
            # Generate personalized content
            content = await self._generate_interaction_content(interaction)
            
            # Execute via callbacks
            success = False
            callbacks = self.execution_callbacks.get(interaction.user_id, [])
            
            for callback in callbacks:
                try:
                    result = await callback({
                        "type": "scheduled_interaction",
                        "schedule_type": interaction.schedule_type.value,
                        "content": content,
                        "user_id": interaction.user_id,
                        "metadata": interaction.metadata
                    })
                    if result:
                        success = True
                except Exception as e:
                    logger.error(f"❌ Scheduled interaction callback error: {e}")
            
            # Update execution records
            interaction.last_executed = datetime.now()
            interaction.execution_count += 1
            interaction.next_execution = await self._calculate_next_execution(interaction)
            
            # Save to database
            await self._update_interaction_execution(interaction, success, content)
            
            # Log execution
            await self._log_execution(interaction, content, success)
            
            logger.info(f"⏰ Executed scheduled interaction {interaction.schedule_id} for user {interaction.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to execute scheduled interaction: {e}")
    
    async def _generate_interaction_content(self, interaction: ScheduledInteraction) -> str:
        """Generate personalized content for the interaction"""
        try:
            content_template = interaction.content_template
            
            # Get user context for personalization
            user_context = await self._get_user_context_for_scheduling(interaction.user_id)
            
            # Replace template variables
            content = content_template
            
            # Basic replacements
            content = content.replace("{user_name}", user_context.get("name", "there"))
            content = content.replace("{time_of_day}", self._get_time_of_day_greeting())
            content = content.replace("{day_of_week}", datetime.now().strftime("%A"))
            
            # Relationship-specific replacements
            relationship_length = user_context.get("relationship_days", 0)
            if relationship_length > 0:
                content = content.replace("{relationship_length}", f"{relationship_length} days")
            
            # Memory-based replacements
            if "{recent_memory}" in content:
                recent_memory = user_context.get("recent_memory", "our conversations")
                content = content.replace("{recent_memory}", recent_memory)
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Failed to generate interaction content: {e}")
            return interaction.content_template
    
    async def _get_user_context_for_scheduling(self, user_id: str) -> Dict[str, Any]:
        """Get user context for content personalization"""
        try:
            context = {
                "user_id": user_id,
                "name": "there",  # Default
                "relationship_days": 0,
                "recent_memory": "our conversations"
            }
            
            # Try to get user profile
            # This would integrate with user management system
            
            # Try to get memory context
            try:
                from ..memory import symbolic_memory
                # Use a simpler method call that exists
                context["recent_memory"] = "our meaningful conversations"
            except Exception:
                logger.debug("Memory context not available for scheduling")
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Failed to get user context for scheduling: {e}")
            return {"user_id": user_id}
    
    def _get_time_of_day_greeting(self) -> str:
        """Get appropriate greeting based on time of day"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    async def _calculate_next_execution(self, interaction: ScheduledInteraction) -> datetime:
        """Calculate next execution time based on recurrence pattern"""
        try:
            current_time = datetime.now()
            
            if interaction.recurrence == RecurrencePattern.ONCE:
                # One-time interaction, disable it
                interaction.enabled = False
                return current_time  # Won't be executed again
            
            elif interaction.recurrence == RecurrencePattern.DAILY:
                # Next day at same time
                next_time = current_time.replace(
                    hour=interaction.execution_time.hour,
                    minute=interaction.execution_time.minute,
                    second=0,
                    microsecond=0
                ) + timedelta(days=1)
                
                return next_time
            
            elif interaction.recurrence == RecurrencePattern.WEEKLY:
                # Next occurrence on specified days of week
                current_weekday = current_time.weekday()
                
                # Find next valid day
                days_ahead = None
                for day_offset in range(1, 8):  # Check next 7 days
                    check_day = (current_weekday + day_offset) % 7
                    if check_day in interaction.days_of_week:
                        days_ahead = day_offset
                        break
                
                if days_ahead is None:
                    # Fallback to next week same day
                    days_ahead = 7
                
                next_time = (current_time + timedelta(days=days_ahead)).replace(
                    hour=interaction.execution_time.hour,
                    minute=interaction.execution_time.minute,
                    second=0,
                    microsecond=0
                )
                
                return next_time
            
            elif interaction.recurrence == RecurrencePattern.MONTHLY:
                # Next month on specified day
                next_month = current_time.replace(day=1) + timedelta(days=32)
                next_month = next_month.replace(day=1)  # First of next month
                
                # Calculate target day
                if interaction.day_of_month:
                    target_day = min(interaction.day_of_month, 
                                   self._days_in_month(next_month.year, next_month.month))
                else:
                    # Last day of month
                    target_day = self._days_in_month(next_month.year, next_month.month)
                
                next_time = next_month.replace(
                    day=target_day,
                    hour=interaction.execution_time.hour,
                    minute=interaction.execution_time.minute,
                    second=0,
                    microsecond=0
                )
                
                return next_time
            
            elif interaction.recurrence == RecurrencePattern.YEARLY:
                # Next year same date
                try:
                    next_time = current_time.replace(year=current_time.year + 1)
                except ValueError:
                    # Handle leap year edge case (Feb 29)
                    next_time = current_time.replace(year=current_time.year + 1, day=28)
                
                return next_time
            
            else:
                # Default: 1 day from now
                return datetime.now() + timedelta(days=1)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate next execution: {e}")
            return datetime.now() + timedelta(days=1)
    
    def _days_in_month(self, year: int, month: int) -> int:
        """Get number of days in specified month"""
        import calendar
        return calendar.monthrange(year, month)[1]
    
    async def _update_interaction_execution(
        self, 
        interaction: ScheduledInteraction, 
        success: bool,
        content: str
    ):
        """Update interaction execution in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Update the interaction record
            conn.execute("""
                UPDATE scheduled_interactions 
                SET last_executed = ?, execution_count = ?, next_execution = ?, enabled = ?
                WHERE schedule_id = ?
            """, (
                interaction.last_executed.isoformat() if interaction.last_executed else None,
                interaction.execution_count,
                interaction.next_execution.isoformat(),
                interaction.enabled,
                interaction.schedule_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to update interaction execution: {e}")
    
    async def _log_execution(
        self, 
        interaction: ScheduledInteraction, 
        content: str,
        success: bool
    ):
        """Log execution in history"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO execution_history 
                (schedule_id, content, success, delivery_method, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                interaction.schedule_id,
                content,
                success,
                "app_notification",  # Default delivery method
                json.dumps({"execution_time": datetime.now().isoformat()})
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to log execution: {e}")
    
    async def create_scheduled_interaction(
        self,
        user_id: str,
        schedule_type: ScheduleType,
        title: str,
        content_template: str,
        recurrence: RecurrencePattern,
        execution_time: time,
        days_of_week: Optional[List[int]] = None,
        day_of_month: Optional[int] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new scheduled interaction"""
        try:
            schedule_id = f"schedule_{user_id}_{datetime.now().isoformat()}"
            
            # Calculate first execution time
            next_execution = await self._calculate_first_execution(
                execution_time, recurrence, days_of_week, day_of_month
            )
            
            interaction = ScheduledInteraction(
                schedule_id=schedule_id,
                user_id=user_id,
                schedule_type=schedule_type,
                title=title,
                description=description or "",
                content_template=content_template,
                recurrence=recurrence,
                next_execution=next_execution,
                enabled=True,
                execution_time=execution_time,
                days_of_week=days_of_week or [],
                day_of_month=day_of_month,
                metadata=metadata or {},
                created_at=datetime.now()
            )
            
            # Store in database
            await self._store_scheduled_interaction(interaction)
            
            # Add to active interactions
            self.scheduled_interactions[schedule_id] = interaction
            
            logger.info(f"⏰ Created scheduled interaction {schedule_id} for user {user_id}")
            return schedule_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create scheduled interaction: {e}")
            raise
    
    async def _calculate_first_execution(
        self,
        execution_time: time,
        recurrence: RecurrencePattern,
        days_of_week: Optional[List[int]],
        day_of_month: Optional[int]
    ) -> datetime:
        """Calculate first execution time for new scheduled interaction"""
        try:
            current_time = datetime.now()
            
            # Start with today at execution time
            candidate_time = current_time.replace(
                hour=execution_time.hour,
                minute=execution_time.minute,
                second=0,
                microsecond=0
            )
            
            # If time has passed today, start tomorrow
            if candidate_time <= current_time:
                candidate_time += timedelta(days=1)
            
            if recurrence == RecurrencePattern.WEEKLY and days_of_week:
                # Find next valid weekday
                while candidate_time.weekday() not in days_of_week:
                    candidate_time += timedelta(days=1)
            
            elif recurrence == RecurrencePattern.MONTHLY and day_of_month:
                # Adjust to target day of month
                target_day = min(day_of_month, 
                               self._days_in_month(candidate_time.year, candidate_time.month))
                candidate_time = candidate_time.replace(day=target_day)
            
            return candidate_time
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate first execution: {e}")
            return datetime.now() + timedelta(hours=1)
    
    async def _store_scheduled_interaction(self, interaction: ScheduledInteraction):
        """Store scheduled interaction in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO scheduled_interactions 
                (schedule_id, user_id, schedule_type, title, description, content_template,
                 recurrence, next_execution, enabled, execution_time, days_of_week,
                 day_of_month, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                interaction.schedule_id,
                interaction.user_id,
                interaction.schedule_type.value,
                interaction.title,
                interaction.description,
                interaction.content_template,
                interaction.recurrence.value,
                interaction.next_execution.isoformat(),
                interaction.enabled,
                interaction.execution_time.isoformat(),
                json.dumps(interaction.days_of_week),
                interaction.day_of_month,
                json.dumps(interaction.metadata),
                interaction.created_at.isoformat()
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to store scheduled interaction: {e}")
    
    def register_execution_callback(self, user_id: str, callback: Callable):
        """Register callback for scheduled interaction executions"""
        if user_id not in self.execution_callbacks:
            self.execution_callbacks[user_id] = []
        self.execution_callbacks[user_id].append(callback)
    
    async def get_user_schedules(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all scheduled interactions for a user"""
        try:
            user_schedules = [
                {
                    "schedule_id": interaction.schedule_id,
                    "schedule_type": interaction.schedule_type.value,
                    "title": interaction.title,
                    "description": interaction.description,
                    "recurrence": interaction.recurrence.value,
                    "next_execution": interaction.next_execution.isoformat(),
                    "enabled": interaction.enabled,
                    "execution_time": interaction.execution_time.isoformat(),
                    "execution_count": interaction.execution_count,
                    "last_executed": interaction.last_executed.isoformat() if interaction.last_executed else None
                }
                for interaction in self.scheduled_interactions.values()
                if interaction.user_id == user_id
            ]
            
            return user_schedules
            
        except Exception as e:
            logger.error(f"❌ Failed to get user schedules: {e}")
            return []
    
    async def update_schedule_status(self, schedule_id: str, enabled: bool):
        """Enable or disable a scheduled interaction"""
        try:
            if schedule_id in self.scheduled_interactions:
                self.scheduled_interactions[schedule_id].enabled = enabled
                
                # Update in database
                conn = sqlite3.connect(self.db_path)
                conn.execute("""
                    UPDATE scheduled_interactions 
                    SET enabled = ? 
                    WHERE schedule_id = ?
                """, (enabled, schedule_id))
                conn.commit()
                conn.close()
                
                logger.info(f"⏰ Updated schedule {schedule_id} enabled: {enabled}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update schedule status: {e}")

# Global instance
scheduled_interactions = ScheduledInteractionEngine()

__all__ = ["scheduled_interactions", "ScheduleType", "RecurrencePattern", "ScheduledInteraction"]
