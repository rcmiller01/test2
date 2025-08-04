#!/usr/bin/env python3
"""
Test Configuration Update System

This script tests the API key management system to ensure it properly handles
configuration updates through the chat interface.
"""

import asyncio
import sys
import os

# Add the core directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from emotional_ai import EmotionalAI

async def test_config_updates():
    """Test the configuration update functionality"""
    print("🧪 Testing Configuration Update System...")
    
    # Initialize the AI system
    ai = EmotionalAI()
    
    # Test 1: Show current configuration
    print("\n📋 Test 1: Showing current configuration")
    result = await ai._handle_config_update({"message": "show config"})
    print(f"Result: {result}")
    
    # Test 2: Update N8N API key
    print("\n🔑 Test 2: Updating N8N API key")
    result = await ai._handle_config_update({
        "message": "update n8n key: x" # api key placeholder
    })
    print(f"Result: {result}")
       # Test 3: Update OpenRouter API key
    print("\n🚀 Test 3: Updating OpenRouter API key")
    result = await ai._handle_config_update({
        "message": "set openrouter: x" #api key placeholder
    })
    print(f"Result: {result}")

    # Test 4: Update temperature
    print("\n🌡️ Test 4: Updating temperature")
    result = await ai._handle_config_update({
        "message": "set temperature to 0.8"
    })
    print(f"Result: {result}")
    
    # Test 5: Show updated configuration
    print("\n📋 Test 5: Showing updated configuration")
    result = await ai._handle_config_update({"message": "show current config"})
    print(f"Result: {result}")
    
    # Test 6: Test through process_message to verify end-to-end functionality
    print("\n🔧 Test 6: Testing config update through process_message")
    result = await ai.process_message("test_user", "test_thread", "config_update: show my current settings")
    print(f"Full message processing: {result}")
    
    print("\n✅ Configuration update tests completed!")

if __name__ == "__main__":
    asyncio.run(test_config_updates())
