#!/usr/bin/env python3
"""
Resource Monitor - System resource monitoring and optimization

This module addresses performance concerns from the code review by providing:
- Real-time system resource monitoring
- Memory leak detection and prevention
- CPU usage optimization
- I/O performance tracking
- Automatic resource cleanup
- Performance bottleneck identification

Author: Emotional AI System
Date: August 3, 2025
"""

import asyncio
import logging
import psutil
import time
import threading
from typing import Dict, List, Optional, Any, Callable, NamedTuple
from dataclasses import dataclass, field
from collections import deque
import gc
import tracemalloc
import weakref
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ResourceSnapshot:
    """Snapshot of system resources at a point in time"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    open_files: int
    active_threads: int

@dataclass
class PerformanceAlert:
    """Alert for performance issues"""
    timestamp: float
    level: str  # "warning", "critical"
    category: str  # "memory", "cpu", "disk", "network"
    message: str
    value: float
    threshold: float
    
@dataclass
class ResourceLimits:
    """Resource usage limits and thresholds"""
    max_memory_percent: float = 80.0
    max_cpu_percent: float = 85.0
    max_disk_percent: float = 90.0
    max_open_files: int = 1000
    max_active_threads: int = 100
    memory_warning_percent: float = 70.0
    cpu_warning_percent: float = 70.0

class MemoryLeakDetector:
    """Detect and track memory leaks"""
    
    def __init__(self):
        self.snapshots = deque(maxlen=100)
        self.leak_threshold = 50 * 1024 * 1024  # 50MB
        self.check_interval = 300  # 5 minutes
        self.last_check = 0
        
        # Start tracemalloc if not already started
        if not tracemalloc.is_tracing():
            tracemalloc.start()
    
    def take_snapshot(self) -> None:
        """Take a memory snapshot"""
        try:
            snapshot = tracemalloc.take_snapshot()
            current_size = sum(stat.size for stat in snapshot.statistics('filename'))
            
            self.snapshots.append({
                'timestamp': time.time(),
                'size': current_size,
                'snapshot': snapshot
            })
            
        except Exception as e:
            logger.error(f"Failed to take memory snapshot: {e}")
    
    def detect_leaks(self) -> List[Dict[str, Any]]:
        """Detect potential memory leaks"""
        if len(self.snapshots) < 2:
            return []
        
        current_time = time.time()
        if current_time - self.last_check < self.check_interval:
            return []
        
        self.last_check = current_time
        leaks = []
        
        try:
            # Compare first and last snapshots
            first_snapshot = self.snapshots[0]
            last_snapshot = self.snapshots[-1]
            
            size_growth = last_snapshot['size'] - first_snapshot['size']
            time_span = last_snapshot['timestamp'] - first_snapshot['timestamp']
            
            if size_growth > self.leak_threshold:
                # Analyze top growing files
                if 'snapshot' in last_snapshot and 'snapshot' in first_snapshot:
                    top_current = last_snapshot['snapshot'].statistics('filename')[:10]
                    
                    for stat in top_current:
                        leak_info = {
                            'filename': stat.traceback.format()[0] if stat.traceback else 'unknown',
                            'size_mb': stat.size / 1024 / 1024,
                            'growth_rate_mb_per_hour': (size_growth / time_span) * 3600 / 1024 / 1024,
                            'line_count': stat.count
                        }
                        leaks.append(leak_info)
            
        except Exception as e:
            logger.error(f"Error detecting memory leaks: {e}")
        
        return leaks

class ResourceMonitor:
    """Comprehensive system resource monitoring"""
    
    def __init__(self, check_interval: float = 5.0):
        self.check_interval = check_interval
        self.limits = ResourceLimits()
        self.history = deque(maxlen=1000)  # Keep last 1000 snapshots
        self.alerts = deque(maxlen=500)    # Keep last 500 alerts
        self.leak_detector = MemoryLeakDetector()
        
        self.monitoring = False
        self.monitor_thread = None
        
        # Performance callbacks
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        self.cleanup_callbacks: List[Callable[[], None]] = []
        
        # Tracked objects for cleanup
        self.tracked_objects = weakref.WeakSet()
        
        # Network baseline
        self.network_baseline = None
        self._update_network_baseline()
    
    def _update_network_baseline(self):
        """Update network usage baseline"""
        try:
            net_io = psutil.net_io_counters()
            self.network_baseline = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Failed to update network baseline: {e}")
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Add callback for performance alerts"""
        self.alert_callbacks.append(callback)
    
    def add_cleanup_callback(self, callback: Callable[[], None]):
        """Add callback for resource cleanup"""
        self.cleanup_callbacks.append(callback)
    
    def track_object(self, obj: Any):
        """Track object for cleanup monitoring"""
        self.tracked_objects.add(obj)
    
    def get_current_snapshot(self) -> ResourceSnapshot:
        """Get current resource usage snapshot"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network usage
            net_io = psutil.net_io_counters()
            network_sent_mb = 0.0
            network_recv_mb = 0.0
            
            if self.network_baseline:
                time_diff = time.time() - self.network_baseline['timestamp']
                if time_diff > 0:
                    network_sent_mb = (net_io.bytes_sent - self.network_baseline['bytes_sent']) / 1024 / 1024
                    network_recv_mb = (net_io.bytes_recv - self.network_baseline['bytes_recv']) / 1024 / 1024
            
            # Process info
            current_process = psutil.Process()
            open_files = len(current_process.open_files())
            active_threads = threading.active_count()
            
            return ResourceSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_available_mb=memory.available / 1024 / 1024,
                disk_usage_percent=disk.percent,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                open_files=open_files,
                active_threads=active_threads
            )
            
        except Exception as e:
            logger.error(f"Failed to get resource snapshot: {e}")
            return ResourceSnapshot(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                open_files=0,
                active_threads=0
            )
    
    def check_thresholds(self, snapshot: ResourceSnapshot) -> List[PerformanceAlert]:
        """Check resource usage against thresholds"""
        alerts = []
        
        # Memory checks
        if snapshot.memory_percent > self.limits.max_memory_percent:
            alerts.append(PerformanceAlert(
                timestamp=snapshot.timestamp,
                level="critical",
                category="memory",
                message=f"Memory usage critical: {snapshot.memory_percent:.1f}%",
                value=snapshot.memory_percent,
                threshold=self.limits.max_memory_percent
            ))
        elif snapshot.memory_percent > self.limits.memory_warning_percent:
            alerts.append(PerformanceAlert(
                timestamp=snapshot.timestamp,
                level="warning",
                category="memory",
                message=f"Memory usage high: {snapshot.memory_percent:.1f}%",
                value=snapshot.memory_percent,
                threshold=self.limits.memory_warning_percent
            ))
        
        # CPU checks
        if snapshot.cpu_percent > self.limits.max_cpu_percent:
            alerts.append(PerformanceAlert(
                timestamp=snapshot.timestamp,
                level="critical",
                category="cpu",
                message=f"CPU usage critical: {snapshot.cpu_percent:.1f}%",
                value=snapshot.cpu_percent,
                threshold=self.limits.max_cpu_percent
            ))
        elif snapshot.cpu_percent > self.limits.cpu_warning_percent:
            alerts.append(PerformanceAlert(
                timestamp=snapshot.timestamp,
                level="warning",
                category="cpu",
                message=f"CPU usage high: {snapshot.cpu_percent:.1f}%",
                value=snapshot.cpu_percent,
                threshold=self.limits.cpu_warning_percent
            ))
        
        # Disk checks
        if snapshot.disk_usage_percent > self.limits.max_disk_percent:
            alerts.append(PerformanceAlert(
                timestamp=snapshot.timestamp,
                level="critical",
                category="disk",
                message=f"Disk usage critical: {snapshot.disk_usage_percent:.1f}%",
                value=snapshot.disk_usage_percent,
                threshold=self.limits.max_disk_percent
            ))
        
        # File handle checks
        if snapshot.open_files > self.limits.max_open_files:
            alerts.append(PerformanceAlert(
                timestamp=snapshot.timestamp,
                level="warning",
                category="files",
                message=f"Too many open files: {snapshot.open_files}",
                value=float(snapshot.open_files),
                threshold=float(self.limits.max_open_files)
            ))
        
        # Thread checks
        if snapshot.active_threads > self.limits.max_active_threads:
            alerts.append(PerformanceAlert(
                timestamp=snapshot.timestamp,
                level="warning",
                category="threads",
                message=f"Too many active threads: {snapshot.active_threads}",
                value=float(snapshot.active_threads),
                threshold=float(self.limits.max_active_threads)
            ))
        
        return alerts
    
    def trigger_cleanup(self):
        """Trigger resource cleanup procedures"""
        logger.info("Triggering resource cleanup")
        
        try:
            # Force garbage collection
            gc.collect()
            
            # Call registered cleanup callbacks
            for callback in self.cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Cleanup callback failed: {e}")
            
            # Memory leak detection
            self.leak_detector.take_snapshot()
            leaks = self.leak_detector.detect_leaks()
            
            if leaks:
                logger.warning(f"Detected {len(leaks)} potential memory leaks")
                for leak in leaks:
                    logger.warning(f"Memory leak: {leak}")
            
        except Exception as e:
            logger.error(f"Resource cleanup failed: {e}")
    
    def optimize_performance(self, snapshot: ResourceSnapshot):
        """Optimize performance based on current resource usage"""
        
        # Trigger cleanup if memory usage is high
        if snapshot.memory_percent > self.limits.memory_warning_percent:
            self.trigger_cleanup()
        
        # Adjust monitoring frequency based on resource usage
        if snapshot.cpu_percent > 50 or snapshot.memory_percent > 50:
            # Increase monitoring frequency during high usage
            self.check_interval = max(1.0, self.check_interval * 0.8)
        else:
            # Decrease frequency during low usage
            self.check_interval = min(10.0, self.check_interval * 1.1)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Resource monitoring started")
        
        while self.monitoring:
            try:
                # Get current snapshot
                snapshot = self.get_current_snapshot()
                self.history.append(snapshot)
                
                # Check thresholds
                alerts = self.check_thresholds(snapshot)
                
                # Process alerts
                for alert in alerts:
                    self.alerts.append(alert)
                    
                    # Call alert callbacks
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            logger.error(f"Alert callback failed: {e}")
                
                # Optimize performance
                self.optimize_performance(snapshot)
                
                # Sleep until next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(5)  # Wait before retrying
        
        logger.info("Resource monitoring stopped")
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Resource monitoring thread started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.history:
            return {}
        
        recent_snapshots = list(self.history)[-10:]  # Last 10 snapshots
        
        return {
            'current': recent_snapshots[-1].__dict__ if recent_snapshots else {},
            'averages': {
                'cpu_percent': sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots),
                'memory_percent': sum(s.memory_percent for s in recent_snapshots) / len(recent_snapshots),
                'disk_usage_percent': sum(s.disk_usage_percent for s in recent_snapshots) / len(recent_snapshots),
            },
            'peaks': {
                'max_cpu': max(s.cpu_percent for s in recent_snapshots),
                'max_memory': max(s.memory_percent for s in recent_snapshots),
                'max_open_files': max(s.open_files for s in recent_snapshots),
            },
            'active_alerts': len([a for a in self.alerts if time.time() - a.timestamp < 300]),  # Last 5 minutes
            'total_snapshots': len(self.history),
            'monitored_objects': len(self.tracked_objects)
        }
    
    def export_performance_data(self, filepath: Optional[str] = None) -> str:
        """Export performance data to JSON file"""
        if filepath is None:
            filepath = f"performance_data_{int(time.time())}.json"
        
        data = {
            'summary': self.get_performance_summary(),
            'recent_history': [s.__dict__ for s in list(self.history)[-100:]],  # Last 100 snapshots
            'recent_alerts': [a.__dict__ for a in list(self.alerts)[-50:]],     # Last 50 alerts
            'limits': self.limits.__dict__,
            'export_timestamp': time.time()
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Performance data exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export performance data: {e}")
            return ""

# Global resource monitor instance
resource_monitor = ResourceMonitor()

# Convenience functions
def start_monitoring():
    """Start resource monitoring"""
    resource_monitor.start_monitoring()

def stop_monitoring():
    """Stop resource monitoring"""
    resource_monitor.stop_monitoring()

def get_performance_summary() -> Dict[str, Any]:
    """Get current performance summary"""
    return resource_monitor.get_performance_summary()

def trigger_cleanup():
    """Trigger resource cleanup"""
    resource_monitor.trigger_cleanup()

def track_object(obj: Any):
    """Track object for cleanup monitoring"""
    resource_monitor.track_object(obj)
