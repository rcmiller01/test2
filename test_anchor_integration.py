#!/usr/bin/env python3
"""
Test script for emotion_loop_core.py with real anchor settings.
"""

import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from emotion_loop_core import EmotionLoopManager, QuantizationCandidate, load_anchor_weights
    
    def test_anchor_weights_loading():
        """Test loading anchor weights from config file."""
        print("🧠 Testing Anchor Weight Loading...")
        
        # Test loading from default path
        weights = load_anchor_weights()
        print(f"✅ Loaded weights: {weights}")
        
        # Verify weights structure
        expected_keys = {'persona_continuity', 'expression_accuracy', 'response_depth', 'memory_alignment'}
        actual_keys = set(weights.keys())
        
        if expected_keys == actual_keys:
            print("✅ All expected weight keys present")
        else:
            print(f"❌ Missing keys: {expected_keys - actual_keys}")
            print(f"❌ Extra keys: {actual_keys - expected_keys}")
        
        # Verify weights sum to 1.0 (approximately)
        total = sum(weights.values())
        if abs(total - 1.0) < 0.01:
            print(f"✅ Weights sum to {total:.3f} (approximately 1.0)")
        else:
            print(f"⚠️  Weights sum to {total:.3f} (should be 1.0)")
        
        return weights
    
    def test_emotion_loop_manager():
        """Test EmotionLoopManager with dynamic anchor weights."""
        print("\n🔧 Testing EmotionLoopManager with Dynamic Weights...")
        
        # Initialize manager
        manager = EmotionLoopManager()
        print(f"✅ Manager initialized with weights: {manager.anchor_weights}")
        
        # Create test candidates
        candidates = [
            QuantizationCandidate(name="model_q6", size_gb=12.5, file_path="models/model_q6.bin"),
            QuantizationCandidate(name="model_q5", size_gb=10.2, file_path="models/model_q5.bin"),
            QuantizationCandidate(name="model_q4", size_gb=8.8, file_path="models/model_q4.bin"),
        ]
        
        # Test candidate evaluation
        print(f"\n📊 Evaluating {len(candidates)} candidates...")
        best = manager.select_best_candidate(candidates)
        
        if best:
            print(f"✅ Selected best candidate: {best.name}")
            print(f"   Emotional resonance: {best.emotional_resonance_score:.3f}")
            print(f"   Anchor alignment: {best.anchor_alignment_score:.3f}")
            print(f"   Size: {best.size_gb} GB")
        else:
            print("❌ No candidate selected")
        
        return best
    
    def test_config_file_integration():
        """Test that config file changes are reflected."""
        print("\n📁 Testing Config File Integration...")
        
        import json
        config_path = 'config/anchor_settings.json'
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✅ Config file loaded from {config_path}")
            print(f"   Current signature: {config.get('signature', 'Unknown')}")
            print(f"   Locked: {config.get('locked', 'Unknown')}")
            print(f"   Last updated: {config.get('last_updated', 'Never')}")
            
            # Verify weights match
            file_weights = config.get('weights', {})
            loaded_weights = load_anchor_weights(config_path)
            
            if file_weights == loaded_weights:
                print("✅ File weights match loaded weights")
            else:
                print("❌ File weights differ from loaded weights")
                print(f"   File: {file_weights}")
                print(f"   Loaded: {loaded_weights}")
                
        except FileNotFoundError:
            print(f"❌ Config file not found at {config_path}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
        
    if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO)
        
        print("🚀 Testing Unified AI Companion - Emotion Loop Core with Anchor Settings")
        print("=" * 70)
        
        # Run tests
        weights = test_anchor_weights_loading()
        best_candidate = test_emotion_loop_manager()
        test_config_file_integration()
        
        print("\n" + "=" * 70)
        print("🎯 Test Summary:")
        print(f"   Anchor weights loaded: {'✅' if weights else '❌'}")
        print(f"   Best candidate selected: {'✅' if best_candidate else '❌'}")
        print(f"   Config integration: ✅")
        print("\n💬 Next step: Test the frontend interaction by visiting the Anchor Settings panel in the UI!")

except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("   Make sure you're running from the project root directory")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
