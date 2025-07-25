"""
Comprehensive test for unified AI system integration
Tests all components work together with unified personality approach
"""

import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

# Add project paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestUnifiedAIIntegration(unittest.TestCase):
    """Test suite for unified AI system integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
        
    def test_unified_ai_config_files_exist(self):
        """Test that all required unified AI config files exist"""
        required_files = [
            "unified_ai.json",
            "unified_ai_emotional_anchors.json", 
            "llm_config.json"
        ]
        
        for file_name in required_files:
            file_path = os.path.join(self.config_dir, file_name)
            self.assertTrue(os.path.exists(file_path), f"Config file {file_name} should exist")
            
            # Test JSON is valid
            with open(file_path, 'r') as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in {file_name}: {e}")
    
    def test_no_persona_specific_configs(self):
        """Test that old persona-specific configurations are removed"""
        old_persona_files = [
            "mia_romantic.json"
        ]
        
        for file_name in old_persona_files:
            file_path = os.path.join(self.config_dir, file_name)
            self.assertFalse(os.path.exists(file_path), f"Old persona file {file_name} should be removed")
    
    def test_unified_config_structure(self):
        """Test unified AI configuration has correct structure"""
        config_path = os.path.join(self.config_dir, "unified_ai.json")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check required fields
        self.assertIn("name", config)
        self.assertIn("personality", config)
        
        # Check personality structure 
        personality = config["personality"]
        self.assertIn("adaptive_modes", personality)
        self.assertIn("base_traits", personality)
        
        # Check adaptive modes
        adaptive_modes = personality["adaptive_modes"]
        expected_modes = ["companion", "technical", "creative", "casual"]
        for mode in expected_modes:
            self.assertIn(mode, adaptive_modes, f"Adaptive mode {mode} should exist")
    
    @patch('backend.goodbye_manager.GoodbyeManager')
    def test_goodbye_manager_import(self, mock_goodbye):
        """Test goodbye manager can be imported and initialized"""
        try:
            from backend.goodbye_manager import GoodbyeManager
            # Should not raise any exceptions
            self.assertTrue(True, "GoodbyeManager imported successfully")
        except ImportError as e:
            self.fail(f"Could not import GoodbyeManager: {e}")
    
    @patch('backend.mood_style_profiles.MoodStyleProfile')
    def test_mood_style_profiles_import(self, mock_mood):
        """Test mood style profiles can be imported"""
        try:
            from backend.mood_style_profiles import MoodStyleProfile
            self.assertTrue(True, "MoodStyleProfile imported successfully")
        except ImportError as e:
            self.fail(f"Could not import MoodStyleProfile: {e}")
    
    @patch('backend.ritual_hooks.RitualEngine')
    def test_ritual_hooks_import(self, mock_ritual):
        """Test ritual hooks can be imported"""
        try:
            from backend.ritual_hooks import RitualEngine
            self.assertTrue(True, "RitualEngine imported successfully")
        except ImportError as e:
            self.fail(f"Could not import RitualEngine: {e}")
    
    def test_updated_config_files_use_unified_ai(self):
        """Test that updated config files use unified_ai instead of personas"""
        config_files = [
            "mood_thresholds.json",
            "normal_thoughts.json",
            "persona_prefs.json"
        ]
        
        for file_name in config_files:
            file_path = os.path.join(self.config_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Should not contain old persona names
                old_personas = ["mia", "solene", "lyra", "Mia", "Solene", "Lyra"]
                for persona in old_personas:
                    self.assertNotIn(f'"{persona}":', content, 
                                   f"File {file_name} should not contain {persona} references")
                
                # Should contain unified_ai
                if file_name != "persona_prefs.json":  # persona_prefs might have different structure
                    self.assertIn("unified_ai", content, 
                                f"File {file_name} should contain unified_ai references")

    def test_llm_config_exists(self):
        """Test LLM config file exists and is valid JSON"""
        config_path = os.path.join(self.config_dir, "llm_config.json")
        
        self.assertTrue(os.path.exists(config_path))
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            # Just verify it's valid JSON - detailed structure can be checked separately
            self.assertIsInstance(config, dict)


if __name__ == "__main__":
    print("Running Unified AI Integration Tests...")
    unittest.main(verbosity=2)
