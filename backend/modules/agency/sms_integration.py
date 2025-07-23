"""
SMS Integration
Real-world messaging integration via Twilio for proactive character interactions
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import sqlite3
import os

logger = logging.getLogger(__name__)

class SMSStatus(Enum):
    """SMS delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"

class SMSType(Enum):
    """Types of SMS messages"""
    PROACTIVE_CHECKIN = "proactive_checkin"
    EMOTIONAL_SUPPORT = "emotional_support"
    DAILY_GREETING = "daily_greeting"
    MEMORY_SHARE = "memory_share"
    CARING_MESSAGE = "caring_message"
    EMERGENCY_RESPONSE = "emergency_response"

@dataclass
class SMSMessage:
    """SMS message data"""
    message_id: str
    user_id: str
    phone_number: str
    content: str
    sms_type: SMSType
    priority: str
    scheduled_time: datetime
    status: SMSStatus
    twilio_sid: Optional[str] = None
    delivery_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class SMSIntegration:
    """
    SMS integration system for proactive character interactions
    """
    
    def __init__(self, db_path: str = "sms_integration.db"):
        self.db_path = db_path
        self.twilio_client = None
        self.from_number = None
        self.enabled = False
        self.message_queue: List[SMSMessage] = []
        self.rate_limits = {
            "per_minute": 5,
            "per_hour": 20,
            "per_day": 50
        }
        self._setup_twilio()
    
    def _setup_twilio(self):
        """Setup Twilio client if credentials are available"""
        try:
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            self.from_number = os.getenv('TWILIO_FROM_NUMBER')
            
            if account_sid and auth_token and self.from_number:
                try:
                    from twilio.rest import Client
                    self.twilio_client = Client(account_sid, auth_token)
                    self.enabled = True
                    logger.info("📱 Twilio SMS integration enabled")
                except ImportError:
                    logger.warning("📱 Twilio library not installed. SMS features disabled.")
                    self.enabled = False
            else:
                logger.info("📱 Twilio credentials not configured. SMS features disabled.")
                self.enabled = False
                
        except Exception as e:
            logger.error(f"❌ Failed to setup Twilio: {e}")
            self.enabled = False
    
    async def initialize(self):
        """Initialize SMS integration system"""
        try:
            # Create database tables
            conn = sqlite3.connect(self.db_path)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sms_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sms_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    scheduled_time DATETIME NOT NULL,
                    status TEXT NOT NULL,
                    twilio_sid TEXT,
                    delivery_time DATETIME,
                    metadata JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sms_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    phone_number TEXT,
                    enabled BOOLEAN DEFAULT FALSE,
                    allowed_types JSON,
                    quiet_hours_start TIME,
                    quiet_hours_end TIME,
                    timezone TEXT,
                    max_daily_messages INTEGER DEFAULT 3,
                    emergency_override BOOLEAN DEFAULT TRUE,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sms_delivery_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    twilio_response JSON,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES sms_messages (message_id)
                )
            """)
            
            conn.close()
            logger.info("📱 SMS Integration initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize SMS integration: {e}")
            raise
    
    async def send_proactive_sms(
        self, 
        user_id: str, 
        content: str,
        sms_type: SMSType = SMSType.PROACTIVE_CHECKIN,
        priority: str = "normal",
        schedule_time: Optional[datetime] = None
    ) -> Optional[str]:
        """Send proactive SMS to user"""
        try:
            if not self.enabled:
                logger.warning("📱 SMS not enabled, cannot send message")
                return None
            
            # Get user SMS preferences
            user_prefs = await self._get_user_sms_preferences(user_id)
            if not user_prefs or not user_prefs.get("enabled", False):
                logger.info(f"📱 SMS not enabled for user {user_id}")
                return None
            
            phone_number = user_prefs.get("phone_number")
            if not phone_number:
                logger.warning(f"📱 No phone number configured for user {user_id}")
                return None
            
            # Check rate limits
            if not await self._check_rate_limits(user_id, priority):
                logger.warning(f"📱 Rate limit exceeded for user {user_id}")
                return None
            
            # Check quiet hours
            if not await self._check_quiet_hours(user_id, priority):
                logger.info(f"📱 Message delayed due to quiet hours for user {user_id}")
                # Schedule for later
                schedule_time = await self._calculate_next_send_time(user_id)
            
            # Create SMS message
            message_id = f"sms_{user_id}_{datetime.now().isoformat()}"
            sms_message = SMSMessage(
                message_id=message_id,
                user_id=user_id,
                phone_number=phone_number,
                content=content,
                sms_type=sms_type,
                priority=priority,
                scheduled_time=schedule_time or datetime.now(),
                status=SMSStatus.PENDING,
                metadata={"generated_at": datetime.now().isoformat()}
            )
            
            # Store message
            await self._store_sms_message(sms_message)
            
            # Send immediately if not scheduled
            if not schedule_time or schedule_time <= datetime.now():
                return await self._send_sms_now(sms_message)
            else:
                # Add to queue for later
                self.message_queue.append(sms_message)
                logger.info(f"📱 SMS scheduled for {schedule_time} for user {user_id}")
                return message_id
            
        except Exception as e:
            logger.error(f"❌ Failed to send proactive SMS: {e}")
            return None
    
    async def _send_sms_now(self, sms_message: SMSMessage) -> Optional[str]:
        """Send SMS immediately via Twilio"""
        try:
            if not self.twilio_client:
                logger.error("📱 Twilio client not available")
                return None
            
            # Send via Twilio
            message = self.twilio_client.messages.create(
                body=sms_message.content,
                from_=self.from_number,
                to=sms_message.phone_number
            )
            
            # Update message with Twilio SID
            sms_message.twilio_sid = message.sid
            sms_message.status = SMSStatus.SENT
            sms_message.delivery_time = datetime.now()
            
            # Update in database
            await self._update_sms_status(sms_message)
            
            # Log delivery
            await self._log_sms_delivery(sms_message.message_id, SMSStatus.SENT, {
                "twilio_sid": message.sid,
                "status": message.status
            })
            
            logger.info(f"📱 SMS sent successfully to user {sms_message.user_id}")
            return sms_message.message_id
            
        except Exception as e:
            logger.error(f"❌ Failed to send SMS: {e}")
            
            # Update status to failed
            sms_message.status = SMSStatus.FAILED
            await self._update_sms_status(sms_message)
            
            return None
    
    async def _get_user_sms_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user SMS preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT phone_number, enabled, allowed_types, quiet_hours_start, 
                       quiet_hours_end, timezone, max_daily_messages, emergency_override
                FROM sms_preferences 
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            phone, enabled, allowed_types, quiet_start, quiet_end, tz, max_daily, emergency = row
            
            return {
                "phone_number": phone,
                "enabled": bool(enabled),
                "allowed_types": json.loads(allowed_types) if allowed_types else [],
                "quiet_hours_start": quiet_start,
                "quiet_hours_end": quiet_end,
                "timezone": tz,
                "max_daily_messages": max_daily or 3,
                "emergency_override": bool(emergency)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get user SMS preferences: {e}")
            return None
    
    async def _check_rate_limits(self, user_id: str, priority: str) -> bool:
        """Check if user has exceeded SMS rate limits"""
        try:
            now = datetime.now()
            
            # Emergency messages bypass rate limits
            if priority == "emergency":
                return True
            
            # Check daily limit
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_count = await self._get_message_count_since(user_id, day_start)
            
            user_prefs = await self._get_user_sms_preferences(user_id)
            max_daily = user_prefs.get("max_daily_messages", 3) if user_prefs else 3
            
            if daily_count >= max_daily:
                return False
            
            # Check hourly limit (system-wide)
            hour_start = now.replace(minute=0, second=0, microsecond=0)
            hourly_count = await self._get_message_count_since(user_id, hour_start)
            
            if hourly_count >= self.rate_limits["per_hour"]:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check rate limits: {e}")
            return False
    
    async def _check_quiet_hours(self, user_id: str, priority: str) -> bool:
        """Check if current time is within user's quiet hours"""
        try:
            # Emergency messages bypass quiet hours
            if priority == "emergency":
                return True
            
            user_prefs = await self._get_user_sms_preferences(user_id)
            if not user_prefs:
                return True
            
            quiet_start = user_prefs.get("quiet_hours_start")
            quiet_end = user_prefs.get("quiet_hours_end")
            
            if not quiet_start or not quiet_end:
                return True  # No quiet hours set
            
            current_time = datetime.now().time()
            
            # Parse time strings
            from datetime import time
            start_time = time.fromisoformat(quiet_start)
            end_time = time.fromisoformat(quiet_end)
            
            # Check if current time is in quiet hours
            if start_time <= end_time:
                # Same day quiet hours
                return not (start_time <= current_time <= end_time)
            else:
                # Overnight quiet hours
                return not (current_time >= start_time or current_time <= end_time)
            
        except Exception as e:
            logger.error(f"❌ Failed to check quiet hours: {e}")
            return True
    
    async def _calculate_next_send_time(self, user_id: str) -> datetime:
        """Calculate next appropriate send time considering quiet hours"""
        try:
            user_prefs = await self._get_user_sms_preferences(user_id)
            if not user_prefs:
                # Default: wait 30 minutes
                return datetime.now() + timedelta(minutes=30)
            
            quiet_end = user_prefs.get("quiet_hours_end")
            if not quiet_end:
                return datetime.now() + timedelta(minutes=30)
            
            # Schedule for end of quiet hours
            from datetime import time
            end_time = time.fromisoformat(quiet_end)
            
            tomorrow = datetime.now().replace(hour=end_time.hour, minute=end_time.minute, 
                                            second=0, microsecond=0)
            
            if tomorrow <= datetime.now():
                tomorrow += timedelta(days=1)
            
            return tomorrow
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate next send time: {e}")
            return datetime.now() + timedelta(minutes=30)
    
    async def _get_message_count_since(self, user_id: str, since_time: datetime) -> int:
        """Get count of messages sent to user since given time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT COUNT(*) 
                FROM sms_messages 
                WHERE user_id = ? AND delivery_time >= ? AND status IN ('sent', 'delivered')
            """, (user_id, since_time.isoformat()))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"❌ Failed to get message count: {e}")
            return 0
    
    async def _store_sms_message(self, sms_message: SMSMessage):
        """Store SMS message in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO sms_messages 
                (message_id, user_id, phone_number, content, sms_type, priority, 
                 scheduled_time, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sms_message.message_id,
                sms_message.user_id,
                sms_message.phone_number,
                sms_message.content,
                sms_message.sms_type.value,
                sms_message.priority,
                sms_message.scheduled_time.isoformat(),
                sms_message.status.value,
                json.dumps(sms_message.metadata) if sms_message.metadata else None
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to store SMS message: {e}")
    
    async def _update_sms_status(self, sms_message: SMSMessage):
        """Update SMS message status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                UPDATE sms_messages 
                SET status = ?, twilio_sid = ?, delivery_time = ?
                WHERE message_id = ?
            """, (
                sms_message.status.value,
                sms_message.twilio_sid,
                sms_message.delivery_time.isoformat() if sms_message.delivery_time else None,
                sms_message.message_id
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to update SMS status: {e}")
    
    async def _log_sms_delivery(self, message_id: str, status: SMSStatus, twilio_response: Dict[str, Any]):
        """Log SMS delivery attempt"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO sms_delivery_log (message_id, status, twilio_response)
                VALUES (?, ?, ?)
            """, (message_id, status.value, json.dumps(twilio_response)))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to log SMS delivery: {e}")
    
    async def set_user_sms_preferences(
        self, 
        user_id: str,
        phone_number: str,
        enabled: bool = True,
        allowed_types: Optional[List[str]] = None,
        quiet_hours_start: Optional[str] = None,
        quiet_hours_end: Optional[str] = None,
        max_daily_messages: int = 3
    ):
        """Set user SMS preferences"""
        try:
            if allowed_types is None:
                allowed_types = [sms_type.value for sms_type in SMSType]
            
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT OR REPLACE INTO sms_preferences 
                (user_id, phone_number, enabled, allowed_types, quiet_hours_start, 
                 quiet_hours_end, max_daily_messages)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                phone_number,
                enabled,
                json.dumps(allowed_types),
                quiet_hours_start,
                quiet_hours_end,
                max_daily_messages
            ))
            conn.commit()
            conn.close()
            
            logger.info(f"📱 Updated SMS preferences for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to set user SMS preferences: {e}")
    
    async def process_scheduled_messages(self):
        """Process any scheduled SMS messages that are ready to send"""
        try:
            current_time = datetime.now()
            ready_messages = [
                msg for msg in self.message_queue 
                if msg.scheduled_time <= current_time
            ]
            
            for message in ready_messages:
                await self._send_sms_now(message)
                self.message_queue.remove(message)
            
            # Also check database for any scheduled messages
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT message_id, user_id, phone_number, content, sms_type, priority, scheduled_time, metadata
                FROM sms_messages 
                WHERE status = 'pending' AND scheduled_time <= ?
            """, (current_time.isoformat(),))
            
            for row in cursor.fetchall():
                msg_id, user_id, phone, content, sms_type, priority, sched_time, metadata = row
                
                sms_message = SMSMessage(
                    message_id=msg_id,
                    user_id=user_id,
                    phone_number=phone,
                    content=content,
                    sms_type=SMSType(sms_type),
                    priority=priority,
                    scheduled_time=datetime.fromisoformat(sched_time),
                    status=SMSStatus.PENDING,
                    metadata=json.loads(metadata) if metadata else None
                )
                
                await self._send_sms_now(sms_message)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to process scheduled messages: {e}")
    
    async def get_sms_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get SMS history for user"""
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT message_id, content, sms_type, priority, scheduled_time, 
                       status, delivery_time, created_at
                FROM sms_messages 
                WHERE user_id = ? AND created_at >= ?
                ORDER BY created_at DESC
            """, (user_id, since_date.isoformat()))
            
            history = []
            for row in cursor.fetchall():
                msg_id, content, sms_type, priority, sched_time, status, delivery_time, created_at = row
                
                history.append({
                    "message_id": msg_id,
                    "content": content,
                    "sms_type": sms_type,
                    "priority": priority,
                    "scheduled_time": sched_time,
                    "status": status,
                    "delivery_time": delivery_time,
                    "created_at": created_at
                })
            
            conn.close()
            return history
            
        except Exception as e:
            logger.error(f"❌ Failed to get SMS history: {e}")
            return []

# Global instance
sms_integration = SMSIntegration()

__all__ = ["sms_integration", "SMSType", "SMSStatus", "SMSMessage"]
