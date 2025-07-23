"""
Session Control System
Manages healthy usage patterns and prevents emotional overwhelm through session monitoring
"""

import logging
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class SessionRisk(Enum):
    """Session risk levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class InterventionType(Enum):
    """Types of session interventions"""
    GENTLE_REMINDER = "gentle_reminder"
    BREAK_SUGGESTION = "break_suggestion"
    MANDATORY_PAUSE = "mandatory_pause"
    COOLDOWN_PERIOD = "cooldown_period"
    PROFESSIONAL_REFERRAL = "professional_referral"

class UsagePattern(Enum):
    """Usage pattern types"""
    HEALTHY = "healthy"
    INTENSIVE = "intensive"
    CONCERNING = "concerning"
    DEPENDENT = "dependent"

@dataclass
class SessionMetrics:
    """Session tracking metrics"""
    user_id: str
    session_id: str
    start_time: datetime
    current_duration: float
    message_count: int
    emotional_intensity_avg: float
    emotional_intensity_peak: float
    topic_categories: List[str]
    risk_indicators: List[str]

@dataclass
class SessionIntervention:
    """Session intervention event"""
    user_id: str
    session_id: str
    intervention_type: InterventionType
    risk_level: SessionRisk
    trigger_reason: str
    action_taken: str
    user_response: Optional[str]
    timestamp: datetime

class SessionControlSystem:
    """
    Monitors and manages user sessions to promote healthy usage patterns
    and prevent emotional overwhelm or dependency
    """
    
    def __init__(self, db_path: str = "session_control.db"):
        self.db_path = db_path
        self.active_sessions: Dict[str, SessionMetrics] = {}
        self.session_limits = {}
        self.intervention_rules = {}
        self.healthy_patterns = {}
        self._initialize_rules()
    
    async def initialize(self):
        """Initialize session control system"""
        try:
            # Create database tables
            conn = sqlite3.connect(self.db_path)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    duration_minutes REAL,
                    message_count INTEGER,
                    emotional_intensity_avg REAL,
                    emotional_intensity_peak REAL,
                    topic_categories TEXT,
                    risk_indicators TEXT,
                    interventions_triggered INTEGER DEFAULT 0,
                    session_quality TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_interventions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    intervention_type TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    trigger_reason TEXT,
                    action_taken TEXT,
                    user_response TEXT,
                    effectiveness_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_session_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    max_session_duration INTEGER DEFAULT 120,
                    daily_session_limit INTEGER DEFAULT 4,
                    break_reminder_interval INTEGER DEFAULT 60,
                    intensity_threshold REAL DEFAULT 0.7,
                    intervention_enabled BOOLEAN DEFAULT 1,
                    custom_limits JSON,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    date DATE NOT NULL,
                    total_session_time REAL,
                    session_count INTEGER,
                    avg_session_quality REAL,
                    interventions_count INTEGER,
                    usage_pattern TEXT,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, date)
                )
            """)
            
            conn.close()
            logger.info("🕐 Session Control System initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize session control: {e}")
            raise
    
    def _initialize_rules(self):
        """Initialize session control rules and limits"""
        
        # Default session limits (in minutes)
        self.session_limits = {
            "max_session_duration": 120,        # 2 hours
            "suggested_session_duration": 60,   # 1 hour
            "break_reminder_interval": 45,      # 45 minutes
            "daily_session_limit": 6,           # 6 sessions per day
            "weekly_session_limit": 35,         # 35 sessions per week
            "cooldown_period": 30,              # 30 minutes between intensive sessions
        }
        
        # Risk assessment rules
        self.intervention_rules = {
            SessionRisk.LOW: {
                "duration_threshold": 60,
                "intensity_threshold": 0.5,
                "message_rate_threshold": 2.0,  # messages per minute
                "intervention": InterventionType.GENTLE_REMINDER
            },
            SessionRisk.MODERATE: {
                "duration_threshold": 90,
                "intensity_threshold": 0.7,
                "message_rate_threshold": 3.0,
                "intervention": InterventionType.BREAK_SUGGESTION
            },
            SessionRisk.HIGH: {
                "duration_threshold": 120,
                "intensity_threshold": 0.8,
                "message_rate_threshold": 4.0,
                "intervention": InterventionType.MANDATORY_PAUSE
            },
            SessionRisk.CRITICAL: {
                "duration_threshold": 180,
                "intensity_threshold": 0.9,
                "message_rate_threshold": 5.0,
                "intervention": InterventionType.COOLDOWN_PERIOD
            }
        }
        
        # Healthy usage patterns
        self.healthy_patterns = {
            "session_duration": (20, 60),       # 20-60 minutes ideal
            "daily_sessions": (1, 4),           # 1-4 sessions per day
            "emotional_intensity": (0.2, 0.6), # Moderate emotional engagement
            "break_between_sessions": 60,       # 1 hour minimum break
            "variety_topics": 3                 # At least 3 different topic areas
        }
    
    async def start_session(
        self, 
        user_id: str, 
        session_id: str,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> SessionMetrics:
        """Start tracking a new session"""
        try:
            # Check if user is in cooldown period
            if await self._check_cooldown_period(user_id):
                logger.warning(f"⏰ User {user_id} still in cooldown period")
                # Allow session but mark as concerning
            
            # Create session metrics
            session = SessionMetrics(
                user_id=user_id,
                session_id=session_id,
                start_time=datetime.now(),
                current_duration=0.0,
                message_count=0,
                emotional_intensity_avg=0.0,
                emotional_intensity_peak=0.0,
                topic_categories=[],
                risk_indicators=[]
            )
            
            self.active_sessions[session_id] = session
            
            # Schedule periodic checks
            asyncio.create_task(self._monitor_session(session_id))
            
            logger.info(f"📊 Started session tracking: {session_id} for user {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to start session: {e}")
            raise
    
    async def update_session(
        self,
        session_id: str,
        emotional_state: Dict[str, float],
        content_category: str,
        message_content: str
    ):
        """Update session metrics with new interaction"""
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"⚠️ Session {session_id} not found for update")
                return
            
            session = self.active_sessions[session_id]
            
            # Update duration
            session.current_duration = (datetime.now() - session.start_time).total_seconds() / 60
            
            # Update message count
            session.message_count += 1
            
            # Update emotional metrics
            current_intensity = max(emotional_state.values()) if emotional_state else 0
            session.emotional_intensity_peak = max(session.emotional_intensity_peak, current_intensity)
            
            # Calculate running average
            if session.message_count == 1:
                session.emotional_intensity_avg = current_intensity
            else:
                # Exponential moving average
                alpha = 0.3
                session.emotional_intensity_avg = (
                    alpha * current_intensity + 
                    (1 - alpha) * session.emotional_intensity_avg
                )
            
            # Update topic categories
            if content_category not in session.topic_categories:
                session.topic_categories.append(content_category)
            
            # Check for risk indicators
            await self._update_risk_indicators(session, emotional_state, message_content)
            
            # Assess if intervention needed
            await self._assess_intervention_need(session)
            
        except Exception as e:
            logger.error(f"❌ Failed to update session: {e}")
    
    async def end_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """End session tracking and generate summary"""
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"⚠️ Session {session_id} not found for ending")
                return None
            
            session = self.active_sessions[session_id]
            end_time = datetime.now()
            final_duration = (end_time - session.start_time).total_seconds() / 60
            
            # Calculate session quality
            session_quality = await self._calculate_session_quality(session)
            
            # Log session to database
            await self._log_session_completion(session, end_time, session_quality)
            
            # Update daily stats
            await self._update_daily_stats(session.user_id, final_duration, session_quality)
            
            # Generate session summary
            summary = {
                "session_id": session_id,
                "user_id": session.user_id,
                "duration_minutes": final_duration,
                "message_count": session.message_count,
                "emotional_intensity_avg": session.emotional_intensity_avg,
                "emotional_intensity_peak": session.emotional_intensity_peak,
                "topic_categories": session.topic_categories,
                "session_quality": session_quality,
                "risk_indicators": session.risk_indicators
            }
            
            # Clean up active session
            del self.active_sessions[session_id]
            
            logger.info(f"📊 Session ended: {session_id}, duration: {final_duration:.1f}min, quality: {session_quality}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to end session: {e}")
            return None
    
    async def _monitor_session(self, session_id: str):
        """Monitor session for interventions"""
        try:
            # Check every 5 minutes
            while session_id in self.active_sessions:
                await asyncio.sleep(300)  # 5 minutes
                
                if session_id in self.active_sessions:
                    session = self.active_sessions[session_id]
                    await self._assess_intervention_need(session)
                    
        except Exception as e:
            logger.error(f"❌ Session monitoring error: {e}")
    
    async def _update_risk_indicators(
        self, 
        session: SessionMetrics, 
        emotional_state: Dict[str, float],
        content: str
    ):
        """Update risk indicators for the session"""
        try:
            content_lower = content.lower()
            
            # Check for dependency language
            dependency_patterns = [
                "can't live without", "only thing that matters", "all i need",
                "nothing else", "forget everything", "only you understand"
            ]
            
            for pattern in dependency_patterns:
                if pattern in content_lower and "dependency_language" not in session.risk_indicators:
                    session.risk_indicators.append("dependency_language")
            
            # Check emotional intensity patterns
            if session.emotional_intensity_peak > 0.8 and "high_emotional_intensity" not in session.risk_indicators:
                session.risk_indicators.append("high_emotional_intensity")
            
            # Check session duration
            if session.current_duration > 120 and "extended_duration" not in session.risk_indicators:
                session.risk_indicators.append("extended_duration")
            
            # Check message frequency
            message_rate = session.message_count / max(session.current_duration, 1)
            if message_rate > 3.0 and "rapid_messaging" not in session.risk_indicators:
                session.risk_indicators.append("rapid_messaging")
            
        except Exception as e:
            logger.error(f"❌ Failed to update risk indicators: {e}")
    
    async def _assess_intervention_need(self, session: SessionMetrics) -> Optional[SessionIntervention]:
        """Assess if session intervention is needed"""
        try:
            # Determine risk level
            risk_level = await self._calculate_session_risk(session)
            
            # Check if intervention is warranted
            if risk_level == SessionRisk.LOW:
                return None
            
            # Get intervention rules for this risk level
            rules = self.intervention_rules.get(risk_level)
            if not rules:
                return None
            
            # Check user preferences
            intervention_enabled = await self._check_intervention_enabled(session.user_id)
            if not intervention_enabled and risk_level != SessionRisk.CRITICAL:
                return None
            
            # Create intervention
            intervention = await self._create_intervention(session, risk_level, rules)
            
            # Log intervention
            await self._log_intervention(intervention)
            
            return intervention
            
        except Exception as e:
            logger.error(f"❌ Failed to assess intervention need: {e}")
            return None
    
    async def _calculate_session_risk(self, session: SessionMetrics) -> SessionRisk:
        """Calculate current session risk level"""
        try:
            risk_score = 0
            
            # Duration risk
            if session.current_duration > 180:  # 3 hours
                risk_score += 4
            elif session.current_duration > 120:  # 2 hours
                risk_score += 3
            elif session.current_duration > 90:   # 1.5 hours
                risk_score += 2
            elif session.current_duration > 60:   # 1 hour
                risk_score += 1
            
            # Emotional intensity risk
            if session.emotional_intensity_peak > 0.9:
                risk_score += 4
            elif session.emotional_intensity_peak > 0.8:
                risk_score += 3
            elif session.emotional_intensity_peak > 0.7:
                risk_score += 2
            elif session.emotional_intensity_peak > 0.6:
                risk_score += 1
            
            # Message frequency risk
            message_rate = session.message_count / max(session.current_duration, 1)
            if message_rate > 5.0:
                risk_score += 3
            elif message_rate > 4.0:
                risk_score += 2
            elif message_rate > 3.0:
                risk_score += 1
            
            # Risk indicators
            risk_score += len(session.risk_indicators)
            
            # Convert to risk level
            if risk_score >= 10:
                return SessionRisk.CRITICAL
            elif risk_score >= 7:
                return SessionRisk.HIGH
            elif risk_score >= 4:
                return SessionRisk.MODERATE
            else:
                return SessionRisk.LOW
                
        except Exception as e:
            logger.error(f"❌ Failed to calculate session risk: {e}")
            return SessionRisk.LOW
    
    async def _create_intervention(
        self, 
        session: SessionMetrics, 
        risk_level: SessionRisk,
        rules: Dict[str, Any]
    ) -> SessionIntervention:
        """Create appropriate intervention for session"""
        
        intervention_type = rules["intervention"]
        
        # Determine trigger reason
        trigger_reasons = []
        if session.current_duration > rules["duration_threshold"]:
            trigger_reasons.append(f"session_duration_{session.current_duration:.0f}min")
        if session.emotional_intensity_peak > rules["intensity_threshold"]:
            trigger_reasons.append(f"emotional_intensity_{session.emotional_intensity_peak:.2f}")
        
        trigger_reason = "; ".join(trigger_reasons)
        
        # Determine action
        action_taken = await self._get_intervention_action(intervention_type, session)
        
        return SessionIntervention(
            user_id=session.user_id,
            session_id=session.session_id,
            intervention_type=intervention_type,
            risk_level=risk_level,
            trigger_reason=trigger_reason,
            action_taken=action_taken,
            user_response=None,
            timestamp=datetime.now()
        )
    
    async def _get_intervention_action(
        self, 
        intervention_type: InterventionType, 
        session: SessionMetrics
    ) -> str:
        """Get appropriate action message for intervention type"""
        
        actions = {
            InterventionType.GENTLE_REMINDER: 
                f"Gentle reminder: You've been chatting for {session.current_duration:.0f} minutes. How are you feeling?",
            
            InterventionType.BREAK_SUGGESTION:
                "I notice we've been talking for quite a while. Would you like to take a short break? Sometimes stepping away can be refreshing.",
            
            InterventionType.MANDATORY_PAUSE:
                "I care about your well-being. You've been engaging intensely for a long time. Let's take a 15-minute break to recharge.",
            
            InterventionType.COOLDOWN_PERIOD:
                "I'm concerned about the intensity of our interaction. Let's pause for 30 minutes to ensure you're taking care of yourself.",
            
            InterventionType.PROFESSIONAL_REFERRAL:
                "I notice you might benefit from additional support. Would you like some resources for professional counseling or support services?"
        }
        
        return actions.get(intervention_type, "Session intervention recommended")
    
    async def _check_cooldown_period(self, user_id: str) -> bool:
        """Check if user is still in mandatory cooldown period"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT timestamp FROM session_interventions 
                WHERE user_id = ? AND intervention_type IN ('cooldown_period', 'mandatory_pause')
                ORDER BY timestamp DESC LIMIT 1
            """, (user_id,))
            
            last_intervention = cursor.fetchone()
            conn.close()
            
            if last_intervention:
                last_time = datetime.fromisoformat(last_intervention[0])
                cooldown_end = last_time + timedelta(minutes=30)
                return datetime.now() < cooldown_end
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check cooldown period: {e}")
            return False
    
    async def _check_intervention_enabled(self, user_id: str) -> bool:
        """Check if user has interventions enabled"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT intervention_enabled FROM user_session_preferences 
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else True  # Default to enabled
            
        except Exception as e:
            logger.error(f"❌ Failed to check intervention settings: {e}")
            return True
    
    async def _calculate_session_quality(self, session: SessionMetrics) -> str:
        """Calculate overall session quality rating"""
        try:
            score = 0
            
            # Duration scoring (optimal 20-60 minutes)
            if 20 <= session.current_duration <= 60:
                score += 3
            elif 10 <= session.current_duration <= 90:
                score += 2
            elif session.current_duration <= 120:
                score += 1
            
            # Emotional balance scoring
            if 0.2 <= session.emotional_intensity_avg <= 0.6:
                score += 3
            elif 0.1 <= session.emotional_intensity_avg <= 0.8:
                score += 2
            elif session.emotional_intensity_avg <= 0.9:
                score += 1
            
            # Topic variety scoring
            if len(session.topic_categories) >= 3:
                score += 2
            elif len(session.topic_categories) >= 2:
                score += 1
            
            # Risk indicators penalty
            score -= len(session.risk_indicators)
            
            # Convert to quality rating
            if score >= 7:
                return "excellent"
            elif score >= 5:
                return "good"
            elif score >= 3:
                return "fair"
            else:
                return "concerning"
                
        except Exception as e:
            logger.error(f"❌ Failed to calculate session quality: {e}")
            return "unknown"
    
    async def _log_session_completion(
        self, 
        session: SessionMetrics, 
        end_time: datetime, 
        quality: str
    ):
        """Log completed session to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO session_logs 
                (user_id, session_id, start_time, end_time, duration_minutes, 
                 message_count, emotional_intensity_avg, emotional_intensity_peak,
                 topic_categories, risk_indicators, session_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.user_id,
                session.session_id,
                session.start_time.isoformat(),
                end_time.isoformat(),
                session.current_duration,
                session.message_count,
                session.emotional_intensity_avg,
                session.emotional_intensity_peak,
                json.dumps(session.topic_categories),
                json.dumps(session.risk_indicators),
                quality
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to log session completion: {e}")
    
    async def _log_intervention(self, intervention: SessionIntervention):
        """Log intervention to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO session_interventions 
                (user_id, session_id, intervention_type, risk_level, 
                 trigger_reason, action_taken, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                intervention.user_id,
                intervention.session_id,
                intervention.intervention_type.value,
                intervention.risk_level.value,
                intervention.trigger_reason,
                intervention.action_taken,
                intervention.timestamp.isoformat()
            ))
            conn.commit()
            conn.close()
            
            logger.info(f"🚨 Intervention logged: {intervention.intervention_type.value} for session {intervention.session_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log intervention: {e}")
    
    async def _update_daily_stats(self, user_id: str, session_duration: float, quality: str):
        """Update daily usage statistics"""
        try:
            today = datetime.now().date()
            
            conn = sqlite3.connect(self.db_path)
            
            # Get existing stats for today
            cursor = conn.execute("""
                SELECT total_session_time, session_count, avg_session_quality 
                FROM daily_usage_stats WHERE user_id = ? AND date = ?
            """, (user_id, today.isoformat()))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                new_total_time = existing[0] + session_duration
                new_session_count = existing[1] + 1
                
                # Update average quality (simplified)
                quality_scores = {"excellent": 4, "good": 3, "fair": 2, "concerning": 1}
                current_quality_score = quality_scores.get(quality, 2)
                new_avg_quality = (existing[2] * existing[1] + current_quality_score) / new_session_count
                
                conn.execute("""
                    UPDATE daily_usage_stats 
                    SET total_session_time = ?, session_count = ?, avg_session_quality = ?
                    WHERE user_id = ? AND date = ?
                """, (new_total_time, new_session_count, new_avg_quality, user_id, today.isoformat()))
            else:
                # Create new record
                quality_scores = {"excellent": 4, "good": 3, "fair": 2, "concerning": 1}
                quality_score = quality_scores.get(quality, 2)
                
                conn.execute("""
                    INSERT INTO daily_usage_stats 
                    (user_id, date, total_session_time, session_count, avg_session_quality)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, today.isoformat(), session_duration, 1, quality_score))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to update daily stats: {e}")
    
    async def get_session_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get session statistics for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get recent session metrics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    AVG(duration_minutes) as avg_duration,
                    AVG(emotional_intensity_avg) as avg_emotional_intensity,
                    COUNT(CASE WHEN session_quality = 'concerning' THEN 1 END) as concerning_sessions
                FROM session_logs 
                WHERE user_id = ? AND start_time > datetime('now', '-7 days')
            """, (user_id,))
            
            session_stats = cursor.fetchone()
            
            # Get intervention count
            cursor = conn.execute("""
                SELECT COUNT(*) FROM session_interventions 
                WHERE user_id = ? AND timestamp > datetime('now', '-7 days')
            """, (user_id,))
            
            intervention_count = cursor.fetchone()[0]
            
            # Get current session if active
            active_session = None
            for session_id, session in self.active_sessions.items():
                if session.user_id == user_id:
                    active_session = {
                        "session_id": session_id,
                        "duration_minutes": session.current_duration,
                        "message_count": session.message_count,
                        "risk_indicators": session.risk_indicators
                    }
                    break
            
            conn.close()
            
            return {
                "total_sessions_7d": session_stats[0] or 0,
                "avg_session_duration": round(session_stats[1] or 0, 1),
                "avg_emotional_intensity": round(session_stats[2] or 0, 2),
                "concerning_sessions": session_stats[3] or 0,
                "interventions_7d": intervention_count,
                "active_session": active_session
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get session statistics: {e}")
            return {}

# Global instance
session_control = SessionControlSystem()

__all__ = ["session_control", "SessionRisk", "InterventionType", "UsagePattern"]
