#!/usr/bin/env python3
"""
Simple test to verify True Recall system components can be imported and created
"""

import sys
import os
from pathlib import Path

# Add the current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test that all components can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from memory.emotion_tagger import EmotionTagger
        print("✅ EmotionTagger imported successfully")
    except Exception as e:
        print(f"❌ EmotionTagger import failed: {e}")
        return False
    
    try:
        from memory.salience_scoring import SalienceScorer
        print("✅ SalienceScorer imported successfully")
    except Exception as e:
        print(f"❌ SalienceScorer import failed: {e}")
        return False
    
    try:
        from storage.memory_store import MemoryStore
        print("✅ MemoryStore imported successfully")
    except Exception as e:
        print(f"❌ MemoryStore import failed: {e}")
        return False
    
    try:
        from memory.memory_graph import MemoryGraph
        print("✅ MemoryGraph imported successfully")
    except Exception as e:
        print(f"❌ MemoryGraph import failed: {e}")
        return False
    
    try:
        from memory.reflection_agent import ReflectionAgent
        print("✅ ReflectionAgent imported successfully")
    except Exception as e:
        print(f"❌ ReflectionAgent import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of each component"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test EmotionTagger
        from memory.emotion_tagger import EmotionTagger
        tagger = EmotionTagger()
        result = tagger.analyze_text("I'm feeling really happy today!")
        print(f"✅ EmotionTagger working: {result.get('primary_emotion', 'unknown')}")
    except Exception as e:
        print(f"❌ EmotionTagger test failed: {e}")
        return False
    
    try:
        # Test SalienceScorer
        from memory.salience_scoring import SalienceScorer
        scorer = SalienceScorer()
        test_event = {
            'content': 'Test memory',
            'timestamp': '2024-01-01T10:00:00',
            'emotion_analysis': {'intensity': 0.5}
        }
        score = scorer.calculate_salience(test_event, [], {})
        print(f"✅ SalienceScorer working: {score.get('total_score', 0)}")
    except Exception as e:
        print(f"❌ SalienceScorer test failed: {e}")
        return False
    
    try:
        # Test MemoryStore
        from storage.memory_store import MemoryStore
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            store = MemoryStore(temp_dir)
            store.store_event({
                'id': 'test1',
                'content': 'Test memory',
                'timestamp': '2024-01-01T10:00:00'
            })
            events = store.get_events()
            print(f"✅ MemoryStore working: {len(events)} events stored")
    except Exception as e:
        print(f"❌ MemoryStore test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 True Recall Simple Test Suite")
    print("=" * 50)
    
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False
    
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed!")
        return False
    
    print("\n🎉 All tests passed! True Recall components are working.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
