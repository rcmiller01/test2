#!/usr/bin/env python3
"""
True Recall Memory System - Working Demonstration

This script demonstrates the core functionality of the True Recall memory system
for AI companions, showing how it can analyze emotions, score memory importance,
and create rich memory profiles.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def demonstrate_emotion_analysis():
    """Demonstrate emotion analysis capabilities"""
    print("🎭 EMOTION ANALYSIS DEMONSTRATION")
    print("-" * 50)
    
    from memory.emotion_tagger import EmotionTagger
    
    tagger = EmotionTagger()
    
    # Test various emotional texts
    test_texts = [
        "I'm so excited about my promotion at work!",
        "I feel really sad about losing my childhood pet.",
        "This project is making me incredibly frustrated and angry.",
        "I'm worried about the upcoming exam next week.",
        "The sunset was absolutely beautiful and peaceful.",
        "I'm grateful for all the support from my friends.",
    ]
    
    for text in test_texts:
        print(f"\n📝 Text: \"{text}\"")
        analysis = tagger.analyze_text(text)
        
        print(f"   🎯 Primary Emotion: {analysis.get('primary_emotion', 'unknown')}")
        print(f"   🔢 Intensity: {analysis.get('intensity', 0):.2f}")
        print(f"   ⚡ Arousal: {analysis.get('arousal', 0):.2f}")
        print(f"   😊 Valence: {analysis.get('valence', 0):.2f}")
        print(f"   🎨 Fingerprint: {analysis.get('emotional_fingerprint', 'none')}")
    
    return True

def demonstrate_salience_scoring():
    """Demonstrate memory importance scoring"""
    print("\n\n🎯 SALIENCE SCORING DEMONSTRATION")
    print("-" * 50)
    
    from memory.salience_scoring import SalienceScorer
    from memory.emotion_tagger import EmotionTagger
    
    scorer = SalienceScorer()
    tagger = EmotionTagger()
    
    # Create test memories with different characteristics
    test_memories = [
        {
            'content': "Just got my dream job! I'm the new Senior Developer at TechCorp!",
            'timestamp': datetime.now().isoformat(),
            'context': {'conversation_type': 'achievement', 'user_initiated': True}
        },
        {
            'content': "Had coffee this morning. It was okay, nothing special.",
            'timestamp': datetime.now().isoformat(),
            'context': {'conversation_type': 'casual', 'user_initiated': False}
        },
        {
            'content': "My grandmother passed away yesterday. I'm heartbroken.",
            'timestamp': datetime.now().isoformat(),
            'context': {'conversation_type': 'personal', 'user_initiated': True}
        },
        {
            'content': "Thinking about learning Python programming.",
            'timestamp': datetime.now().isoformat(),
            'context': {'conversation_type': 'learning', 'user_initiated': True}
        }
    ]
    
    for i, memory in enumerate(test_memories, 1):
        print(f"\n📖 Memory {i}: \"{memory['content']}\"")
        
        # Analyze emotions first
        emotion_analysis = tagger.analyze_text(memory['content'])
        memory['emotion_analysis'] = emotion_analysis
        
        # Calculate salience
        salience = scorer.calculate_salience(memory)
        
        print(f"   🎭 Emotion: {emotion_analysis.get('primary_emotion', 'unknown')} "
              f"(intensity: {emotion_analysis.get('intensity', 0):.2f})")
        print(f"   ⭐ Total Salience: {salience.get('total_score', 0):.3f}")
        print(f"   📊 Components:")
        print(f"      - Recency: {salience.get('components', {}).get('recency', 0):.3f}")
        print(f"      - Emotional: {salience.get('components', {}).get('emotional', 0):.3f}")
        print(f"      - Engagement: {salience.get('components', {}).get('engagement', 0):.3f}")
        print(f"      - Contextual: {salience.get('components', {}).get('contextual', 0):.3f}")
        print(f"   🏷️  Level: {salience.get('salience_level', 'unknown')}")
    
    return True

def demonstrate_memory_integration():
    """Demonstrate how components work together"""
    print("\n\n🔗 MEMORY INTEGRATION DEMONSTRATION")
    print("-" * 50)
    
    from memory.emotion_tagger import EmotionTagger
    from memory.salience_scoring import SalienceScorer
    
    # Simulate a conversation flow
    conversation = [
        "Hi! How are you doing today?",
        "I've been feeling a bit anxious about my job interview tomorrow.",
        "Can you help me prepare some questions?",
        "What should I wear? I want to make a good impression.",
        "Thank you so much! I feel much more confident now."
    ]
    
    tagger = EmotionTagger()
    scorer = SalienceScorer()
    
    print("🗣️  Simulated Conversation Flow:")
    
    memories = []
    for i, message in enumerate(conversation, 1):
        print(f"\n💬 Turn {i}: \"{message}\"")
        
        # Create memory event
        memory_event = {
            'id': f'conv_{i}',
            'content': message,
            'timestamp': datetime.now().isoformat(),
            'context': {
                'conversation_turn': i,
                'conversation_length': len(conversation),
                'user_initiated': i in [1, 2, 4]  # Simulate which turns user initiated
            }
        }
        
        # Analyze emotions
        emotion_analysis = tagger.analyze_text(message)
        memory_event['emotion_analysis'] = emotion_analysis
        
        # Calculate salience
        salience = scorer.calculate_salience(memory_event, memories)
        memory_event['salience'] = salience
        
        # Store memory
        memories.append(memory_event)
        
        # Display analysis
        primary_emotion = emotion_analysis.get('primary_emotion', 'neutral')
        intensity = emotion_analysis.get('intensity', 0)
        salience_score = salience.get('total_score', 0)
        salience_level = salience.get('salience_level', 'low')
        
        print(f"   🎭 Emotion: {primary_emotion} (intensity: {intensity:.2f})")
        print(f"   ⭐ Salience: {salience_score:.3f} ({salience_level})")
    
    print(f"\n📊 Conversation Summary:")
    print(f"   💾 Total memories: {len(memories)}")
    high_salience = [m for m in memories if m['salience']['total_score'] > 0.6]
    print(f"   🔥 High-importance memories: {len(high_salience)}")
    
    if high_salience:
        print(f"   📌 Most important: \"{high_salience[0]['content'][:50]}...\"")
    
    return True

def main():
    """Run the complete demonstration"""
    print("🧠 TRUE RECALL MEMORY SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("Advanced AI companion memory with emotion analysis,")
    print("importance scoring, and contextual understanding.")
    print("=" * 60)
    
    try:
        # Run demonstrations
        demonstrate_emotion_analysis()
        demonstrate_salience_scoring()
        demonstrate_memory_integration()
        
        print("\n\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("✅ All True Recall components are working correctly!")
        print("🚀 Ready for integration with your AI companion system.")
        print("\n📖 Next steps:")
        print("   1. Install dependencies: pip install textblob scikit-learn tinydb")
        print("   2. Import RecallEngine in your main application")
        print("   3. Create memory-enhanced conversations")
        print("   4. Enjoy intelligent, emotionally-aware AI interactions!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
