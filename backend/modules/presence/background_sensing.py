"""
Background Sensing System
Passive presence detection through ambient signals and system metrics
"""

import logging
import asyncio
import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class SensorType(Enum):
    """Types of background sensors"""
    SYSTEM_ACTIVITY = "system_activity"     # CPU, memory, network usage
    BROWSER_SIGNALS = "browser_signals"     # Tab focus, window state
    AUDIO_ACTIVITY = "audio_activity"       # Microphone/speaker activity
    NETWORK_PATTERNS = "network_patterns"   # Network usage patterns
    SYSTEM_EVENTS = "system_events"         # Lock/unlock, screensaver
    APPLICATION_FOCUS = "application_focus" # App focus/blur events

class PresenceIndicator(Enum):
    """Background presence indicators"""
    STRONG_PRESENCE = "strong_presence"     # Multiple positive signals
    LIKELY_PRESENT = "likely_present"       # Some positive signals
    UNCERTAIN = "uncertain"                 # Mixed or weak signals
    LIKELY_AWAY = "likely_away"             # Negative signals
    STRONG_ABSENCE = "strong_absence"       # Multiple negative signals

@dataclass
class SensorReading:
    """Individual sensor reading"""
    sensor_type: SensorType
    timestamp: datetime
    value: float           # 0.0 to 1.0, confidence of presence
    metadata: Dict[str, Any]

@dataclass
class PresenceSignal:
    """Aggregated presence signal"""
    user_id: str
    indicator: PresenceIndicator
    confidence: float      # 0.0 to 1.0
    contributing_sensors: List[SensorType]
    last_updated: datetime
    metadata: Dict[str, Any]

