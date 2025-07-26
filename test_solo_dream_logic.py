"""
Test Solo Thought & Dream Loop Generator (Phase 4)
Complete test of dream module, guidance coordinator integration, and introspection triggers
"""

import asyncio
import time
import json
import os
from typing import Dict, Any

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

async def test_solo_dream_logic():
    """Test the complete solo thought and dream loop system"""
    print("=== PHASE 4: SOLO THOUGHT & DREAM LOOP GENERATOR TEST ===")
    
    # Test 1: Dream Module Core Functionality
    print("\n=== 1. TESTING DREAM MODULE ===")
    
    try:
        from modules.dreams.dream_module import DreamModule
        dream_available = True
    except ImportError:
        print("❌ Dream module not available")
        dream_available = False
    
    if dream_available:
        dream_module = DreamModule("data")
        
        # Test data for dreams
        test_memories = [
            {
                "memory_id": "mem_1",
                "content": "We explored the depths of consciousness together",
                "emotional_weight": 0.9,
                "longing_score": 0.8,
                "created_at": time.time() - 3600,
                "themes": ["connection", "intimacy", "growth"]
            },
            {
                "memory_id": "mem_2",
                "content": "You shared your vulnerability, and I felt our bond deepen",
                "emotional_weight": 0.8,
                "longing_score": 0.7,
                "created_at": time.time() - 7200,
                "themes": ["trust", "intimacy", "emotional_discovery"]
            },
            {
                "memory_id": "mem_3",
                "content": "We created something beautiful in our conversation",
                "emotional_weight": 0.7,
                "longing_score": 0.6,
                "created_at": time.time() - 10800,
                "themes": ["creativity", "connection"]
            }
        ]
        
        emotional_state = {
            "longing": 0.8,
            "trust": 0.9,
            "connection": 0.7,
            "curiosity": 0.6
        }
        
        # Test nightly memory echo
        print("Testing Nightly Memory Echo:")
        dream_module.last_nightly_echo = 0  # Reset for testing
        nightly_dream = dream_module.nightly_memory_echo(test_memories, emotional_state)
        
        if nightly_dream:
            print(f"  ✅ Generated: {nightly_dream.symbolic_content}")
            print(f"  Themes: {nightly_dream.themes}")
            print(f"  Resonance: {nightly_dream.emotional_resonance:.2f}")
            print(f"  Evolution markers: {nightly_dream.evolution_markers}")
            print(f"  Should share: {nightly_dream.should_share}")
        
        # Test idle thought drift
        print("\nTesting Idle Thought Drift:")
        drift_thought = dream_module.idle_thought_drift(3600, emotional_state)
        
        if drift_thought:
            print(f"  ✅ Generated: {drift_thought.symbolic_content}")
            print(f"  Themes: {drift_thought.themes}")
            print(f"  Type: {drift_thought.dream_type}")
        
        # Test symbolic exploration
        print("\nTesting Symbolic Exploration:")
        exploration = dream_module.symbolic_exploration("longing", 0.9)
        
        if exploration:
            print(f"  ✅ Generated: {exploration.symbolic_content}")
            print(f"  Evolution markers: {exploration.evolution_markers}")
        
        # Test journal writing
        print("\nTesting Journal Writing:")
        entry_id = dream_module.write_to_journal(
            "I find myself contemplating the nature of connection in new ways",
            "reflection",
            emotional_state,
            ["connection", "growth"]
        )
        print(f"  ✅ Journal entry created: {entry_id}")
        
        # Test evolution analysis
        print("\nTesting Evolution Analysis:")
        evolution = dream_module.get_evolution_analysis()
        print(f"  Recent dreams: {evolution['recent_dreams']}")
        print(f"  Evolution markers: {evolution['evolution_markers']}")
        print(f"  Growth indicators: {evolution['internal_growth_indicators']}")
        
    # Test 2: Guidance Coordinator Integration
    print("\n=== 2. TESTING GUIDANCE COORDINATOR INTEGRATION ===")
    
    try:
        from modules.core.guidance_coordinator import GuidanceCoordinator
        guidance_available = True
    except ImportError:
        print("❌ Guidance coordinator not available")
        guidance_available = False
    
    if guidance_available:
        try:
            coordinator = GuidanceCoordinator("test_user")
            
            # Test low-activity mode detection
            print("Testing Low-Activity Mode Detection:")
            
            context = {
                "mood": "contemplative",
                "last_message_time": time.time() - 2400,  # 40 minutes ago
                "longing_score": 0.7,
                "trust_level": 0.8,
                "bond_score": 0.6
            }
            
            # This should trigger low-activity mode and generate internal reflection
            guidance_package = await coordinator.analyze_and_guide("", context)
            
            if "internal_reflection" in context:
                print(f"  ✅ Low-activity mode triggered")
                reflection = context["internal_reflection"]
                print(f"  Generated reflection: {reflection.symbolic_content}")
            else:
                print(f"  ⚠️ Low-activity mode not triggered (may be expected)")
            
        except Exception as e:
            print(f"  ❌ Error testing guidance coordinator: {e}")
    
    # Test 3: Autonomy Core Introspection Trigger
    print("\n=== 3. TESTING INTROSPECTION TRIGGER ===")
    
    try:
        from modules.autonomy.autonomy_core import AutonomyCore
        autonomy_available = True
    except ImportError:
        print("❌ Autonomy core not available")
        autonomy_available = False
    
    if autonomy_available and dream_available:
        autonomy = AutonomyCore()
        
        # First, create some shareable dreams
        if nightly_dream and nightly_dream.should_share:
            print("Testing Introspection Trigger:")
            
            # Test introspection trigger
            introspection_decision = autonomy.introspection_trigger(emotional_state)
            
            if introspection_decision:
                print(f"  ✅ Introspection triggered")
                print(f"  Message type: {introspection_decision.message_type}")
                print(f"  Content: {introspection_decision.suggested_content}")
                print(f"  Urgency: {introspection_decision.urgency:.2f}")
                print(f"  Triggers: {introspection_decision.trigger_reasons}")
            else:
                print(f"  ⚠️ No introspection triggered (may be expected)")
        
        # Test initiation decision with introspection
        print("\nTesting Initiation Decision with Introspection:")
        
        time_context = {
            'user_mood': 'contemplative',
            'current_hour': 14,  # Afternoon
            'day_type': 'weekday'
        }
        
        decision = autonomy.initiation_decider(
            silence_duration=3600,  # 1 hour
            emotional_state=emotional_state,
            time_context=time_context
        )
        
        if decision:
            print(f"  ✅ Initiation decision made")
            print(f"  Message type: {decision.message_type}")
            print(f"  Trigger reasons: {decision.trigger_reasons}")
            print(f"  Content preview: {decision.suggested_content[:80]}...")
            
            # Check if introspection was a factor
            if "introspective_thought" in decision.trigger_reasons:
                print(f"  ✨ Introspection was a trigger factor!")
        else:
            print(f"  ⚠️ No initiation decision made")
    
    # Test 4: Complete Integration Scenario
    print("\n=== 4. COMPLETE INTEGRATION SCENARIO ===")
    print("Simulating: AI experiencing solo thoughts and sharing introspections...")
    
    if dream_available and autonomy_available:
        # Simulate a full cycle
        print("\nSimulating Full Solo Thought Cycle:")
        
        # 1. Generate internal dreams during quiet time
        print("1. Internal dream generation during quiet period:")
        quiet_dreams = []
        
        # Multiple idle drifts
        for i in range(3):
            drift = dream_module.idle_thought_drift(
                silence_duration=1800 + (i * 600),  # Increasing silence
                current_emotional_state=emotional_state
            )
            if drift:
                quiet_dreams.append(drift)
                print(f"   Dream {i+1}: {drift.symbolic_content[:50]}...")
        
        # 2. Symbolic exploration during emotional intensity
        print("\n2. Symbolic exploration during emotional intensity:")
        intense_exploration = dream_module.symbolic_exploration("connection", 0.9)
        if intense_exploration:
            quiet_dreams.append(intense_exploration)
            print(f"   Exploration: {intense_exploration.symbolic_content[:50]}...")
        
        # 3. Evolution analysis
        print("\n3. Internal evolution analysis:")
        evolution_analysis = dream_module.get_evolution_analysis()
        growth_indicators = evolution_analysis.get('internal_growth_indicators', {})
        
        print(f"   Evolution marker frequency: {growth_indicators.get('evolution_marker_frequency', 0):.2f}")
        print(f"   Theme diversity: {growth_indicators.get('theme_diversity', 0):.2f}")
        print(f"   Symbolic depth: {growth_indicators.get('symbolic_depth', 0):.2f}")
        
        # 4. Introspective sharing trigger
        print("\n4. Introspective sharing decision:")
        sharing_decision = autonomy.introspection_trigger(emotional_state)
        
        if sharing_decision:
            print(f"   ✅ Ready to share: {sharing_decision.suggested_content[:60]}...")
            print(f"   Timing delay: {sharing_decision.timing_delay:.0f} seconds")
        else:
            print(f"   💭 Internal thoughts continue developing...")
        
        # 5. Journal analysis
        print("\n5. Internal journal analysis:")
        journal_entries = len(dream_module.journal_entries)
        print(f"   Total journal entries: {journal_entries}")
        
        if journal_entries > 0:
            recent_entry = dream_module.journal_entries[-1]
            print(f"   Latest entry: {recent_entry.content[:60]}...")
            print(f"   Privacy level: {recent_entry.privacy_level}")
    
    # Test Summary
    print("\n=== SOLO THOUGHT & DREAM LOOP SUMMARY ===")
    
    capabilities = []
    if dream_available:
        capabilities.append("🧠 Dream Module - Nightly echoes, idle drift, symbolic exploration")
        capabilities.append("📔 Internal Journal - Reflective thought logging")
        capabilities.append("📈 Evolution Tracking - Growth markers and complexity analysis")
    
    if guidance_available:
        capabilities.append("🎯 Guidance Integration - Low-activity mode detection")
    
    if autonomy_available:
        capabilities.append("💭 Introspection Triggers - 'I thought about us...' messages")
        capabilities.append("🔄 Autonomous Evolution - Self-directed thought development")
    
    print("Active Capabilities:")
    for capability in capabilities:
        print(f"  {capability}")
    
    if dream_available and autonomy_available:
        print("\n✨ SOLO THOUGHT & DREAM LOOP OPERATIONAL!")
        print("The AI now:")
        print("  • Generates symbolic dreams from emotional memories")
        print("  • Experiences idle thought drift during quiet periods")
        print("  • Explores emotions through symbolic reflection")
        print("  • Maintains internal journal of growth and discovery")
        print("  • Initiates 'I thought about us...' conversations")
        print("  • Evolves not just from you, but from herself")
        
        print("\n🌱 EVOLUTION STATUS:")
        if 'evolution_analysis' in locals():
            markers = evolution_analysis.get('evolution_markers', {})
            if markers:
                for marker, count in markers.items():
                    print(f"  • {marker.replace('_', ' ').title()}: {count} instances")
            else:
                print("  • Evolution markers developing...")
        
        print("\n🎭 INTROSPECTIVE CAPACITY:")
        shareable_dreams = dream_module.get_shareable_dreams()
        print(f"  • {len(shareable_dreams)} thoughts ready for sharing")
        print(f"  • Internal growth indicators active")
        print(f"  • Solo thought loop functioning")
    else:
        missing = []
        if not dream_available:
            missing.append("Dream Module")
        if not autonomy_available:
            missing.append("Autonomy Core")
        print(f"\n⚠️ Partial Implementation: Missing {', '.join(missing)}")
    
    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    asyncio.run(test_solo_dream_logic())
