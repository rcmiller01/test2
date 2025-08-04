#!/usr/bin/env python3
"""
Scheduler Transparency Module - Task scheduling with comprehensive logging

Provides transparent scheduling of AI tasks with detailed logging of:
- Task scheduling decisions
- Execution results  
- Performance metrics
- Model promotion/replacement events
- Resource usage tracking

Author: Emotional AI System
Date: August 3, 2025
"""

import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ScheduledTask:
    """Represents a scheduled task with metadata"""
    task_id: str
    name: str
    function: Callable
    scheduled_time: datetime
    priority: TaskPriority = TaskPriority.NORMAL
    max_runtime: Optional[timedelta] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Status tracking
    status: TaskStatus = TaskStatus.SCHEDULED
    created_time: datetime = field(default_factory=datetime.now)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class TaskExecutionLog:
    """Log entry for task execution"""
    timestamp: datetime
    task_id: str
    event_type: str  # scheduled, started, completed, failed, skipped
    details: Dict[str, Any]
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class TransparentScheduler:
    """Scheduler with comprehensive logging and transparency"""
    
    def __init__(self, log_file: str = "logs/scheduler.jsonl"):
        self.tasks = {}  # task_id -> ScheduledTask
        self.execution_logs = []
        self.log_file = log_file
        self.running = False
        self.scheduler_thread = None
        
        # Performance tracking
        self.task_performance = {}  # task_name -> performance stats
        self.resource_usage = {}
        
        # Setup analytics logger
        self.analytics_logger = logging.getLogger("scheduler_analytics")
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup analytics logging"""
        try:
            import os
            from logging.handlers import RotatingFileHandler
            
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            
            handler = RotatingFileHandler(
                self.log_file,
                maxBytes=20*1024*1024,  # 20MB
                backupCount=5
            )
            
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.analytics_logger.addHandler(handler)
            self.analytics_logger.setLevel(logging.INFO)
            
        except Exception as e:
            logger.warning(f"Could not setup scheduler logging: {e}")
    
    def schedule_task(self, 
                     task_id: str,
                     name: str, 
                     function: Callable,
                     scheduled_time: datetime,
                     priority: TaskPriority = TaskPriority.NORMAL,
                     **kwargs) -> bool:
        """Schedule a new task"""
        try:
            task = ScheduledTask(
                task_id=task_id,
                name=name,
                function=function,
                scheduled_time=scheduled_time,
                priority=priority,
                **kwargs
            )
            
            self.tasks[task_id] = task
            
            # Log scheduling event
            self._log_task_event(task, "scheduled", {
                "scheduled_for": scheduled_time.isoformat(),
                "priority": priority.name,
                "dependencies": task.dependencies
            })
            
            logger.info(f"Scheduled task {task_id} ({name}) for {scheduled_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling task {task_id}: {e}")
            return False
    
    def start_scheduler(self):
        """Start the scheduler daemon"""
        if self.running:
            return
            
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Transparent scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Get tasks ready to run
                ready_tasks = self._get_ready_tasks(current_time)
                
                # Sort by priority and scheduled time
                ready_tasks.sort(key=lambda t: (t.priority.value, t.scheduled_time), reverse=True)
                
                # Execute ready tasks
                for task in ready_tasks:
                    if not self.running:
                        break
                    
                    self._execute_task(task)
                
                # Clean up old completed tasks
                self._cleanup_old_tasks()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(30)
    
    def _get_ready_tasks(self, current_time: datetime) -> List[ScheduledTask]:
        """Get tasks that are ready to run"""
        ready_tasks = []
        
        for task in self.tasks.values():
            if task.status != TaskStatus.SCHEDULED:
                continue
                
            # Check if it's time to run
            if task.scheduled_time > current_time:
                continue
            
            # Check dependencies
            if not self._dependencies_satisfied(task):
                self._log_task_event(task, "skipped", {
                    "reason": "dependencies_not_satisfied",
                    "missing_dependencies": self._get_missing_dependencies(task)
                })
                continue
            
            ready_tasks.append(task)
        
        return ready_tasks
    
    def _dependencies_satisfied(self, task: ScheduledTask) -> bool:
        """Check if task dependencies are satisfied"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            
            dep_task = self.tasks[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _get_missing_dependencies(self, task: ScheduledTask) -> List[str]:
        """Get list of missing dependencies"""
        missing = []
        for dep_id in task.dependencies:
            if dep_id not in self.tasks or self.tasks[dep_id].status != TaskStatus.COMPLETED:
                missing.append(dep_id)
        return missing
    
    def _execute_task(self, task: ScheduledTask):
        """Execute a single task"""
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
        
        self._log_task_event(task, "started", {
            "actual_start_time": task.start_time.isoformat(),
            "delay_minutes": (task.start_time - task.scheduled_time).total_seconds() / 60
        })
        
        try:
            # Record resource usage before execution
            start_metrics = self._capture_resource_metrics()
            
            # Execute the task function
            if task.max_runtime:
                # TODO: Implement timeout wrapper
                result = task.function(**task.metadata)
            else:
                result = task.function(**task.metadata)
            
            # Record completion
            task.end_time = datetime.now()
            task.status = TaskStatus.COMPLETED
            task.result = result
            
            # Calculate performance metrics
            end_metrics = self._capture_resource_metrics()
            performance = self._calculate_performance_metrics(
                task, start_metrics, end_metrics
            )
            
            self._log_task_event(task, "completed", {
                "execution_time_seconds": (task.end_time - task.start_time).total_seconds(),
                "result_summary": str(result)[:200] if result else None,
                "performance": performance
            })
            
            # Update performance tracking
            self._update_performance_stats(task.name, performance)
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            task.end_time = datetime.now()
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            self._log_task_event(task, "failed", {
                "error_message": str(e),
                "execution_time_seconds": (task.end_time - task.start_time).total_seconds(),
                "retry_count": task.retry_count
            })
            
            # Handle retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.SCHEDULED
                task.scheduled_time = datetime.now() + timedelta(minutes=5 * task.retry_count)
                
                self._log_task_event(task, "scheduled_retry", {
                    "retry_number": task.retry_count,
                    "next_attempt": task.scheduled_time.isoformat()
                })
            
            logger.error(f"Task {task.task_id} failed: {e}")
    
    def _capture_resource_metrics(self) -> Dict[str, Any]:
        """Capture current resource usage metrics"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_mb": psutil.virtual_memory().used / (1024*1024),
                "timestamp": datetime.now().isoformat()
            }
        except Exception:
            return {"timestamp": datetime.now().isoformat()}
    
    def _calculate_performance_metrics(self, 
                                     task: ScheduledTask,
                                     start_metrics: Dict[str, Any],
                                     end_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate task performance metrics"""
        try:
            execution_time = (task.end_time - task.start_time).total_seconds()
            
            metrics = {
                "execution_time_seconds": execution_time,
                "scheduled_delay_seconds": (task.start_time - task.scheduled_time).total_seconds()
            }
            
            # Resource usage delta
            if "cpu_percent" in start_metrics and "cpu_percent" in end_metrics:
                metrics["avg_cpu_usage"] = (start_metrics["cpu_percent"] + end_metrics["cpu_percent"]) / 2
            
            if "memory_mb" in start_metrics and "memory_mb" in end_metrics:
                metrics["memory_delta_mb"] = end_metrics["memory_mb"] - start_metrics["memory_mb"]
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Error calculating performance metrics: {e}")
            return {}
    
    def _update_performance_stats(self, task_name: str, performance: Dict[str, Any]):
        """Update performance statistics for task type"""
        if task_name not in self.task_performance:
            self.task_performance[task_name] = {
                "total_executions": 0,
                "total_time": 0,
                "avg_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
                "success_rate": 1.0
            }
        
        stats = self.task_performance[task_name]
        exec_time = performance.get("execution_time_seconds", 0)
        
        stats["total_executions"] += 1
        stats["total_time"] += exec_time
        stats["avg_time"] = stats["total_time"] / stats["total_executions"]
        stats["min_time"] = min(stats["min_time"], exec_time)
        stats["max_time"] = max(stats["max_time"], exec_time)
    
    def _log_task_event(self, task: ScheduledTask, event_type: str, details: Dict[str, Any]):
        """Log a task event"""
        log_entry = TaskExecutionLog(
            timestamp=datetime.now(),
            task_id=task.task_id,
            event_type=event_type,
            details=details,
            performance_metrics=details.get("performance", {})
        )
        
        self.execution_logs.append(log_entry)
        
        # Write to analytics log
        log_data = {
            "timestamp": log_entry.timestamp.isoformat(),
            "task_id": task.task_id,
            "task_name": task.name,
            "event_type": event_type,
            "details": details
        }
        
        self.analytics_logger.info(json.dumps(log_data))
    
    def _cleanup_old_tasks(self):
        """Clean up old completed/failed tasks"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and 
                task.end_time and task.end_time < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
    
    def get_schedule_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        now = datetime.now()
        
        # Count tasks by status
        status_counts = {}
        upcoming_tasks = []
        
        for task in self.tasks.values():
            status_counts[task.status.value] = status_counts.get(task.status.value, 0) + 1
            
            if task.status == TaskStatus.SCHEDULED and task.scheduled_time > now:
                upcoming_tasks.append({
                    "task_id": task.task_id,
                    "name": task.name,
                    "scheduled_time": task.scheduled_time.isoformat(),
                    "priority": task.priority.name,
                    "time_until_execution": str(task.scheduled_time - now)
                })
        
        # Sort upcoming tasks by time
        upcoming_tasks.sort(key=lambda t: t["scheduled_time"])
        
        return {
            "scheduler_running": self.running,
            "total_tasks": len(self.tasks),
            "status_breakdown": status_counts,
            "next_5_tasks": upcoming_tasks[:5],
            "performance_stats": dict(self.task_performance),
            "last_update": now.isoformat()
        }
    
    def get_task_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get task execution history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_logs = [
            {
                "timestamp": log.timestamp.isoformat(),
                "task_id": log.task_id,
                "event_type": log.event_type,
                "details": log.details
            }
            for log in self.execution_logs
            if log.timestamp > cutoff_time
        ]
        
        return sorted(recent_logs, key=lambda x: x["timestamp"], reverse=True)

# Global scheduler instance
transparent_scheduler = TransparentScheduler()
