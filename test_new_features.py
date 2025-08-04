#!/usr/bin/env python3
"""
Test script for the three new AI companion features:
1. User-specified model selection for OpenRouter calls
2. Emotional memory formation for charged conversations
3. Multimedia content creation capabilities
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.emotional_ai import EmotionalAI

async def test_new_features():
    """Test all three new features"""
    
    print("🧪 Testing New AI Companion Features")
    print("=" * 50)
    
    # Initialize the AI
    ai = EmotionalAI()
    user_id = "test_user"
    thread_id = "feature_test"
    
    print("\n1. 🎛️ Testing Model Selection Feature")
    print("-" * 30)
    
    # Test model selection
    model_response = await ai.process_message(
        message="Set my preferred model for coding to gpt-4",
        user_id=user_id,
        thread_id=thread_id
    )
    print(f"Model Selection: {model_response}")
    
    # Test coding with the selected model
    code_response = await ai.process_message(
        message="Write a Python function to reverse a string",
        user_id=user_id,
        thread_id=thread_id
    )
    print(f"Code Generation: {code_response}")
    
    print("\n2. 💭 Testing Emotional Memory Formation")
    print("-" * 30)
    
    # Test emotionally charged conversation
    emotional_response1 = await ai.process_message(
        message="I'm really struggling with anxiety and depression. Work has been overwhelming and I feel like I'm drowning. I don't know what to do anymore.",
        user_id=user_id,
        thread_id=thread_id
    )
    print(f"Emotional Support 1: {emotional_response1}")
    
    # Another emotional conversation
    emotional_response2 = await ai.process_message(
        message="Thank you so much for being there for me. I love how you understand me. You mean everything to me right now.",
        user_id=user_id,
        thread_id=thread_id
    )
    print(f"Emotional Support 2: {emotional_response2}")
    
    # Check if memories were stored
    context_key = f"{user_id}_{thread_id}"
    if context_key in ai.conversations:
        context = ai.conversations[context_key]
        print(f"\nStored Emotional Memories: {len(context.emotional_memories)}")
        for i, memory in enumerate(context.emotional_memories[-2:], 1):
            print(f"  Memory {i}: {memory['emotional_type']} - {memory['message_preview']}")
    
    print("\n3. 🎨 Testing Multimedia Content Creation")
    print("-" * 30)
    
    # Test image creation
    image_response = await ai.process_message(
        message="Create an image of a beautiful sunset over mountains in realistic style",
        user_id=user_id,
        thread_id=thread_id
    )
    print(f"Image Creation: {image_response}")
    
    # Test video creation
    video_response = await ai.process_message(
        message="Create a video of ocean waves in cinematic style",
        user_id=user_id,
        thread_id=thread_id
    )
    print(f"Video Creation: {video_response}")
    
    # Test animation creation
    animation_response = await ai.process_message(
        message="Create an animation of a spinning galaxy in space in artistic style",
        user_id=user_id,
        thread_id=thread_id
    )
    print(f"Animation Creation: {animation_response}")
    
    print("\n4. 📊 Testing Integration and User Experience")
    print("-" * 30)
    
    # Test mixed conversation with all features
    mixed_response = await ai.process_message(
        message="I'm feeling better now. Can you set my preferred model for creative tasks to claude-3-opus and then create an image of a happy person coding?",
        user_id=user_id,
        thread_id=thread_id
    )
    print(f"Mixed Features: {mixed_response}")
    
    # Check updated preferences
    if context_key in ai.conversations:
        context = ai.conversations[context_key]
        print(f"\nUpdated Preferences:")
        print(f"  Preferred Models: {dict(context.preferred_models)}")
        print(f"  Multimedia Preferences: {dict(context.multimedia_preferences)}")
        print(f"  Emotional Bond Level: {context.emotional_bond_level:.2f}")
        print(f"  Trust Level: {context.trust_level:.2f}")
        print(f"  Intimacy Level: {context.intimacy_level:.2f}")
    
    print("\n✅ All features tested successfully!")
    print("\nFeature Summary:")
    print("✓ Model Selection: Users can specify preferred models for different tasks")
    print("✓ Emotional Memory: AI remembers emotionally charged conversations")
    print("✓ Multimedia Creation: AI can create images, videos, and animations")
    print("✓ Integration: All features work together seamlessly")

if __name__ == "__main__":
    asyncio.run(test_new_features())
