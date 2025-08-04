#!/usr/bin/env python3
"""
Test script for new AI companion features
"""

import asyncio
import json
from core.emotional_ai import EmotionalAI, ConversationContext

async def test_ai_companion_features():
    """Test the new AI companion features"""
    
    # Initialize the EmotionalAI system
    ai = EmotionalAI()
    
    # Create a test context
    context = ConversationContext(
        user_id="test_user",
        thread_id="test_session",
        message_history=[],
        current_mood="excited"
    )
    
    print("🤖 Testing AI Companion Features")
    print("=" * 50)
    
    # Test scenarios for the new features
    test_scenarios = [
        {
            "name": "SMS Messaging",
            "message": "Send an SMS to my friend saying 'Hey! How are you doing today?'",
            "expected_function": "sms_messaging"
        },
        {
            "name": "Social Media Posting", 
            "message": "Post to Twitter: 'Just finished an amazing coding session! #programming #AI'",
            "expected_function": "social_media"
        },
        {
            "name": "Development Tools (OpenRouter)",
            "message": "Debug this Python code: def hello(): print('Hello World')",
            "expected_function": "dev_tools_openrouter"
        },
        {
            "name": "System Monitoring",
            "message": "Show me the current CPU and memory usage",
            "expected_function": "dev_tools"
        },
        {
            "name": "AI Analysis",
            "message": "Analyze this document content: 'This is a technical specification for our new API system'",
            "expected_function": "ai_analysis"
        },
        {
            "name": "Memory System",
            "message": "Remember that I prefer coffee over tea",
            "expected_function": "memory_system"
        },
        {
            "name": "External Services - News",
            "message": "Get me the latest news about artificial intelligence",
            "expected_function": "external_services"
        },
        {
            "name": "External Services - Weather",
            "message": "What's the weather like today?",
            "expected_function": "external_services"
        },
        {
            "name": "Multimedia Control",
            "message": "Play some relaxing music",
            "expected_function": "multimedia"
        },
        {
            "name": "Voice Synthesis",
            "message": "Generate speech for 'Welcome to our AI companion system'",
            "expected_function": "voice_synthesis"
        },
        {
            "name": "Creative Learning",
            "message": "Write a short story about a robot learning to paint",
            "expected_function": "creative_learning"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing {scenario['name']}")
        print("-" * 40)
        
        try:
            # Get AI response
            response = await ai.process_message(context.user_id, context.thread_id, scenario['message'])
            
            print(f"💬 User: {scenario['message']}")
            print(f"🤖 AI: {response}")
            
            # Parse the utility request to see which function was called
            utility_result = ai._parse_utility_request(scenario['message'])
            if utility_result:
                print(f"✅ Function Called: {utility_result['function']}")
                print(f"📊 Parameters: {json.dumps(utility_result['parameters'], indent=2)}")
                
                # Verify it matches expected function
                if utility_result['function'] == scenario['expected_function']:
                    print("✅ Correct function route detected!")
                else:
                    print(f"⚠️  Expected {scenario['expected_function']}, got {utility_result['function']}")
            else:
                print("ℹ️  No utility function detected (handled as general conversation)")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    print("🎉 AI Companion Feature Testing Complete!")
    print("\n💡 Key Features Implemented:")
    print("• SMS messaging integration")
    print("• Social media posting")
    print("• Development tools routing to OpenRouter")
    print("• System monitoring")
    print("• AI-powered analysis")
    print("• Memory storage and retrieval")
    print("• External service integration (news, weather, stocks)")
    print("• Multimedia control")
    print("• Voice synthesis")
    print("• Creative content generation")

def test_function_routing():
    """Test the function routing logic"""
    
    ai = EmotionalAI()
    
    print("\n🔄 Testing Function Routing Logic")
    print("=" * 50)
    
    routing_tests = [
        ("debug my code", "dev_tools_openrouter"),
        ("check system performance", "dev_tools"),
        ("send SMS to John", "sms_messaging"),
        ("post to Facebook", "social_media"),
        ("analyze this image", "ai_analysis"),
        ("remember my birthday", "memory_system"),
        ("get weather forecast", "external_services"),
        ("play music", "multimedia"),
        ("speak this text", "voice_synthesis"),
        ("write a poem", "creative_learning"),
    ]
    
    for message, expected in routing_tests:
        result = ai._parse_utility_request(message)
        if result:
            actual = result['function']
            status = "✅" if actual == expected else "❌"
            print(f"{status} '{message}' → {actual} (expected: {expected})")
        else:
            print(f"❌ '{message}' → No function detected (expected: {expected})")

if __name__ == "__main__":
    # Test the function routing logic first
    test_function_routing()
    
    # Then test the full AI companion features
    asyncio.run(test_ai_companion_features())
