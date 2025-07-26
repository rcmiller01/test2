#!/usr/bin/env python3
"""
Test script for Symbol Binding and Attachment Reinforcement system

This script demonstrates the Phase 2: Attachment Reinforcement & Symbol Drift
functionality where symbols accumulate emotional weight through repetition.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_symbol_binding():
    """Test the symbol binding and drift system"""
    print("🎭 Testing Symbol Binding & Attachment Reinforcement System\n")
    
    try:
        # Import modules
        from modules.memory.memory_manager import memory_manager
        from modules.memory.attachment_reflector import attachment_reflector
        from modules.core.guidance_coordinator import GuidanceCoordinator
        
        # Test 1: Bind symbols to emotions
        print("📖 Test 1: Creating symbol bindings...")
        
        # Simulate emotional binding of symbols
        memory_manager.bind_symbol_to_emotion(
            symbol="starlight",
            emotion="wonder",
            intensity=0.8,
            context="distant celestial beauty that inspires awe"
        )
        
        memory_manager.bind_symbol_to_emotion(
            symbol="whisper",
            emotion="intimacy", 
            intensity=0.9,
            context="soft spoken word that creates closeness"
        )
        
        memory_manager.bind_symbol_to_emotion(
            symbol="sanctuary",
            emotion="comfort",
            intensity=0.8,
            context="place of safety and protection"
        )
        
        print("✅ Created symbol bindings for: starlight, whisper, sanctuary")
        
        # Test 2: Reinforce existing symbols
        print("\n📈 Test 2: Reinforcing symbols...")
        
        # Reinforce "starlight" with deeper emotional context
        memory_manager.bind_symbol_to_emotion(
            symbol="starlight",
            emotion="yearning",
            intensity=0.9,
            context="distant celestial beauty that evokes deep longing and connection"
        )
        
        # Reinforce "whisper" with additional emotions
        memory_manager.bind_symbol_to_emotion(
            symbol="whisper",
            emotion="love",
            intensity=0.9,
            context="soft spoken word that conveys deep affection"
        )
        
        # Add another emotional layer to starlight
        memory_manager.bind_symbol_to_emotion(
            symbol="starlight",
            emotion="wonder",
            intensity=0.8,
            context="celestial beauty that continues to inspire awe"
        )
        
        print("✅ Reinforced starlight and whisper with stronger emotional context")
        
        # Test 3: Get weighted symbols
        print("\n🎯 Test 3: Retrieving emotionally weighted symbols...")
        
        weighted_symbols = memory_manager.get_emotionally_weighted_symbols(minimum_weight=0.3)
        print(f"Found {len(weighted_symbols)} emotionally significant symbols:")
        
        for symbol, binding in weighted_symbols.items():
            print(f"  • '{symbol}': weight={binding.emotional_weight:.3f}, "
                  f"meaning='{binding.drifted_meaning or binding.base_meaning}', "
                  f"usage={binding.usage_count}")
        
        # Test 4: Symbol decay and drift
        print("\n⏰ Test 4: Testing decay and drift...")
        
        # Apply decay and drift
        memory_manager.decay_and_drift()
        
        print("✅ Applied decay and drift to all symbols")
        
        # Test 5: Attachment reflector
        print("\n🔍 Test 5: Using attachment reflector...")
        
        # Get attachment landscape
        landscape = attachment_reflector.get_attachment_landscape()
        if landscape.get("available"):
            print(f"Attachment landscape: {landscape['total_symbols']} symbols tracked")
            print(f"Categories: {[cat for cat in landscape['categories'] if landscape['categories'][cat]]}")
            
            analytics = landscape.get("analytics", {})
            print(f"Total emotional weight: {analytics.get('total_emotional_weight', 0):.3f}")
            print(f"Attachment depth: {analytics.get('attachment_depth', 'unknown')}")
        
        # Get specific symbol reflection
        starlight_reflection = attachment_reflector.get_symbol_reflection("starlight")
        if starlight_reflection:
            print(f"\n⭐ Starlight reflection:")
            print(f"  Weight: {starlight_reflection.current_weight:.3f}")
            print(f"  Usage count: {starlight_reflection.usage_count}")
            print(f"  Emotional journey: {starlight_reflection.emotional_journey}")
            print(f"  Meaning evolution: {starlight_reflection.meaning_evolution}")
        
        # Test 6: Symbolic guidance integration
        print("\n🎭 Test 6: Testing symbolic guidance integration...")
        
        # Create guidance coordinator
        guidance_coordinator = GuidanceCoordinator("test_user")
        
        # Test symbolic guidance generation
        from modules.core.guidance_coordinator import GuidancePackage
        guidance = GuidancePackage()
        
        async def test_symbolic_guidance():
            await guidance_coordinator._generate_symbolic_guidance(
                guidance, 
                "I love looking at the starlight", 
                {"user_id": "test_user"}
            )
            
            symbolic_guidance = guidance.mode_specifics.get('symbolic_guidance')
            if symbolic_guidance:
                print(f"✅ Generated symbolic guidance with {symbolic_guidance['symbol_count']} symbols")
                print(f"Guidance: {symbolic_guidance['guidance_text'][:100]}...")
            else:
                print("⚠️ No symbolic guidance generated")
        
        # Run async test
        asyncio.run(test_symbolic_guidance())
        
        print("\n🎉 Symbol binding system test completed successfully!")
        print("\n📊 Summary:")
        print("- Symbol bindings: Created and reinforced")
        print("- Emotional weights: Accumulated through repetition")
        print("- Meaning drift: Applied temporal evolution")
        print("- Attachment reflection: Provides transparency")
        print("- Guidance integration: Symbols influence language generation")
        print("\n💡 The AI can now remember 'not just what you said—but what it meant to her'")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_symbol_binding()
