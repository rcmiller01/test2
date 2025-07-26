"""
Test script for enhanced GuidanceCoordinator with new module interlinking
Tests desire_registry, ritual_hooks, and sensory_preferences integration
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_enhanced_guidance_coordinator():
    """Test the enhanced GuidanceCoordinator with new module routing"""
    print("🧪 Testing Enhanced GuidanceCoordinator Integration")
    print("=" * 60)
    
    try:
        from modules.core.guidance_coordinator import GuidanceCoordinator
        
        # Initialize coordinator
        coordinator = GuidanceCoordinator("test_user")
        print(f"✅ GuidanceCoordinator initialized")
        
        # Test scenarios
        test_scenarios = [
            {
                "input": "I wish I could understand what love really means",
                "context": {"mood": "contemplative", "conversation_depth": 0.6},
                "expected_modules": ["desire_system"]
            },
            {
                "input": "Can we create something sacred together?",
                "context": {"mood": "intimate", "conversation_depth": 0.9},
                "expected_modules": ["ritual_hooks"]
            },
            {
                "input": "That word tastes like honey and warmth",
                "context": {"mood": "creative", "emotional_intensity": 0.7},
                "expected_modules": ["sensory_preferences"]
            },
            {
                "input": "I yearn for deeper connection with sacred trust",
                "context": {"mood": "vulnerable", "conversation_depth": 0.8},
                "expected_modules": ["desire_system", "ritual_hooks", "sensory_preferences"]
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🔍 Test Scenario {i}: {scenario['input'][:40]}...")
            
            try:
                guidance = await coordinator.analyze_and_guide(
                    scenario["input"], 
                    scenario["context"]
                )
                
                print(f"   ✅ Guidance generated successfully")
                print(f"   Primary mode: {guidance.primary_mode}")
                print(f"   Response tone: {guidance.response_tone}")
                print(f"   Emotional priority: {guidance.emotional_priority}")
                
                # Check for enhanced module guidance
                enhanced_guidance_found = []
                if 'desire_guidance' in guidance.mode_specifics:
                    enhanced_guidance_found.append("desire_system")
                    print(f"   🎯 Desire guidance: {len(guidance.mode_specifics['desire_guidance'].get('active_longings', []))} longings detected")
                
                if 'ritual_guidance' in guidance.mode_specifics:
                    enhanced_guidance_found.append("ritual_hooks")
                    ritual_ready = guidance.mode_specifics['ritual_guidance'].get('ready', False)
                    print(f"   🔮 Ritual guidance: {'Ready' if ritual_ready else 'Not ready'}")
                
                if 'sensory_guidance' in guidance.mode_specifics:
                    enhanced_guidance_found.append("sensory_preferences")
                    sensory_response = guidance.mode_specifics['sensory_guidance'].get('sensory_response')
                    print(f"   👃 Sensory guidance: {'Response generated' if sensory_response else 'No specific response'}")
                
                # Utility recommendations
                if guidance.utility_recommendations:
                    print(f"   💡 Utility recommendations: {', '.join(guidance.utility_recommendations)}")
                
                # Validate expected modules
                expected = set(scenario["expected_modules"])
                found = set(enhanced_guidance_found)
                if expected.issubset(found):
                    print(f"   ✅ Expected modules activated: {', '.join(expected)}")
                else:
                    missing = expected - found
                    print(f"   ⚠️ Missing expected modules: {', '.join(missing)}")
                
            except Exception as e:
                print(f"   ❌ Scenario failed: {e}")
        
        # Test analytics
        print(f"\n📊 System Analytics:")
        available_modules = []
        if hasattr(coordinator, 'desire_registry') and coordinator.desire_registry:
            available_modules.append("desire_registry")
        if hasattr(coordinator, 'ritual_engine') and coordinator.ritual_engine:
            available_modules.append("ritual_engine")
        if hasattr(coordinator, 'sensory_preferences') and coordinator.sensory_preferences:
            available_modules.append("sensory_preferences")
        
        print(f"   Available enhanced modules: {', '.join(available_modules)}")
        
        print(f"\n🎉 Enhanced GuidanceCoordinator integration test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Some modules may not be available")
    except Exception as e:
        print(f"❌ Test failed: {e}")

async def test_module_availability():
    """Test individual module availability"""
    print("\n🔧 Testing Module Availability")
    print("-" * 40)
    
    modules_to_test = [
        ("backend.desire_system", "DesireRegistry"),
        ("backend.ritual_hooks", "RitualEngine"),
        ("backend.sensory_desires", "SensoryDesireEngine")
    ]
    
    for module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"   ✅ {module_path}.{class_name} - Available")
            
            # Try to instantiate
            if class_name == "RitualEngine":
                # Mock connection tracker
                class MockTracker:
                    def get_bond_depth(self):
                        return 0.5
                instance = cls(MockTracker())
            else:
                instance = cls()
            print(f"      Instantiation: Success")
            
        except ImportError:
            print(f"   ❌ {module_path}.{class_name} - Not available")
        except Exception as e:
            print(f"   ⚠️ {module_path}.{class_name} - Available but error: {e}")

if __name__ == "__main__":
    asyncio.run(test_module_availability())
    asyncio.run(test_enhanced_guidance_coordinator())
