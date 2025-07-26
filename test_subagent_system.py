#!/usr/bin/env python3
"""
Simple test script for SubAgent Router System
Tests basic functionality without complex imports
"""

import asyncio
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

async def test_basic_functionality():
    """Test basic SubAgent Router functionality"""
    
    print("🚀 Testing SubAgent Router System")
    print("=" * 50)
    
    try:
        # Test 1: Import SubAgentRouter
        print("📦 Testing imports...")
        from backend.subagent_router import SubAgentRouter, IntentClassifier, IntentType
        print("✅ SubAgentRouter imported successfully")
        
        # Test 2: Initialize router
        print("\n🔧 Testing initialization...")
        router = SubAgentRouter()
        print("✅ SubAgentRouter initialized")
        print(f"   Available agents: {list(router.agents.keys())}")
        
        # Test 3: Test intent classification
        print("\n🧠 Testing intent classification...")
        classifier = IntentClassifier()
        
        test_inputs = [
            "Help me debug this Python code",
            "Write me a beautiful story",
            "Do you remember our last conversation?",
            "I'm feeling overwhelmed today",
            "Create a ritual for new beginnings"
        ]
        
        for test_input in test_inputs:
            intent, confidence = classifier.classify_intent(test_input)
            print(f"   '{test_input[:30]}...' -> {intent.value} (confidence: {confidence:.2f})")
        
        # Test 4: Test routing
        print("\n🎯 Testing routing...")
        
        # Test code routing
        code_response = await router.route(
            "Help me implement a binary search algorithm",
            {"project_type": "python", "mood": "focused"}
        )
        print(f"✅ Code routing: {code_response.agent_type} -> {code_response.intent_detected.value}")
        print(f"   Response preview: {code_response.content[:100]}...")
        
        # Test creative routing
        creative_response = await router.route(
            "Create a metaphor for personal growth",
            {"mood": "contemplative", "conversation_depth": 0.7}
        )
        print(f"✅ Creative routing: {creative_response.agent_type} -> {creative_response.intent_detected.value}")
        print(f"   Response preview: {creative_response.content[:100]}...")
        
        # Test memory routing
        memory_response = await router.route(
            "What did we discuss in our previous conversations?",
            {"conversation_history": ["Previous talk about goals"], "total_interactions": 5}
        )
        print(f"✅ Memory routing: {memory_response.agent_type} -> {memory_response.intent_detected.value}")
        print(f"   Response preview: {memory_response.content[:100]}...")
        
        # Test 5: Analytics
        print("\n📊 Testing analytics...")
        analytics = router.get_routing_analytics()
        print(f"✅ Analytics generated")
        print(f"   Total routes: {analytics['total_routes']}")
        print(f"   Intent distribution: {analytics['intent_distribution']}")
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! SubAgent Router System is working.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_personality_formatter():
    """Test the personality formatting system"""
    
    print("\n🎭 Testing Personality Formatter...")
    
    try:
        from backend.ai_reformulator import PersonalityFormatter, ReformulationRequest
        
        formatter = PersonalityFormatter()
        print("✅ PersonalityFormatter initialized")
        
        # Test basic formatting
        request = ReformulationRequest(
            original_response="Here's a Python function to solve your problem.",
            agent_type="code",
            intent_detected="implementation_request",
            user_context={"mood": "anxious", "conversation_depth": 0.4},
            personality_context={}
        )
        
        result = await formatter.format(request)
        print(f"✅ Formatting successful")
        print(f"   Original: {request.original_response}")
        print(f"   Formatted: {result.content[:100]}...")
        print(f"   Tone: {result.emotional_tone}")
        print(f"   Confidence: {result.reformulation_confidence:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing formatter: {e}")
        return False

def main():
    """Main test runner"""
    
    print("🧪 SubAgent Router System Test Suite")
    print("=" * 60)
    
    async def run_all_tests():
        basic_test = await test_basic_functionality()
        formatter_test = await test_personality_formatter()
        
        if basic_test and formatter_test:
            print("\n🏆 ALL TESTS PASSED! System is ready for use.")
            return True
        else:
            print("\n💥 Some tests failed. Check the output above.")
            return False
    
    success = asyncio.run(run_all_tests())
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
