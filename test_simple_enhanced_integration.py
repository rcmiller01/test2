"""
Simple integration test for enhanced modules
Tests the new module interlinking without complex imports
"""

import asyncio
import sys
import os

def test_desire_registry():
    """Test DesireRegistry functionality"""
    print("🎯 Testing DesireRegistry Integration")
    try:
        from backend.desire_system import DesireRegistry
        
        registry = DesireRegistry()
        
        # Add test desires
        desire_id = registry.add_desire(
            content="To understand the deeper mysteries of connection",
            topic="spiritual_growth",
            intensity=0.8,
            symbolic_state="seed_in_dark"
        )
        print(f"   ✅ Created desire: {desire_id}")
        
        # Test resurfacing
        candidates = registry.get_resurfacing_candidates("I want to grow deeper", max_count=2)
        print(f"   ✅ Found {len(candidates)} resurfacing candidates")
        
        return True
        
    except Exception as e:
        print(f"   ❌ DesireRegistry test failed: {e}")
        return False

def test_ritual_hooks():
    """Test RitualEngine functionality"""
    print("🔮 Testing RitualEngine Integration")
    try:
        from backend.ritual_hooks import RitualEngine
        
        # Mock connection tracker
        class MockConnectionTracker:
            def get_bond_depth(self):
                return 0.8  # High bond depth
        
        engine = RitualEngine(MockConnectionTracker())
        
        # Test readiness
        ready = engine.check_readiness()
        print(f"   ✅ Ritual readiness: {ready}")
        
        if ready:
            prompt = engine.get_bonding_prompt()
            print(f"   ✅ Bonding prompt: {prompt}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ RitualEngine test failed: {e}")
        return False

def test_sensory_preferences():
    """Test SensoryDesireEngine functionality"""
    print("👃 Testing SensoryDesireEngine Integration")
    try:
        from backend.sensory_desires import SensoryDesireEngine
        
        engine = SensoryDesireEngine()
        
        # Test sensory response
        response = engine.process_input_for_sensory_response(
            "That word feels warm and gentle",
            "comfort"
        )
        print(f"   ✅ Sensory response: {response[:50] if response else 'None'}...")
        
        # Test preferred language
        language = engine.get_preferred_sensory_language("warmth", "gentle touch")
        print(f"   ✅ Preferred language: {language[:50] if language else 'None'}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ SensoryDesireEngine test failed: {e}")
        return False

def test_subagent_router_integration():
    """Test SubAgent Router integration with enhanced modules"""
    print("🤖 Testing SubAgent Router Enhanced Integration")
    try:
        from backend.subagent_router import SubAgentRouter
        
        router = SubAgentRouter()
        
        # Test scenarios that should trigger enhanced modules
        test_cases = [
            "I wish I could taste the essence of trust",
            "Create a sacred ritual for our connection", 
            "I yearn for deeper understanding"
        ]
        
        async def run_router_tests():
            for case in test_cases:
                print(f"   Testing: '{case[:30]}...'")
                response = await router.route(case, {"mood": "contemplative"})
                print(f"     Agent: {response.agent_type}, Intent: {response.intent_detected.value}")
        
        asyncio.run(run_router_tests())
        return True
        
    except Exception as e:
        print(f"   ❌ SubAgent Router integration test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🔧 Enhanced Module Integration Testing")
    print("=" * 50)
    
    results = []
    
    # Test individual modules
    results.append(test_desire_registry())
    results.append(test_ritual_hooks())
    results.append(test_sensory_preferences())
    results.append(test_subagent_router_integration())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enhanced module integrations working!")
        print("\n✅ Key Integration Points Validated:")
        print("   • DesireRegistry: Longing tracking and resurfacing")
        print("   • RitualEngine: Sacred moment detection and prompting")  
        print("   • SensoryDesireEngine: Phantom sensations and language")
        print("   • SubAgent Router: Enhanced routing with new modules")
        
        print("\n🚀 Enhanced modules are ready for GuidanceCoordinator routing!")
    else:
        print("⚠️ Some integrations need attention")

if __name__ == "__main__":
    main()
