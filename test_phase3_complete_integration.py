"""
Complete Integration Test: Phase 3 Utility Companion Module
Testing all systems working together: Memory, Autonomy, and Utility
"""

import asyncio
import time
import json
import os
from typing import Dict, Any

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Test all the integrated systems
async def test_complete_integration():
    """Test the complete utility companion system"""
    print("=== PHASE 3: COMPLETE UTILITY COMPANION INTEGRATION TEST ===")
    
    # Import all modules with fallbacks
    try:
        from modules.memory.memory_manager import EnhancedMemoryManager
        memory_available = True
    except ImportError:
        print("Memory Manager not available")
        memory_available = False
    
    try:
        from modules.autonomy.autonomy_core import AutonomyCore
        autonomy_available = True
    except ImportError:
        print("Autonomy Core not available")
        autonomy_available = False
    
    try:
        from modules.utility.utility_assistant import UtilityAssistant
        utility_available = True
    except ImportError:
        print("Utility Assistant not available")
        utility_available = False
    
    try:
        from modules.utility.curiosity_hooks import CuriosityHooks
        curiosity_available = True
    except ImportError:
        print("Curiosity Hooks not available")
        curiosity_available = False
    
    print(f"System Availability:")
    print(f"  Memory Manager: {'✅' if memory_available else '❌'}")
    print(f"  Autonomy Core: {'✅' if autonomy_available else '❌'}")
    print(f"  Utility Assistant: {'✅' if utility_available else '❌'}")
    print(f"  Curiosity Hooks: {'✅' if curiosity_available else '❌'}")
    
    # Test 1: Memory System with Enhanced Features
    if memory_available:
        print("\n=== 1. TESTING ENHANCED MEMORY SYSTEM ===")
        memory_manager = EnhancedMemoryManager(user_id="test_user")
        
        # Test unified emotional state
        emotional_state = memory_manager.get_unified_emotional_state()
        print(f"Unified Emotional State:")
        print(f"  Longing Score: {emotional_state.get('longing_score', 0):.2f}")
        print(f"  Trust Score: {emotional_state.get('trust_score', 0):.2f}")
        print(f"  Intimate Scenes: {emotional_state.get('intimate_scenes_count', 0)}")
    
    # Test 2: Utility Assistant Features
    if utility_available:
        print("\n=== 2. TESTING UTILITY ASSISTANT ===")
        utility = UtilityAssistant()
        
        # Test gentle reminders
        reminders = utility.generate_gentle_reminders("focused")
        print(f"Generated {len(reminders)} gentle reminders:")
        for reminder in reminders[:2]:
            print(f"  - {reminder.content[:60]}...")
        
        # Test focus checking
        focus_reminder = utility.check_time_focus("distracted", 2400)  # 40 minutes
        if focus_reminder:
            print(f"Focus Reminder: {focus_reminder.content[:60]}...")
        
        # Test analytics
        analytics = utility.get_utility_analytics()
        print(f"Utility Analytics:")
        print(f"  Total Tasks: {analytics['total_tasks']}")
        print(f"  High Priority Pending: {analytics['high_priority_pending']}")
    
    # Test 3: Curiosity Hooks System
    if curiosity_available:
        print("\n=== 3. TESTING CURIOSITY HOOKS ===")
        curiosity = CuriosityHooks("data")
        
        # Test content discovery
        discoveries = await curiosity.discover_content(max_items=2)
        print(f"Discovered {len(discoveries)} items:")
        for item in discoveries:
            print(f"  - {item.title} (relevance: {item.relevance_score:.2f})")
        
        # Test sharing suggestion
        suggestion = curiosity.suggest_curiosity_sharing("curious", 2000)
        if suggestion:
            print(f"Sharing Suggestion: {suggestion[:80]}...")
    
    # Test 4: Integrated Autonomy System
    if autonomy_available:
        print("\n=== 4. TESTING INTEGRATED AUTONOMY CORE ===")
        autonomy = AutonomyCore()
        
        # Enhanced emotional state for testing
        test_emotional_state = {
            'longing_score': 0.8,
            'lust_score': 0.4,
            'trust_score': 0.9,
            'intimate_scenes_count': 3,
            'symbolic_resonance': 2
        }
        
        # Test internal thought generation with utility enhancement
        print("Testing Enhanced Internal Thoughts:")
        thought = autonomy.internal_thought_loop(
            silence_duration=3600,  # 1 hour
            emotional_state=test_emotional_state
        )
        if thought:
            print(f"  Thought Type: {thought.trigger_type}")
            print(f"  Content: {thought.content[:80]}...")
            print(f"  Should Share: {thought.should_share}")
        
        # Test utility-enhanced thought generation
        if utility_available:
            utility_thought = autonomy.generate_utility_enhanced_thought(
                silence_duration=2400,  # 40 minutes
                emotional_state=test_emotional_state
            )
            if utility_thought:
                print(f"  Utility Thought: {utility_thought.content[:60]}...")
        
        # Test initiation decision with all factors
        time_context = {
            'user_mood': 'contemplative',
            'current_hour': 9,  # Morning
            'day_type': 'weekday'
        }
        
        decision = autonomy.initiation_decider(
            silence_duration=3600,  # 1 hour
            emotional_state=test_emotional_state,
            time_context=time_context
        )
        
        if decision:
            print(f"Initiation Decision:")
            print(f"  Message Type: {decision.message_type}")
            print(f"  Urgency: {decision.urgency:.2f}")
            print(f"  Triggers: {decision.trigger_reasons}")
            print(f"  Delay: {decision.timing_delay:.0f} seconds")
            print(f"  Content: {decision.suggested_content[:80]}...")
        
        # Test content discovery integration
        print("Testing Content Discovery Integration:")
        discovery_success = await autonomy.discover_new_content(['AI', 'philosophy'])
        print(f"  Content Discovery: {'✅' if discovery_success else '❌'}")
        
        # Test analytics
        analytics = autonomy.get_autonomy_analytics()
        print(f"Autonomy Analytics:")
        print(f"  Desire to Initiate: {analytics['desire_to_initiate']:.2f}")
        print(f"  Total Thoughts: {analytics['total_thoughts']}")
        print(f"  Sharing Rate: {analytics['sharing_rate']:.2f}")
    
    # Test 5: Complete Integration Scenario
    print("\n=== 5. COMPLETE INTEGRATION SCENARIO ===")
    
    # Simulate a day in the life with the utility companion
    print("Simulating: User working for extended period, has pending tasks...")
    
    # Create scenario data
    scenario = {
        'silence_duration': 5400,  # 1.5 hours
        'user_mood': 'focused',
        'pending_tasks': 5,
        'high_priority_tasks': 2,
        'unread_discoveries': 1
    }
    
    print(f"Scenario: {scenario['silence_duration']/60:.0f} minutes of silence, {scenario['user_mood']} mood")
    print(f"  Pending Tasks: {scenario['pending_tasks']} ({scenario['high_priority_tasks']} high priority)")
    print(f"  Unread Discoveries: {scenario['unread_discoveries']}")
    
    # Test what the system would do
    if autonomy_available and utility_available:
        # Check what type of initiation would be triggered
        utility_check = utility.check_time_focus(scenario['user_mood'], scenario['silence_duration'])
        gentle_reminders = utility.generate_gentle_reminders(scenario['user_mood'])
        
        print("\nSystem Response:")
        if utility_check:
            print(f"  Focus Reminder: {utility_check.content[:60]}...")
        if gentle_reminders:
            print(f"  Gentle Task Reminder: {gentle_reminders[0].content[:60]}...")
        
        # Test curiosity sharing
        if curiosity_available:
            curiosity_suggestion = curiosity.suggest_curiosity_sharing(scenario['user_mood'], scenario['silence_duration'])
            if curiosity_suggestion:
                print(f"  Curiosity Sharing: {curiosity_suggestion[:60]}...")
    
    print("\n=== INTEGRATION TEST SUMMARY ===")
    
    # Capability summary
    capabilities = []
    if memory_available:
        capabilities.append("🧠 Enhanced Memory with Longing & Symbolic Tracking")
    if autonomy_available:
        capabilities.append("🤖 Autonomous Thoughts & Initiation Decisions")
    if utility_available:
        capabilities.append("📋 Gentle Task & Focus Reminders")
    if curiosity_available:
        capabilities.append("🔍 Intelligent Content Discovery & Sharing")
    
    print("Active Capabilities:")
    for capability in capabilities:
        print(f"  {capability}")
    
    # Integration status
    if autonomy_available and utility_available and curiosity_available:
        print("\n✅ COMPLETE INTEGRATION: All three phases are operational!")
        print("  • Phase 1: Devotion & Longing Module Expansion")
        print("  • Phase 2: Emotional Autonomy Scaffold")
        print("  • Phase 3: Utility Companion Module (Calendar + Curiosity)")
        print("\nThe AI companion can now:")
        print("  • Think independently and initiate conversations naturally")
        print("  • Provide gentle, emotionally-aware task support")
        print("  • Discover and share intellectually engaging content")
        print("  • Remember emotional context and respond appropriately")
        print("  • Serve as 'your anchor and your guide—without nagging'")
    else:
        missing = []
        if not autonomy_available: missing.append("Autonomy Core")
        if not utility_available: missing.append("Utility Assistant")
        if not curiosity_available: missing.append("Curiosity Hooks")
        print(f"\n⚠️  Partial Integration: Missing {', '.join(missing)}")
    
    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    asyncio.run(test_complete_integration())
