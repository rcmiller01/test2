#!/usr/bin/env python3
"""
Comprehensive Integration Test for AI Companion Enhanced Systems

Tests the integration of all new additions:
- Phase 2: Symbol Binding & Attachment Reinforcement
- Phase 4: Solo Dream Logic & Autonomous Dream Delivery  
- Phase 5: Emotional Broadcast System
- Investment Tracker Integration
- Narrative Agency System
- Presence Signal Broadcasting
"""

import sys
import os
import asyncio
import json
import time
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_comprehensive_integration():
    """Test integration of all enhanced AI companion systems"""
    print("🚀 Comprehensive AI Companion Integration Test")
    print("=" * 60)
    print("Testing all new additions and their interactions...")
    print()
    
    results = {
        "symbol_binding": False,
        "dream_delivery": False,
        "emotional_broadcast": False,
        "investment_tracker": False,
        "narrative_agency": False,
        "presence_signals": False,
        "integration_flow": False
    }
    
    try:
        # Test 1: Symbol Binding System (Phase 2)
        print("🎭 Test 1: Symbol Binding & Attachment Reinforcement")
        print("-" * 50)
        
        from modules.memory.memory_manager import memory_manager
        from modules.memory.attachment_reflector import attachment_reflector
        
        # Create test symbols with emotional context
        memory_manager.bind_symbol_to_emotion(
            symbol="moonlight",
            emotion="serenity", 
            intensity=0.8,
            context="peaceful evening contemplation"
        )
        
        memory_manager.bind_symbol_to_emotion(
            symbol="harmony",
            emotion="contentment",
            intensity=0.9,
            context="perfect balance achieved"
        )
        
        # Test symbol retrieval
        weighted_symbols = memory_manager.get_emotionally_weighted_symbols(minimum_weight=0.3)
        if weighted_symbols:
            print(f"✅ Symbol binding working: {len(weighted_symbols)} symbols tracked")
            print(f"   Symbols: {list(weighted_symbols.keys())}")
            results["symbol_binding"] = True
        else:
            print("❌ Symbol binding failed")
        
        # Test attachment reflection
        landscape = attachment_reflector.get_attachment_landscape()
        if landscape.get("available"):
            print(f"✅ Attachment reflection working: {landscape['total_symbols']} symbols in landscape")
        
        print()
        
        # Test 2: Autonomous Dream Delivery (Phase 4)
        print("🌙 Test 2: Autonomous Dream Delivery System")
        print("-" * 50)
        
        try:
            from modules.dreams.dream_module import get_dream_module
            dream_module = get_dream_module()
            
            # Test dream generation
            if dream_module and hasattr(dream_module, 'generate_autonomous_dream'):
                dream_result = dream_module.generate_autonomous_dream("test_user")
                if dream_result:
                    print("✅ Dream module working: Generated autonomous dream")
                    print(f"   Dream type: {dream_result.get('type', 'unknown')}")
                    results["dream_delivery"] = True
                else:
                    print("⚠️ Dream module available but no dream generated")
            else:
                print("⚠️ Dream module available but missing autonomous dream method")
                
        except Exception as e:
            print(f"❌ Dream delivery test failed: {e}")
        
        print()
        
        # Test 3: Emotional Broadcast System (Phase 5)
        print("📡 Test 3: Emotional Broadcast System")
        print("-" * 50)
        
        try:
            from modules.presence.unified_broadcast import UnifiedPresenceBroadcast
            from modules.presence.presence_signal import PresenceSignal
            
            # Test presence broadcasting
            broadcaster = UnifiedPresenceBroadcast()
            
            # Create test emotional state
            emotional_state = {
                "primary_emotion": "contentment",
                "intensity": 0.7,
                "context": "integration testing",
                "timestamp": datetime.now().isoformat()
            }
            
            # Test broadcast
            signal_sent = broadcaster.broadcast_emotional_presence(emotional_state)
            if signal_sent:
                print("✅ Emotional broadcast working: Signal transmitted")
                results["emotional_broadcast"] = True
            else:
                print("❌ Emotional broadcast failed")
                
        except Exception as e:
            print(f"❌ Emotional broadcast test failed: {e}")
        
        print()
        
        # Test 4: Investment Tracker Integration  
        print("💰 Test 4: Investment Tracker System")
        print("-" * 50)
        
        try:
            # Test investment tracker import
            from demo_investment_tracker import InvestmentTracker
            
            tracker = InvestmentTracker()
            
            # Test basic investment operations
            test_investment = {
                "symbol": "TEST",
                "amount": 1000.0,
                "price": 50.0,
                "type": "integration_test"
            }
            
            success = tracker.add_investment(**test_investment)
            if success:
                print("✅ Investment tracker working: Added test investment")
                
                # Test portfolio retrieval
                portfolio = tracker.get_portfolio_summary()
                if portfolio:
                    print(f"   Portfolio value: ${portfolio.get('total_value', 0):.2f}")
                    results["investment_tracker"] = True
            else:
                print("❌ Investment tracker failed to add investment")
                
        except Exception as e:
            print(f"❌ Investment tracker test failed: {e}")
        
        print()
        
        # Test 5: Narrative Agency System
        print("📖 Test 5: Narrative Agency System")
        print("-" * 50)
        
        try:
            from modules.narrative.narrative_agency import NarrativeAgency
            from modules.narrative.narrative_integration import NarrativeIntegrator
            
            # Test narrative agency
            agency = NarrativeAgency("test_user")
            integrator = NarrativeIntegrator()
            
            # Test narrative generation
            narrative_context = {
                "user_input": "I'm feeling contemplative tonight",
                "emotional_state": "reflective",
                "scene": "quiet evening"
            }
            
            narrative = agency.generate_contextual_narrative(narrative_context)
            if narrative:
                print("✅ Narrative agency working: Generated contextual narrative")
                print(f"   Length: {len(narrative)} characters")
                results["narrative_agency"] = True
            else:
                print("❌ Narrative agency failed")
                
        except Exception as e:
            print(f"❌ Narrative agency test failed: {e}")
        
        print()
        
        # Test 6: Presence Signal Integration
        print("🎯 Test 6: Presence Signal Broadcasting")
        print("-" * 50)
        
        try:
            from modules.presence.ui_integration import UIPresenceManager
            from modules.presence.voice_integration import VoicePresenceManager
            
            # Test UI presence
            ui_manager = UIPresenceManager()
            voice_manager = VoicePresenceManager()
            
            # Test presence signal generation
            presence_data = {
                "user_activity": "testing",
                "engagement_level": 0.8,
                "context": "integration_test"
            }
            
            ui_signal = ui_manager.generate_presence_signal(presence_data)
            voice_signal = voice_manager.generate_presence_signal(presence_data)
            
            if ui_signal and voice_signal:
                print("✅ Presence signals working: UI and Voice signals generated")
                results["presence_signals"] = True
            else:
                print("❌ Presence signal generation failed")
                
        except Exception as e:
            print(f"❌ Presence signal test failed: {e}")
        
        print()
        
        # Test 7: Integration Flow
        print("🔄 Test 7: Cross-System Integration Flow")
        print("-" * 50)
        
        try:
            # Test guidance coordinator with symbolic integration
            from modules.core.guidance_coordinator import GuidanceCoordinator, GuidancePackage
            
            coordinator = GuidanceCoordinator("integration_test_user")
            
            # Test symbolic guidance generation
            guidance = GuidancePackage()
            test_context = {
                "user_id": "integration_test_user",
                "emotional_state": "contemplative",
                "session_context": "integration_testing"
            }
            
            async def test_guidance_flow():
                await coordinator._generate_symbolic_guidance(
                    guidance, 
                    "The moonlight brings me harmony", 
                    test_context
                )
                
                symbolic_guidance = guidance.mode_specifics.get('symbolic_guidance')
                if symbolic_guidance:
                    print("✅ Integration flow working: Symbolic guidance generated")
                    print(f"   Symbols incorporated: {symbolic_guidance['symbol_count']}")
                    results["integration_flow"] = True
                    return True
                else:
                    print("❌ Integration flow failed: No symbolic guidance")
                    return False
            
            # Run async integration test
            flow_success = asyncio.run(test_guidance_flow())
            
        except Exception as e:
            print(f"❌ Integration flow test failed: {e}")
        
        print()
        
        # Test Results Summary
        print("📊 Integration Test Results Summary")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for system, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            system_name = system.replace("_", " ").title()
            print(f"{status:8} | {system_name}")
        
        print("-" * 60)
        print(f"Overall Result: {passed_tests}/{total_tests} systems working")
        
        if passed_tests == total_tests:
            print("🎉 ALL SYSTEMS INTEGRATED SUCCESSFULLY!")
            print("\n🚀 Ready for production deployment!")
        elif passed_tests >= total_tests * 0.8:
            print("🟡 MOSTLY WORKING - Minor issues to resolve")
        else:
            print("🔴 SIGNIFICANT INTEGRATION ISSUES - Requires attention")
        
        # Data Files Check
        print("\n📁 Data Files Verification")
        print("-" * 30)
        
        data_files = [
            "data/dreams.json",
            "data/emotional_session_state.json", 
            "data/emotional_signatures.json",
            "data/haptic_signal.json",
            "data/investment_goals.json",
            "data/investment_journal.json",
            "data/investment_strategies.json",
            "data/presence_broadcast_log.json",
            "data/ui_presence_signal.json",
            "data/voice_presence_signal.json"
        ]
        
        files_exist = 0
        for file_path in data_files:
            if os.path.exists(file_path):
                files_exist += 1
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - Missing")
        
        print(f"\nData Files: {files_exist}/{len(data_files)} present")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ Critical integration test failure: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting comprehensive integration test...")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = test_comprehensive_integration()
    
    if success:
        print("\n🎉 Integration test completed successfully!")
        print("All systems are ready for deployment.")
    else:
        print("\n⚠️ Integration test completed with issues.")
        print("Review the results above for specific failures.")
