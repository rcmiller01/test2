#!/usr/bin/env python3
"""
System Metrics Tracker - Enhanced idle detection and activity monitoring

This module provides comprehensive system activity monitoring including:
- Keyboard/mouse activity detection
- Application focus tracking  
- CPU/Memory/Disk usage
- Network activity monitoring
- User engagement metrics

Author: Emotional AI System
Date: August 3, 2025
"""

import time
import psutil
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System activity and performance metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    
    # Activity metrics
    last_input_time: Optional[datetime] = None
    idle_duration_minutes: float = 0.0
    active_window: str = ""
    keyboard_events: int = 0
    mouse_events: int = 0
    
    # Engagement metrics
    user_engaged: bool = False
    engagement_score: float = 0.0
    activity_level: str = "unknown"  # idle, light, moderate, heavy

class ActivityMonitor:
    """Monitor user activity and system metrics"""
    
    def __init__(self):
        self.last_activity = datetime.now()
        self.activity_history = []
        self.monitoring = False
        self.monitor_thread = None
        
        # Activity thresholds (minutes)
        self.idle_threshold = 5.0
        self.light_activity_threshold = 15.0
        self.moderate_activity_threshold = 45.0
        
        # Platform-specific input monitoring
        self.input_monitor = self._setup_input_monitoring()
        
    def _setup_input_monitoring(self):
        """Setup platform-specific input monitoring"""
        try:
            import platform
            system = platform.system().lower()
            
            if system == "windows":
                return self._setup_windows_monitoring()
            elif system == "linux":
                return self._setup_linux_monitoring()
            elif system == "darwin":
                return self._setup_macos_monitoring()
            else:
                logger.warning(f"Input monitoring not supported on {system}")
                return None
                
        except Exception as e:
            logger.warning(f"Could not setup input monitoring: {e}")
            return None
    
    def _setup_windows_monitoring(self):
        """Setup Windows-specific activity monitoring"""
        try:
            import ctypes
            from ctypes import wintypes
            
            class WindowsInputMonitor:
                def __init__(self):
                    self.last_input_info = wintypes.DWORD()
                    
                def get_last_input_time(self):
                    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(self.last_input_info))
                    return self.last_input_info.value
                    
                def get_active_window(self):
                    try:
                        import win32gui
                        window = win32gui.GetForegroundWindow()
                        return win32gui.GetWindowText(window)
                    except ImportError:
                        return "Unknown"
            
            return WindowsInputMonitor()
            
        except Exception as e:
            logger.warning(f"Windows monitoring setup failed: {e}")
            return None
    
    def _setup_linux_monitoring(self):
        """Setup Linux-specific activity monitoring"""
        try:
            # Using Xlib for X11 systems
            from Xlib import display
            from Xlib.ext import record
            from Xlib.protocol import rq
            
            class LinuxInputMonitor:
                def __init__(self):
                    self.display = display.Display()
                    self.last_activity = time.time()
                    
                def get_last_input_time(self):
                    return int((time.time() - self.last_activity) * 1000)
                    
                def get_active_window(self):
                    try:
                        window = self.display.get_input_focus().focus
                        return window.get_wm_name() or "Unknown"
                    except:
                        return "Unknown"
            
            return LinuxInputMonitor()
            
        except Exception as e:
            logger.warning(f"Linux monitoring setup failed: {e}")
            return None
    
    def _setup_macos_monitoring(self):
        """Setup macOS-specific activity monitoring"""
        try:
            import Quartz
            
            class MacOSInputMonitor:
                def get_last_input_time(self):
                    return int(Quartz.CGEventSourceSecondsSinceLastEventType(
                        Quartz.kCGEventSourceStateCombinedSessionState,
                        Quartz.kCGAnyInputEventType
                    ) * 1000)
                    
                def get_active_window(self):
                    try:
                        from AppKit import NSWorkspace
                        app = NSWorkspace.sharedWorkspace().activeApplication()
                        return app.get('NSApplicationName', 'Unknown')
                    except:
                        return "Unknown"
            
            return MacOSInputMonitor()
            
        except Exception as e:
            logger.warning(f"macOS monitoring setup failed: {e}")
            return None
    
    def start_monitoring(self):
        """Start continuous activity monitoring"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Activity monitoring started")
    
    def stop_monitoring(self):
        """Stop activity monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("Activity monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = self.collect_metrics()
                self.activity_history.append(metrics)
                
                # Keep only last hour of metrics
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.activity_history = [
                    m for m in self.activity_history 
                    if m.timestamp > cutoff_time
                ]
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        metrics = SystemMetrics()
        
        try:
            # System performance metrics
            metrics.cpu_percent = psutil.cpu_percent(interval=1)
            metrics.memory_percent = psutil.virtual_memory().percent
            metrics.disk_usage_percent = psutil.disk_usage('/').percent
            
            # Network metrics
            net_io = psutil.net_io_counters()
            metrics.network_bytes_sent = net_io.bytes_sent
            metrics.network_bytes_recv = net_io.bytes_recv
            
            # Activity metrics
            if self.input_monitor:
                try:
                    last_input_ms = self.input_monitor.get_last_input_time()
                    if last_input_ms:
                        metrics.idle_duration_minutes = last_input_ms / (1000 * 60)
                        metrics.last_input_time = datetime.now() - timedelta(milliseconds=last_input_ms)
                    
                    metrics.active_window = self.input_monitor.get_active_window()
                except Exception as e:
                    logger.debug(f"Input monitoring error: {e}")
            
            # Calculate engagement metrics
            metrics.user_engaged = metrics.idle_duration_minutes < self.idle_threshold
            metrics.engagement_score = self._calculate_engagement_score(metrics)
            metrics.activity_level = self._determine_activity_level(metrics)
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
        
        return metrics
    
    def _calculate_engagement_score(self, metrics: SystemMetrics) -> float:
        """Calculate user engagement score (0.0 to 1.0)"""
        try:
            # Base score on idle time (inverted)
            idle_score = max(0, 1 - (metrics.idle_duration_minutes / 60))  # 60 min = 0 score
            
            # Boost score for high system activity
            cpu_score = min(1.0, metrics.cpu_percent / 80)  # 80% CPU = full score
            memory_score = min(1.0, metrics.memory_percent / 90)  # 90% memory = full score
            
            # Combined engagement score
            engagement = (idle_score * 0.6) + (cpu_score * 0.2) + (memory_score * 0.2)
            return max(0.0, min(1.0, engagement))
            
        except Exception:
            return 0.5  # Default moderate engagement
    
    def _determine_activity_level(self, metrics: SystemMetrics) -> str:
        """Determine current activity level"""
        if metrics.idle_duration_minutes > self.moderate_activity_threshold:
            return "idle"
        elif metrics.idle_duration_minutes > self.light_activity_threshold:
            return "light"
        elif metrics.idle_duration_minutes > self.idle_threshold:
            return "moderate"
        else:
            return "heavy"
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent metrics"""
        if not self.activity_history:
            return self.collect_metrics()
        return self.activity_history[-1]
    
    def get_activity_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get activity summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.activity_history 
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No recent activity data"}
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_engagement = sum(m.engagement_score for m in recent_metrics) / len(recent_metrics)
        
        # Activity level distribution
        activity_levels = [m.activity_level for m in recent_metrics]
        activity_dist = {
            level: activity_levels.count(level) / len(activity_levels)
            for level in set(activity_levels)
        }
        
        return {
            "period_hours": hours,
            "sample_count": len(recent_metrics),
            "avg_cpu_percent": round(avg_cpu, 2),
            "avg_memory_percent": round(avg_memory, 2),
            "avg_engagement_score": round(avg_engagement, 2),
            "activity_distribution": activity_dist,
            "currently_engaged": recent_metrics[-1].user_engaged if recent_metrics else False,
            "current_activity_level": recent_metrics[-1].activity_level if recent_metrics else "unknown"
        }

# Global activity monitor instance
activity_monitor = ActivityMonitor()
