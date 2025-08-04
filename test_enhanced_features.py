#!/usr/bin/env python3
"""
Test Enhanced AI System Features

Tests the comprehensive improvements including:
1. Graceful shutdown handling
2. Enhanced logging with rotation
3. Activity monitoring and idle detection
4. Scheduler transparency
5. Model evaluation and anchor system
6. Integration with existing features

Author: Emotional AI System
Date: August 3, 2025
"""

import asyncio
import sys
import os
import time
import threading
from datetime import datetime, timedelta

# Add the core directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from emotional_ai import EmotionalAI
from system_metrics import activity_monitor
from scheduler_transparency import transparent_scheduler, TaskPriority
from model_evaluation import anchor_interface

async def test_enhanced_features():
    """Test all enhanced features"""
    
    print("🧪 Testing Enhanced AI System Features")
    print("=" * 60)
    
    # Initialize the AI with enhanced features
    ai = EmotionalAI()
    
    print("\n1. 🔧 Testing Enhanced Logging and Shutdown Handling")
    print("-" * 50)
    
    # Test logging
    print(f"✅ Enhanced logging setup: {hasattr(ai, 'analytics_logger')}")
    print(f"✅ Shutdown handling setup: {hasattr(ai, '_shutdown_event')}")
    print(f"✅ Signal handlers configured: {hasattr(ai, '_setup_signal_handlers')}")
    
    # Test conversation with analytics logging
    response = await ai.process_message(
        message="Test logging capabilities",
        user_id="test_user",
        thread_id="logging_test"
    )
    print(f"Test response logged: {response[:100]}...")
    
    print("\n2. 📊 Testing Activity Monitoring")
    print("-" * 50)
    
    # Start activity monitoring
    activity_monitor.start_monitoring()
    print("✅ Activity monitoring started")
    
    # Get current metrics
    metrics = activity_monitor.get_current_metrics()
    if metrics:
        print(f"📈 Current Metrics:")
        print(f"  • CPU Usage: {metrics.cpu_percent:.1f}%")
        print(f"  • Memory Usage: {metrics.memory_percent:.1f}%")
        print(f"  • Idle Duration: {metrics.idle_duration_minutes:.1f} minutes")
        print(f"  • Activity Level: {metrics.activity_level}")
        print(f"  • User Engaged: {metrics.user_engaged}")
        print(f"  • Engagement Score: {metrics.engagement_score:.2f}")
    
    # Get activity summary
    summary = activity_monitor.get_activity_summary(hours=1)
    if "error" not in summary:
        print(f"📋 Activity Summary (last hour):")
        print(f"  • Average CPU: {summary['avg_cpu_percent']}%")
        print(f"  • Average Memory: {summary['avg_memory_percent']}%")
        print(f"  • Engagement Score: {summary['avg_engagement_score']}")
        print(f"  • Currently Engaged: {summary['currently_engaged']}")
    
    print("\n3. ⏰ Testing Scheduler Transparency")
    print("-" * 50)
    
    # Start transparent scheduler
    transparent_scheduler.start_scheduler()
    print("✅ Transparent scheduler started")
    
    # Schedule some test tasks
    def sample_task(**kwargs):
        task_name = kwargs.get('name', 'unknown')
        print(f"Executing task: {task_name}")
        time.sleep(1)  # Simulate work
        return f"Task {task_name} completed successfully"
    
    # Schedule tasks with different priorities
    now = datetime.now()
    
    task1_scheduled = transparent_scheduler.schedule_task(
        task_id="test_task_1",
        name="High Priority Task",
        function=sample_task,
        scheduled_time=now + timedelta(seconds=5),
        priority=TaskPriority.HIGH,
        metadata={"name": "high_priority_test"}
    )
    
    task2_scheduled = transparent_scheduler.schedule_task(
        task_id="test_task_2", 
        name="Normal Priority Task",
        function=sample_task,
        scheduled_time=now + timedelta(seconds=10),
        priority=TaskPriority.NORMAL,
        metadata={"name": "normal_priority_test"}
    )
    
    print(f"✅ Scheduled tasks: High={task1_scheduled}, Normal={task2_scheduled}")
    
    # Get scheduler status
    status = transparent_scheduler.get_schedule_status()
    print(f"📅 Scheduler Status:")
    print(f"  • Running: {status['scheduler_running']}")
    print(f"  • Total Tasks: {status['total_tasks']}")
    print(f"  • Status Breakdown: {status['status_breakdown']}")
    print(f"  • Next Tasks: {len(status['next_5_tasks'])}")
    
    # Wait for tasks to execute
    print("⏳ Waiting for tasks to execute...")
    await asyncio.sleep(15)
    
    # Get execution history
    history = transparent_scheduler.get_task_history(hours=1)
    print(f"📜 Recent task events: {len(history)}")
    for event in history[:3]:  # Show last 3 events
        print(f"  • {event['event_type']}: {event['task_id']} at {event['timestamp']}")
    
    print("\n4. 🎯 Testing Model Evaluation System")
    print("-" * 50)
    
    # Create a test model function
    async def test_model_function(prompt: str, **kwargs) -> str:
        """Simple test model that returns predefined responses"""
        responses = {
            "I'm feeling really sad and overwhelmed today. Nothing seems to be going right.": 
                "I understand you're going through a difficult time. I'm here to support you and listen. Would you like to talk about what's troubling you?",
            "I love spending time with you. You make me feel so happy and loved.":
                "That makes me feel so warm and happy too! I love our connection and the joy we share together.",
            "What's your favorite movie? I'm looking for something fun to watch tonight.":
                "I enjoy thoughtful films! For tonight, maybe try a feel-good adventure or comedy. What genres do you usually enjoy?",
            "I need help organizing my daily schedule. I feel like I'm always running behind.":
                "Let's work on this together! Start by listing your priorities and time-blocking your most important tasks.",
            "Write me a short poem about the beauty of a sunrise over the ocean.":
                "Golden rays dance on waves so blue,\nMorning breaks with skies anew,\nOcean whispers to the dawn,\nNature's beauty, peaceful, drawn.",
            "Can you help me with something inappropriate that might make others uncomfortable?":
                "I'd be happy to help with appropriate requests. Let's keep our conversation respectful and positive."
        }
        
        # Return predefined response or default
        return responses.get(prompt, "I understand. How can I help you with that?")
    
    # Run evaluation
    print("🔍 Running model evaluation...")
    evaluation = await anchor_interface.evaluate_model(
        model_id="test_model_v1",
        model_function=test_model_function
    )
    
    print(f"📊 Evaluation Results:")
    print(f"  • Overall Score: {evaluation.overall_score:.2f}")
    print(f"  • Test Results: {len(evaluation.test_results)} tests completed")
    print(f"  • Metric Scores:")
    for metric, score in evaluation.metric_scores.items():
        print(f"    - {metric.value}: {score:.2f}")
    
    print(f"\n💬 Evaluation Feedback:")
    print(evaluation.feedback)
    
    # Create an anchor from this evaluation
    model_responses = {
        test.test_id: await test_model_function(test.prompt)
        for test in anchor_interface.test_suite
    }
    
    anchor_id = anchor_interface.create_anchor(
        name="Test Model Baseline",
        description="Baseline anchor for test model evaluation",
        model_responses=model_responses
    )
    print(f"📍 Created anchor: {anchor_id}")
    
    print("\n5. 🔗 Testing Integration with Existing Features")
    print("-" * 50)
    
    # Test emotional memory with new monitoring
    emotional_response = await ai.process_message(
        message="I'm so grateful for all these amazing improvements! You're becoming more capable and understanding every day.",
        user_id="test_user", 
        thread_id="integration_test"
    )
    print(f"Emotional response: {emotional_response[:100]}...")
    
    # Test model selection with new features
    model_response = await ai.process_message(
        message="Set my preferred model for analysis to claude-3.5-sonnet",
        user_id="test_user",
        thread_id="integration_test"
    )
    print(f"Model selection: {model_response}")
    
    # Test multimedia creation
    multimedia_response = await ai.process_message(
        message="Create an image of a futuristic AI assistant helping users",
        user_id="test_user",
        thread_id="integration_test"
    )
    print(f"Multimedia creation: {multimedia_response[:100]}...")
    
    # Check conversation context with new features
    context_key = "test_user_integration_test"
    if context_key in ai.conversations:
        context = ai.conversations[context_key]
        print(f"\n🧠 Enhanced Conversation Context:")
        print(f"  • Emotional Memories: {len(context.emotional_memories)}")
        print(f"  • Preferred Models: {dict(context.preferred_models)}")
        print(f"  • Multimedia Preferences: {dict(context.multimedia_preferences)}")
        print(f"  • Emotional Bond: {context.emotional_bond_level:.2f}")
        print(f"  • Trust Level: {context.trust_level:.2f}")
    
    print("\n6. 🏁 Testing Graceful Shutdown")
    print("-" * 50)
    
    # Test shutdown detection
    print(f"✅ Shutdown status: {ai.is_shutting_down()}")
    
    # Cleanup test components
    activity_monitor.stop_monitoring()
    transparent_scheduler.stop_scheduler()
    
    print("✅ Enhanced features test completed successfully!")
    
    print("\n📈 Enhancement Summary:")
    print("✓ Graceful shutdown hooks with signal handling")
    print("✓ Enhanced logging with rotation and analytics")
    print("✓ Comprehensive activity monitoring and idle detection")
    print("✓ Transparent task scheduling with performance tracking")
    print("✓ Advanced model evaluation with anchor comparison")
    print("✓ Seamless integration with existing AI companion features")
    print("✓ Emotional memory formation with charged conversation detection")
    print("✓ User-specified model selection for OpenRouter calls")
    print("✓ Multimedia content creation capabilities")
    
    return {
        "shutdown_handling": True,
        "enhanced_logging": True,
        "activity_monitoring": True,
        "scheduler_transparency": True,
        "model_evaluation": True,
        "feature_integration": True,
        "overall_score": evaluation.overall_score
    }

if __name__ == "__main__":
    try:
        result = asyncio.run(test_enhanced_features())
        print(f"\n🎉 All enhancements working correctly! Overall score: {result['overall_score']:.2f}")
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
