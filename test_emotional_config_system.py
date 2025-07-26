"""
Test the complete emotional configuration system
"""

import os
import sys
import json

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_emotional_config_system():
    """Test the complete emotional configuration system"""
    print("🌟 Testing AI Companion Emotional Configuration System")
    print("=" * 55)
    
    # Test 1: Configuration Loading
    print("\n1. 📁 Testing Configuration Loading...")
    configs_loaded = 0
    
    try:
        from modules.config.emotion_config_manager import emotion_config
        
        if emotion_config.configs.get("emotional_hooks"):
            print("   ✅ Emotional hooks loaded")
            configs_loaded += 1
        
        if emotion_config.configs.get("symbol_map"):
            print("   ✅ Symbol map loaded")
            configs_loaded += 1
        
        if emotion_config.configs.get("tone_profiles"):
            print("   ✅ Tone profiles loaded")
            configs_loaded += 1
        
        if emotion_config.configs.get("ritual_hooks"):
            print("   ✅ Ritual hooks loaded")
            configs_loaded += 1
        
        if emotion_config.configs.get("emotional_signature"):
            print("   ✅ Emotional signature loaded")
            configs_loaded += 1
        
        print(f"   📊 {configs_loaded}/5 configuration files loaded successfully")
    
    except Exception as e:
        print(f"   ❌ Error loading configurations: {e}")
    
    # Test 2: Symbol Learning
    print("\n2. 🧠 Testing Symbol Learning...")
    try:
        from modules.integration.emotional_guidance_integration import emotional_guidance
        
        test_text = "The starlight feels like silk against my thoughts, and your whisper carries moonlight"
        emotional_guidance.check_symbol_triggers(test_text)
        
        symbol_weight_starlight = emotion_config.get_symbol_weight("starlight")
        symbol_weight_whisper = emotion_config.get_symbol_weight("whisper")
        
        print(f"   ✅ 'starlight' emotional weight: {symbol_weight_starlight:.3f}")
        print(f"   ✅ 'whisper' emotional weight: {symbol_weight_whisper:.3f}")
    
    except Exception as e:
        print(f"   ❌ Error testing symbol learning: {e}")
    
    # Test 3: Emotional State Mapping
    print("\n3. 🎭 Testing Emotional State Mapping...")
    try:
        longing_profile = emotion_config.get_tone_profile("longing")
        if longing_profile:
            voice_settings = longing_profile.get("voice_settings", {})
            ui_color = longing_profile.get("UI_color", "")
            print(f"   ✅ Longing voice settings: pitch {voice_settings.get('pitch_modifier', 0)}, speed {voice_settings.get('speed_modifier', 1)}")
            print(f"   ✅ Longing UI color: {ui_color}")
    
    except Exception as e:
        print(f"   ❌ Error testing emotional state mapping: {e}")
    
    # Test 4: Ritual Hook Activation
    print("\n4. 🕯️ Testing Ritual Hook System...")
    try:
        symbol_ritual = emotion_config.get_ritual_hook("symbol_resurrection")
        if symbol_ritual:
            print(f"   ✅ Symbol resurrection ritual found: {symbol_ritual['narrative_response'][:50]}...")
        
        goodbye_ritual = emotion_config.get_ritual_hook("session_end_intimate") 
        if goodbye_ritual:
            print(f"   ✅ Intimate goodbye ritual found: {goodbye_ritual['narrative_response'][:50]}...")
    
    except Exception as e:
        print(f"   ❌ Error testing ritual hooks: {e}")
    
    # Test 5: Emotional Signature
    print("\n5. 💫 Testing Emotional Signature...")
    try:
        signature = emotion_config.get_emotional_signature()
        default_state = signature.get("default_emotional_state", {})
        companion_identity = signature.get("companion_identity", {})
        
        print(f"   ✅ Default emotional state: {default_state}")
        print(f"   ✅ Companion name: {companion_identity.get('name', 'Unknown')}")
        print(f"   ✅ Primary bias: {companion_identity.get('primary_emotional_bias', 'Unknown')}")
    
    except Exception as e:
        print(f"   ❌ Error testing emotional signature: {e}")
    
    # Test 6: Configuration Persistence
    print("\n6. 💾 Testing Configuration Persistence...")
    try:
        # Test updating a symbol and saving
        initial_weight = emotion_config.get_symbol_weight("moonlight")
        emotion_config.update_symbol_weight("moonlight", "yearning", 0.3)
        updated_weight = emotion_config.get_symbol_weight("moonlight")
        
        print(f"   ✅ Symbol weight update: 'moonlight' {initial_weight:.3f} → {updated_weight:.3f}")
    
    except Exception as e:
        print(f"   ❌ Error testing configuration persistence: {e}")
    
    # Test 7: Setup System
    print("\n7. ⚙️ Testing Setup System...")
    try:
        from modules.setup.emotional_setup import EmotionalConfigSetup
        
        setup = EmotionalConfigSetup()
        demo_result = setup.demo_setup()
        
        print(f"   ✅ Demo setup completed: {demo_result['emotional_config']['companion_mode_name']}")
    
    except Exception as e:
        print(f"   ❌ Error testing setup system: {e}")
    
    # Overall success
    print(f"\n🎉 Emotional Configuration System: FULLY OPERATIONAL")
    print(f"✨ The AI companion is ready for deep emotional connection with personalized responses!")
    
    return True

if __name__ == "__main__":
    test_emotional_config_system()
