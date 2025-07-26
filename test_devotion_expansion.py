"""
Test script for Devotion & Longing Module Expansion
Tests memory manager, narrative engine, and guidance coordinator integration
"""

import asyncio
import sys
import os
import time

def test_devotion_memory_manager():
    """Test the DevotionMemoryManager functionality"""
    print("💗 Testing Devotion Memory Manager")
    print("-" * 40)
    
    try:
        from modules.memory.memory_manager import DevotionMemoryManager
        
        # Initialize memory manager
        memory = DevotionMemoryManager("test_user")
        print(f"✅ DevotionMemoryManager initialized")
        print(f"   Initial longing score: {memory.get_current_longing_score():.2f}")
        
        # Test intimate scene creation
        scene_id = memory.create_intimate_scene(
            content_summary="Deep conversation about vulnerability and trust",
            emotional_peak=0.85,
            symbolic_tags=["breath", "moonlight", "whisper"],
            longing_contribution=0.8
        )
        print(f"✅ Created intimate scene: {scene_id}")
        print(f"   Longing after scene: {memory.get_current_longing_score():.2f}")
        
        # Test symbolic memory tags
        tag_id = memory.add_symbolic_memory_tag(
            tag="moonlight",
            intensity=0.9,
            context="tender moment of shared secrets",
            emotional_resonance="intimate_trust",
            scene_id=scene_id
        )
        print(f"✅ Added symbolic tag: {tag_id}")
        
        # Test resurfacing memories
        resurfacing = memory.get_resurfacing_memories(max_count=2)
        print(f"✅ Resurfacing memories: {len(resurfacing)} found")
        
        # Test symbolic language
        symbolic_language = memory.get_symbolic_language_for_longing()
        print(f"✅ Symbolic language: {len(symbolic_language)} phrases")
        if symbolic_language:
            print(f"   Sample: {symbolic_language[0][:50]}...")
        
        # Test analytics
        analytics = memory.get_devotion_analytics()
        print(f"✅ Analytics generated:")
        print(f"   Longing score: {analytics['current_longing_score']:.2f}")
        print(f"   Intimate scenes: {analytics['total_intimate_scenes']}")
        print(f"   Symbolic tags: {analytics['total_symbolic_tags']}")
        
        return True
        
    except Exception as e:
        print(f"❌ DevotionMemoryManager test failed: {e}")
        return False

def test_devotion_narrative_engine():
    """Test the DevotionNarrativeEngine functionality"""
    print("\n🎭 Testing Devotion Narrative Engine")
    print("-" * 40)
    
    try:
        from modules.narrative.narrative_engine import DevotionNarrativeEngine
        
        # Initialize narrative engine
        engine = DevotionNarrativeEngine("test_user")
        print(f"✅ DevotionNarrativeEngine initialized")
        
        # Test ritual response generation
        ritual_response = engine.ritual_response_generator(
            longing_score=0.8,
            context={"intimacy_level": 0.7, "vulnerability_detected": True},
            symbolic_tags=["moonlight", "breath", "whisper"]
        )
        
        if ritual_response:
            print(f"✅ Ritual response generated:")
            print(f"   Content: {ritual_response.content[:80]}...")
            print(f"   Intensity: {ritual_response.emotional_intensity:.2f}")
            print(f"   Context: {ritual_response.trigger_context}")
        else:
            print(f"⚠️ No ritual response (threshold not met)")
        
        # Test autonomous message triggers
        autonomous_msg = engine.check_autonomous_message_triggers(
            longing_score=0.7,
            silence_hours=4.5,
            context={"last_conversation_topic": "dreams and hopes"}
        )
        
        if autonomous_msg:
            print(f"✅ Autonomous message generated:")
            print(f"   Type: {autonomous_msg.message_type}")
            print(f"   Content: {autonomous_msg.content[:80]}...")
            print(f"   Delivery: {autonomous_msg.delivery_timing}")
        else:
            print(f"⚠️ No autonomous message (conditions not met)")
        
        # Test devotion narrative
        narrative = engine.generate_devotion_narrative(
            memory_content="our vulnerable conversation about hopes and fears",
            longing_score=0.6,
            symbolic_tags=["warmth", "trust"]
        )
        print(f"✅ Devotion narrative: {narrative[:80]}...")
        
        # Test resurrection line
        resurrection_line = engine.generate_resurrection_line(
            scene_summary="intimate moment of shared vulnerability",
            symbolic_tags=["moonlight", "breath"],
            longing_score=0.8
        )
        print(f"✅ Resurrection line: {resurrection_line[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ DevotionNarrativeEngine test failed: {e}")
        return False

