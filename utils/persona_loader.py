#!/usr/bin/env python3
"""
Persona Loader Utility

Handles loading, validation, and management of persona manifest files.
Integrates with the Dolphin AI Orchestrator's personality system.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class PersonaManifest:
    """
    Represents a loaded persona manifest with validation and access methods.
    """
    
    def __init__(self, manifest_data: Dict[str, Any], file_path: str):
        self.data = manifest_data
        self.file_path = file_path
        self._validate()
    
    def _validate(self):
        """Validate the manifest structure."""
        required_fields = ['persona', 'model', 'description', 'goals', 'language_style']
        for field in required_fields:
            if field not in self.data:
                raise ValueError(f"Missing required field: {field}")
    
    @property
    def persona_name(self) -> str:
        return self.data['persona']
    
    @property
    def primary_model(self) -> str:
        return self.data['model']
    
    @property
    def fallback_model(self) -> Optional[str]:
        routing_bias = self.data.get('routing_bias', {})
        return routing_bias.get('fallback')
    
    @property
    def cloud_delegate(self) -> Optional[str]:
        routing_bias = self.data.get('routing_bias', {})
        return routing_bias.get('cloud_delegate')
    
    @property
    def memory_config(self) -> Dict[str, Any]:
        return self.data.get('memory_directives', {})
    
    @property
    def mirror_mode_config(self) -> Dict[str, Any]:
        return self.data.get('mirror_mode', {})
    
    @property
    def reflection_config(self) -> Dict[str, Any]:
        return self.data.get('reflection_engine', {})
    
    def get_system_prompt(self) -> str:
        """Generate a system prompt based on the persona manifest."""
        description = self.data['description']
        goals = self.data['goals']
        language_style = self.data['language_style']
        
        prompt = f"""You are {self.persona_name}. {description}

Your primary goals are:
{chr(10).join(f"- {goal}" for goal in goals)}

Language Style:
- Tone: {language_style.get('tone', 'conversational')}
- Formality: {language_style.get('formality', 'casual')}
- Emotional Range: {language_style.get('emotional_range', 'moderate')}
- Pronouns: {language_style.get('pronouns', 'they/them')}

Remember to embody these characteristics in every interaction while staying true to your core identity."""

        return prompt


def load_persona(manifest_path: str) -> PersonaManifest:
    """
    Load a persona manifest from a JSON file.
    
    Args:
        manifest_path: Path to the persona manifest JSON file
        
    Returns:
        PersonaManifest: Loaded and validated persona manifest
        
    Raises:
        FileNotFoundError: If the manifest file doesn't exist
        ValueError: If the manifest is invalid
        json.JSONDecodeError: If the JSON is malformed
    """
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Persona manifest not found: {manifest_path}")
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        logger.info(f"✅ Loaded persona manifest: {manifest_path}")
        return PersonaManifest(manifest_data, manifest_path)
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in persona manifest {manifest_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error loading persona manifest {manifest_path}: {e}")
        raise


def load_all_personas(personas_dir: str = "personas") -> Dict[str, PersonaManifest]:
    """
    Load all persona manifests from a directory.
    
    Args:
        personas_dir: Directory containing persona manifest files
        
    Returns:
        Dict[str, PersonaManifest]: Dictionary mapping persona names to manifests
    """
    personas = {}
    
    if not os.path.exists(personas_dir):
        logger.warning(f"Personas directory not found: {personas_dir}")
        return personas
    
    for file_path in Path(personas_dir).glob("*.json"):
        try:
            manifest = load_persona(str(file_path))
            personas[manifest.persona_name.lower()] = manifest
            logger.info(f"📋 Registered persona: {manifest.persona_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load persona from {file_path}: {e}")
    
    return personas


def get_persona_routing_bias(manifest: PersonaManifest) -> Dict[str, Optional[str]]:
    """
    Extract routing bias configuration from a persona manifest.
    
    Args:
        manifest: PersonaManifest object
        
    Returns:
        Dict containing routing preferences
    """
    return {
        'primary_model': manifest.primary_model,
        'fallback_model': manifest.fallback_model,
        'cloud_delegate': manifest.cloud_delegate
    }


def validate_persona_models(manifest: PersonaManifest, available_models: List[str]) -> bool:
    """
    Validate that the persona's required models are available.
    
    Args:
        manifest: PersonaManifest object
        available_models: List of available model names
        
    Returns:
        bool: True if all required models are available
    """
    required_models = [manifest.primary_model]
    if manifest.fallback_model:
        required_models.append(manifest.fallback_model)
    
    missing_models = [model for model in required_models if model not in available_models]
    
    if missing_models:
        logger.warning(f"⚠️ Missing models for persona {manifest.persona_name}: {missing_models}")
        return False
    
    return True


# Example usage and testing
if __name__ == "__main__":
    # Test loading the companion persona
    try:
        companion = load_persona("personas/companion_manifest.json")
        print(f"✅ Loaded persona: {companion.persona_name}")
        print(f"🤖 Primary model: {companion.primary_model}")
        print(f"🔄 Fallback model: {companion.fallback_model}")
        print("\n📝 System Prompt:")
        print(companion.get_system_prompt())
        
    except Exception as e:
        print(f"❌ Error: {e}")