class BackgroundSensingSystem:
    """
    Passive presence detection using ambient system and browser signals
    """
    
    def __init__(self):
        self.sensor_readings: Dict[str, List[SensorReading]] = {}
        self.presence_signals: Dict[str, PresenceSignal] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.sensor_weights = {}
        self.detection_rules = {}
        self._initialize_sensors()
    
    def _initialize_sensors(self):
        """Initialize sensor configurations and weights"""
        
        # Sensor weights for presence calculation
        self.sensor_weights = {
            SensorType.APPLICATION_FOCUS: 0.4,     # High weight - direct engagement
            SensorType.BROWSER_SIGNALS: 0.3,       # High weight - user interaction
            SensorType.SYSTEM_ACTIVITY: 0.2,       # Medium weight - indirect signal
            SensorType.AUDIO_ACTIVITY: 0.15,       # Medium weight - can be ambiguous
            SensorType.NETWORK_PATTERNS: 0.1,      # Low weight - background activity
            SensorType.SYSTEM_EVENTS: 0.25,        # Medium-high weight - direct user action
        }
        
        # Detection rules and thresholds
        self.detection_rules = {
            "sensor_timeout": 300,              # 5 minutes
            "confidence_threshold_high": 0.7,   # Strong presence
            "confidence_threshold_medium": 0.4, # Likely present
            "confidence_threshold_low": 0.2,    # Uncertain
            "min_sensors_for_confidence": 2,    # Minimum sensors for reliable reading
            "system_activity_threshold": 0.1,   # CPU usage threshold
            "network_activity_threshold": 0.05, # Network usage threshold
        }
    
    async def start_background_sensing(self, user_id: str):
        """Start background sensing for a user"""
        try:
            if user_id in self.monitoring_tasks:
                # Already monitoring
                return
            
            # Initialize user data
            self.sensor_readings[user_id] = []
            self.presence_signals[user_id] = PresenceSignal(
                user_id=user_id,
                indicator=PresenceIndicator.UNCERTAIN,
                confidence=0.5,
                contributing_sensors=[],
                last_updated=datetime.now(),
                metadata={}
            )
            
            # Start monitoring tasks
            task = asyncio.create_task(self._monitor_background_signals(user_id))
            self.monitoring_tasks[user_id] = task
            
            logger.info(f"📡 Started background sensing for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start background sensing: {e}")
            raise
    
    async def _monitor_background_signals(self, user_id: str):
        """Monitor background signals continuously"""
        try:
            while user_id in self.monitoring_tasks:
                # Collect sensor readings
                await self._collect_system_activity(user_id)
                await self._collect_network_patterns(user_id)
                
                # Update presence signal
                await self._update_presence_signal(user_id)
                
                # Wait before next reading
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except asyncio.CancelledError:
            logger.debug(f"📡 Background sensing cancelled for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Background sensing error for user {user_id}: {e}")
    
    async def _collect_system_activity(self, user_id: str):
        """Collect system activity indicators"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_presence = min(1.0, cpu_percent / 50.0)  # Normalize to 0-1
            
            # Memory usage (less indicative but can show active applications)
            memory = psutil.virtual_memory()
            memory_activity = min(1.0, (memory.percent - 50) / 50.0) if memory.percent > 50 else 0
            
            # Disk I/O activity
            try:
                disk_io = psutil.disk_io_counters()
                # This is a simplistic approach - in reality you'd compare with baseline
                disk_activity = 0.3 if disk_io else 0.1
            except:
                disk_activity = 0.1
            
            # Combine system metrics
            system_presence = (cpu_presence * 0.6 + memory_activity * 0.2 + disk_activity * 0.2)
            
            # Record reading
            reading = SensorReading(
                sensor_type=SensorType.SYSTEM_ACTIVITY,
                timestamp=datetime.now(),
                value=system_presence,
                metadata={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_activity": disk_activity
                }
            )
            
            self.sensor_readings[user_id].append(reading)
            
        except Exception as e:
            logger.error(f"❌ Failed to collect system activity: {e}")
    
    async def _collect_network_patterns(self, user_id: str):
        """Collect network activity patterns"""
        try:
            # Network I/O
            try:
                net_io = psutil.net_io_counters()
                # Simple heuristic: recent network activity suggests presence
                # In reality, you'd track changes over time
                network_activity = 0.4 if net_io.bytes_sent > 0 or net_io.bytes_recv > 0 else 0.1
            except:
                network_activity = 0.1
            
            # Number of active network connections
            try:
                connections = len(psutil.net_connections())
                connection_activity = min(1.0, connections / 50.0)  # Normalize
            except:
                connection_activity = 0.1
            
            # Combine network metrics
            network_presence = (network_activity * 0.7 + connection_activity * 0.3)
            
            # Record reading
            reading = SensorReading(
                sensor_type=SensorType.NETWORK_PATTERNS,
                timestamp=datetime.now(),
                value=network_presence,
                metadata={
                    "network_activity": network_activity,
                    "active_connections": connection_activity
                }
            )
            
            self.sensor_readings[user_id].append(reading)
            
        except Exception as e:
            logger.error(f"❌ Failed to collect network patterns: {e}")
    
    async def record_browser_signal(
        self, 
        user_id: str, 
        signal_type: str, 
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record browser-based presence signal"""
        try:
            if user_id not in self.sensor_readings:
                await self.start_background_sensing(user_id)
            
            # Map signal types to presence values
            signal_mapping = {
                "tab_focus": 0.9,
                "tab_blur": 0.1,
                "window_focus": 0.8,
                "window_blur": 0.2,
                "scroll_activity": 0.6,
                "click_activity": 0.8,
                "typing_activity": 0.9,
                "mouse_movement": 0.5,
                "page_visibility": value,  # Use provided value
            }
            
            presence_value = signal_mapping.get(signal_type, value)
            
            # Record reading
            reading = SensorReading(
                sensor_type=SensorType.BROWSER_SIGNALS,
                timestamp=datetime.now(),
                value=presence_value,
                metadata={
                    "signal_type": signal_type,
                    "original_value": value,
                    **(metadata or {})
                }
            )
            
            self.sensor_readings[user_id].append(reading)
            
            # Trigger immediate presence update for high-confidence signals
            if presence_value > 0.7:
                await self._update_presence_signal(user_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to record browser signal: {e}")
    
    async def record_application_focus(self, user_id: str, focused: bool):
        """Record application focus/blur events"""
        try:
            if user_id not in self.sensor_readings:
                await self.start_background_sensing(user_id)
            
            presence_value = 0.9 if focused else 0.1
            
            reading = SensorReading(
                sensor_type=SensorType.APPLICATION_FOCUS,
                timestamp=datetime.now(),
                value=presence_value,
                metadata={
                    "focused": focused,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.sensor_readings[user_id].append(reading)
            
            # Immediate presence update for focus changes
            await self._update_presence_signal(user_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to record application focus: {e}")
    
    async def record_audio_activity(
        self, 
        user_id: str, 
        activity_type: str, 
        intensity: float
    ):
        """Record audio-related activity"""
        try:
            if user_id not in self.sensor_readings:
                await self.start_background_sensing(user_id)
            
            # Map audio activity to presence confidence
            activity_mapping = {
                "microphone_active": 0.8,
                "speaker_output": 0.6,
                "voice_detected": 0.9,
                "audio_input": 0.7,
                "audio_output": 0.5,
            }
            
            base_presence = activity_mapping.get(activity_type, 0.5)
            presence_value = min(1.0, base_presence * intensity)
            
            reading = SensorReading(
                sensor_type=SensorType.AUDIO_ACTIVITY,
                timestamp=datetime.now(),
                value=presence_value,
                metadata={
                    "activity_type": activity_type,
                    "intensity": intensity
                }
            )
            
            self.sensor_readings[user_id].append(reading)
            
        except Exception as e:
            logger.error(f"❌ Failed to record audio activity: {e}")
    
    async def record_system_event(self, user_id: str, event_type: str):
        """Record system-level events"""
        try:
            if user_id not in self.sensor_readings:
                await self.start_background_sensing(user_id)
            
            # Map system events to presence confidence
            event_mapping = {
                "screen_unlock": 0.9,
                "screen_lock": 0.1,
                "screensaver_start": 0.1,
                "screensaver_end": 0.8,
                "user_login": 0.95,
                "user_logout": 0.0,
                "system_wake": 0.7,
                "system_sleep": 0.0,
            }
            
            presence_value = event_mapping.get(event_type, 0.5)
            
            reading = SensorReading(
                sensor_type=SensorType.SYSTEM_EVENTS,
                timestamp=datetime.now(),
                value=presence_value,
                metadata={
                    "event_type": event_type
                }
            )
            
            self.sensor_readings[user_id].append(reading)
            
            # Immediate update for important system events
            if presence_value in [0.0, 0.95]:
                await self._update_presence_signal(user_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to record system event: {e}")
    
    async def _update_presence_signal(self, user_id: str):
        """Update aggregated presence signal from sensor readings"""
        try:
            readings = self.sensor_readings.get(user_id, [])
            if not readings:
                return
            
            # Filter recent readings (last 5 minutes)
            cutoff = datetime.now() - timedelta(seconds=self.detection_rules["sensor_timeout"])
            recent_readings = [r for r in readings if r.timestamp > cutoff]
            
            if not recent_readings:
                # No recent readings, reduce confidence
                signal = self.presence_signals[user_id]
                signal.confidence *= 0.5
                signal.indicator = self._calculate_presence_indicator(signal.confidence)
                signal.last_updated = datetime.now()
                return
            
            # Group readings by sensor type
            sensor_values = {}
            for reading in recent_readings:
                sensor_type = reading.sensor_type
                if sensor_type not in sensor_values:
                    sensor_values[sensor_type] = []
                sensor_values[sensor_type].append(reading.value)
            
            # Calculate weighted presence score
            total_weight = 0
            weighted_sum = 0
            contributing_sensors = []
            
            for sensor_type, values in sensor_values.items():
                if sensor_type in self.sensor_weights:
                    weight = self.sensor_weights[sensor_type]
                    avg_value = sum(values) / len(values)
                    
                    weighted_sum += weight * avg_value
                    total_weight += weight
                    contributing_sensors.append(sensor_type)
            
            # Calculate final confidence
            if total_weight > 0:
                confidence = weighted_sum / total_weight
            else:
                confidence = 0.5  # Default uncertain
            
            # Apply minimum sensor requirement
            if len(contributing_sensors) < self.detection_rules["min_sensors_for_confidence"]:
                confidence *= 0.7  # Reduce confidence with few sensors
            
            # Update presence signal
            indicator = self._calculate_presence_indicator(confidence)
            
            self.presence_signals[user_id] = PresenceSignal(
                user_id=user_id,
                indicator=indicator,
                confidence=confidence,
                contributing_sensors=contributing_sensors,
                last_updated=datetime.now(),
                metadata={
                    "sensor_count": len(contributing_sensors),
                    "recent_readings": len(recent_readings),
                    "weighted_sum": weighted_sum,
                    "total_weight": total_weight
                }
            )
            
            # Clean up old readings
            self.sensor_readings[user_id] = [
                r for r in readings 
                if r.timestamp > datetime.now() - timedelta(hours=2)
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to update presence signal: {e}")
    
    def _calculate_presence_indicator(self, confidence: float) -> PresenceIndicator:
        """Calculate presence indicator from confidence score"""
        if confidence >= self.detection_rules["confidence_threshold_high"]:
            return PresenceIndicator.STRONG_PRESENCE
        elif confidence >= self.detection_rules["confidence_threshold_medium"]:
            return PresenceIndicator.LIKELY_PRESENT
        elif confidence >= self.detection_rules["confidence_threshold_low"]:
            return PresenceIndicator.UNCERTAIN
        elif confidence > 0.1:
            return PresenceIndicator.LIKELY_AWAY
        else:
            return PresenceIndicator.STRONG_ABSENCE
    
    async def get_presence_signal(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get current presence signal for user"""
        try:
            if user_id not in self.presence_signals:
                return None
            
            signal = self.presence_signals[user_id]
            
            # Calculate time since last update
            time_since_update = (datetime.now() - signal.last_updated).total_seconds()
            
            # Get recent sensor summary
            recent_readings = [
                r for r in self.sensor_readings.get(user_id, [])
                if r.timestamp > datetime.now() - timedelta(minutes=5)
            ]
            
            sensor_summary = {}
            for reading in recent_readings:
                sensor_type = reading.sensor_type.value
                if sensor_type not in sensor_summary:
                    sensor_summary[sensor_type] = {"count": 0, "avg_value": 0}
                sensor_summary[sensor_type]["count"] += 1
                sensor_summary[sensor_type]["avg_value"] += reading.value
            
            # Calculate averages
            for sensor_data in sensor_summary.values():
                sensor_data["avg_value"] /= sensor_data["count"]
                sensor_data["avg_value"] = round(sensor_data["avg_value"], 2)
            
            return {
                "user_id": user_id,
                "presence_indicator": signal.indicator.value,
                "confidence": round(signal.confidence, 2),
                "contributing_sensors": [s.value for s in signal.contributing_sensors],
                "last_updated": signal.last_updated.isoformat(),
                "seconds_since_update": int(time_since_update),
                "recent_sensor_summary": sensor_summary,
                "metadata": signal.metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get presence signal: {e}")
            return None
    
    async def get_sensor_health(self, user_id: str) -> Dict[str, Any]:
        """Get health status of background sensors"""
        try:
            if user_id not in self.sensor_readings:
                return {
                    "user_id": user_id,
                    "monitoring": False,
                    "sensor_health": {}
                }
            
            readings = self.sensor_readings[user_id]
            cutoff = datetime.now() - timedelta(minutes=10)
            recent_readings = [r for r in readings if r.timestamp > cutoff]
            
            # Analyze sensor health
            sensor_health = {}
            for sensor_type in SensorType:
                type_readings = [r for r in recent_readings if r.sensor_type == sensor_type]
                
                sensor_health[sensor_type.value] = {
                    "active": len(type_readings) > 0,
                    "reading_count": len(type_readings),
                    "last_reading": max([r.timestamp for r in type_readings]).isoformat() if type_readings else None,
                    "avg_value": round(sum([r.value for r in type_readings]) / len(type_readings), 2) if type_readings else 0
                }
            
            return {
                "user_id": user_id,
                "monitoring": user_id in self.monitoring_tasks,
                "total_recent_readings": len(recent_readings),
                "sensor_health": sensor_health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get sensor health: {e}")
            return {
                "user_id": user_id,
                "monitoring": False,
                "sensor_health": {}
            }
    
    async def stop_background_sensing(self, user_id: str):
        """Stop background sensing for a user"""
        try:
            # Cancel monitoring task
            if user_id in self.monitoring_tasks:
                self.monitoring_tasks[user_id].cancel()
                del self.monitoring_tasks[user_id]
            
            # Clean up data
            if user_id in self.sensor_readings:
                del self.sensor_readings[user_id]
            if user_id in self.presence_signals:
                del self.presence_signals[user_id]
            
            logger.info(f"📡 Stopped background sensing for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop background sensing: {e}")

# Global instance
background_sensor = BackgroundSensingSystem()

__all__ = ["background_sensor", "SensorType", "PresenceIndicator"]