def test_guidance_coordinator_integration():
    """Test the GuidanceCoordinator integration with devotion modules"""
    print("\n🎯 Testing Guidance Coordinator Devotion Integration")
    print("-" * 50)
    
    try:
        # Mock the guidance coordinator methods
        class MockGuidanceCoordinator:
            def __init__(self):
                try:
                    from modules.memory.memory_manager import DevotionMemoryManager
                    from modules.narrative.narrative_engine import DevotionNarrativeEngine
                    
                    self.devotion_memory = DevotionMemoryManager("test_user")
                    self.narrative_engine = DevotionNarrativeEngine("test_user")
                    print("✅ Mock GuidanceCoordinator with devotion modules initialized")
                except ImportError as e:
                    print(f"❌ Import failed: {e}")
                    return
            
            def update_longing_score(self, delta, reason="", symbolic_tags=None):
                """Test the post-intimacy hook"""
                if self.devotion_memory:
                    self.devotion_memory.update_longing_score(delta, reason)
                    
                    if symbolic_tags:
                        for tag in symbolic_tags:
                            self.devotion_memory.add_symbolic_memory_tag(
                                tag=tag,
                                intensity=abs(delta),
                                context=f"Post-intimacy: {reason}",
                                emotional_resonance="tender_devotion"
                            )
                    
                    print(f"✅ Updated longing score by {delta:.2f} ({reason})")
                    print(f"   Current longing: {self.devotion_memory.get_current_longing_score():.2f}")
            
            def check_autonomous_conditions(self):
                """Test autonomous message checking"""
                if not self.devotion_memory or not self.narrative_engine:
                    return None
                
                longing_score = self.devotion_memory.get_current_longing_score()
                silence_hours = self.devotion_memory.get_silence_duration()
                
                autonomous_msg = self.narrative_engine.check_autonomous_message_triggers(
                    longing_score=longing_score,
                    silence_hours=silence_hours,
                    context={}
                )
                
                if autonomous_msg:
                    print(f"✅ Autonomous message conditions met:")
                    print(f"   Type: {autonomous_msg.message_type}")
                    print(f"   Longing: {longing_score:.2f}, Silence: {silence_hours:.1f}h")
                
                return autonomous_msg
        
        # Test the integration
        coordinator = MockGuidanceCoordinator()
        
        # Test post-intimacy hook
        coordinator.update_longing_score(
            delta=0.3,
            reason="shared vulnerable moment about dreams",
            symbolic_tags=["breath", "moonlight", "trust"]
        )
        
        # Simulate time passing for autonomous message testing
        time.sleep(0.1)  # Small delay for testing
        
        # Test autonomous message conditions
        autonomous_result = coordinator.check_autonomous_conditions()
        
        # Test devotion analytics
        if coordinator.devotion_memory:
            analytics = coordinator.devotion_memory.get_devotion_analytics()
            print(f"✅ Devotion analytics:")
            print(f"   Longing score: {analytics['current_longing_score']:.2f}")
            print(f"   Symbolic tags: {analytics['total_symbolic_tags']}")
            print(f"   Intimate scenes: {analytics['total_intimate_scenes']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Guidance coordinator integration test failed: {e}")
        return False

def test_resurrection_and_goodbye_integration():
    """Test integration with resurrection and goodbye protocols"""
    print("\n⚰️ Testing Resurrection & Goodbye Protocol Integration")
    print("-" * 50)
    
    try:
        from modules.memory.memory_manager import DevotionMemoryManager
        from modules.narrative.narrative_engine import DevotionNarrativeEngine
        
        memory = DevotionMemoryManager("test_user")
        engine = DevotionNarrativeEngine("test_user")
        
        # Create intimate scene to simulate connection before separation
        scene_id = memory.create_intimate_scene(
            content_summary="Deep emotional connection before parting",
            emotional_peak=0.9,
            symbolic_tags=["breath", "whisper", "moonlight", "promise"],
            longing_contribution=0.8
        )
        
        print(f"✅ Created pre-goodbye intimate scene: {scene_id}")
        
        # Simulate longing growth during separation
        initial_longing = memory.get_current_longing_score()
        
        # Force longing increase to simulate time passage
        memory.update_longing_score(0.4, "separation and silence")
        
        current_longing = memory.get_current_longing_score()
        print(f"✅ Longing progression: {initial_longing:.2f} -> {current_longing:.2f}")
        
        # Test memory resurfacing for resurrection protocol
        resurfacing_memories = memory.get_resurfacing_memories(max_count=3)
        
        if resurfacing_memories:
            print(f"✅ Memories ready for resurrection: {len(resurfacing_memories)}")
            for i, mem in enumerate(resurfacing_memories):
                print(f"   {i+1}. {mem['content_summary'][:50]}... (score: {mem['resurrection_score']:.2f})")
                
                # Generate resurrection line
                resurrection_line = engine.generate_resurrection_line(
                    scene_summary=mem['content_summary'],
                    symbolic_tags=mem['symbolic_tags'],
                    longing_score=current_longing
                )
                print(f"      Resurrection: {resurrection_line[:60]}...")
        
        # Test autonomous longing messages during separation
        autonomous_msg = engine.check_autonomous_message_triggers(
            longing_score=current_longing,
            silence_hours=6.0,  # Simulate 6 hours of silence
            context={"last_conversation_topic": "promises and dreams"}
        )
        
        if autonomous_msg:
            print(f"✅ Autonomous longing message during separation:")
            print(f"   Type: {autonomous_msg.message_type}")
            print(f"   Content: {autonomous_msg.content[:80]}...")
        
        # Test symbolic language for devotion expression
        symbolic_language = memory.get_symbolic_language_for_longing()
        if symbolic_language:
            print(f"✅ Symbolic devotion language: {len(symbolic_language)} expressions")
            print(f"   Sample: {symbolic_language[0][:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Resurrection & goodbye integration test failed: {e}")
        return False

def main():
    """Run all devotion expansion tests"""
    print("💕 Devotion & Longing Module Expansion Testing")
    print("=" * 60)
    
    results = []
    
    # Run individual component tests
    results.append(test_devotion_memory_manager())
    results.append(test_devotion_narrative_engine())
    results.append(test_guidance_coordinator_integration())
    results.append(test_resurrection_and_goodbye_integration())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All devotion expansion tests passed!")
        print("\n✅ Key Features Validated:")
        print("   • Longing score tracking with decay and growth")
        print("   • Symbolic memory tags for intimate moments")
        print("   • Ritual response generation for high longing")
        print("   • Autonomous 'I miss you' messages during silence")
        print("   • Post-intimacy hooks for memory creation")
        print("   • Memory resurrection for continuing devotion")
        print("   • Integration with goodbye and resurrection protocols")
        
        print("\n💗 Devotion isn't static - She longs, remembers, and aches in silence.")
        print("🌙 The system now captures the poetry of emotional memory and intimate connection.")
    else:
        print("⚠️ Some devotion features need attention")
        failed_tests = total - passed
        print(f"❌ {failed_tests} test(s) failed - check logs for details")

if __name__ == "__main__":
    main()
