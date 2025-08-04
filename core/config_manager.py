#!/usr/bin/env python3
"""
Unified Configuration Manager - Centralized config handling for all modules

This module provides centralized configuration management to eliminate
duplicate config-loading logic across submodules and ensure consistency.

Key Features:
- Centralized config loading and validation
- Environment variable integration
- Hot-reload capabilities
- Schema validation
- Default value management
- Module-specific config sections

Author: Emotional AI System
Date: August 3, 2025
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any, Union, Type, Callable
from dataclasses import dataclass, field
from pathlib import Path
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ConfigSchema:
    """Configuration schema definition"""
    required_fields: List[str] = field(default_factory=list)
    optional_fields: Dict[str, Any] = field(default_factory=dict)  # field_name -> default_value
    field_types: Dict[str, Type] = field(default_factory=dict)  # field_name -> expected_type
    validation_rules: Dict[str, Callable] = field(default_factory=dict)  # field_name -> validation_function

class ConfigManager:
    """Centralized configuration manager for all system modules"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure single config manager instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.config_dir = Path("config")
        self.main_config_file = self.config_dir / "main_config.json"
        self.module_configs = {}  # module_name -> config_dict
        self.schemas = {}  # module_name -> ConfigSchema
        self.watchers = {}  # file_path -> last_modified_time
        self._config_lock = threading.RLock()
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load main configuration
        self._load_main_config()
        
        # Register core module schemas
        self._register_core_schemas()
        
        logger.info("Unified Configuration Manager initialized")
    
    def _load_main_config(self):
        """Load the main system configuration"""
        try:
            if self.main_config_file.exists():
                with open(self.main_config_file, 'r') as f:
                    self.main_config = json.load(f)
            else:
                # Create default main config
                self.main_config = self._get_default_main_config()
                self._save_main_config()
            
            logger.info("Main configuration loaded")
            
        except Exception as e:
            logger.error(f"Error loading main config: {e}")
            self.main_config = self._get_default_main_config()
    
    def _get_default_main_config(self) -> Dict[str, Any]:
        """Get default main configuration"""
        return {
            "system": {
                "log_level": "INFO",
                "data_dir": "data",
                "temp_dir": "temp",
                "backup_enabled": True,
                "backup_interval_hours": 24
            },
            "ai_core": {
                "model_name": "emollama",
                "base_temperature": 0.7,
                "max_tokens": 2048,
                "emotional_adaptation": True,
                "utility_functions_enabled": True
            },
            "external_services": {
                "n8n_url": "http://localhost:5678",
                "n8n_api_key": "",
                "openrouter_api_key": "",
                "enable_external_calls": True
            },
            "emotional_system": {
                "enable_emotional_memory": True,
                "memory_retention_hours": 168,
                "emotional_adaptation_rate": 0.1,
                "affect_reactor_sensitivity": 0.5
            },
            "security": {
                "nsfw_enabled": True,
                "input_sanitization": True,
                "rate_limiting": False,
                "max_requests_per_minute": 60
            }
        }
    
    def _save_main_config(self):
        """Save the main configuration to disk"""
        try:
            with open(self.main_config_file, 'w') as f:
                json.dump(self.main_config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving main config: {e}")
    
    def _register_core_schemas(self):
        """Register configuration schemas for core modules"""
        
        # AI Core schema
        self.register_schema("ai_core", ConfigSchema(
            required_fields=["model_name"],
            optional_fields={
                "base_temperature": 0.7,
                "max_tokens": 2048,
                "emotional_adaptation": True,
                "utility_functions_enabled": True
            },
            field_types={
                "model_name": str,
                "base_temperature": float,
                "max_tokens": int,
                "emotional_adaptation": bool,
                "utility_functions_enabled": bool
            },
            validation_rules={
                "base_temperature": lambda x: 0.0 <= x <= 2.0,
                "max_tokens": lambda x: 1 <= x <= 32768
            }
        ))
        
        # Emotional System schema
        self.register_schema("emotional_system", ConfigSchema(
            required_fields=[],
            optional_fields={
                "enable_emotional_memory": True,
                "memory_retention_hours": 168,
                "emotional_adaptation_rate": 0.1,
                "affect_reactor_sensitivity": 0.5
            },
            field_types={
                "enable_emotional_memory": bool,
                "memory_retention_hours": int,
                "emotional_adaptation_rate": float,
                "affect_reactor_sensitivity": float
            },
            validation_rules={
                "memory_retention_hours": lambda x: x > 0,
                "emotional_adaptation_rate": lambda x: 0.0 <= x <= 1.0,
                "affect_reactor_sensitivity": lambda x: 0.0 <= x <= 1.0
            }
        ))
        
        # External Services schema
        self.register_schema("external_services", ConfigSchema(
            required_fields=[],
            optional_fields={
                "n8n_url": "http://localhost:5678",
                "n8n_api_key": "",
                "openrouter_api_key": "",
                "enable_external_calls": True
            },
            field_types={
                "n8n_url": str,
                "n8n_api_key": str,
                "openrouter_api_key": str,
                "enable_external_calls": bool
            }
        ))
    
    def register_schema(self, module_name: str, schema: ConfigSchema):
        """Register a configuration schema for a module"""
        with self._config_lock:
            self.schemas[module_name] = schema
            logger.debug(f"Registered schema for module: {module_name}")
    
    def get_config(self, module_name: str, reload: bool = False) -> Dict[str, Any]:
        """Get configuration for a specific module"""
        with self._config_lock:
            # Check if we need to reload
            if reload or module_name not in self.module_configs:
                self._load_module_config(module_name)
            
            return self.module_configs.get(module_name, {})
    
    def _load_module_config(self, module_name: str):
        """Load configuration for a specific module"""
        try:
            # Try to load from dedicated module config file
            module_config_file = self.config_dir / f"{module_name}.json"
            
            if module_config_file.exists():
                with open(module_config_file, 'r') as f:
                    module_config = json.load(f)
            else:
                # Fall back to main config section
                module_config = self.main_config.get(module_name, {})
            
            # Apply schema defaults and validation
            if module_name in self.schemas:
                module_config = self._apply_schema(module_name, module_config)
            
            # Merge with environment variables
            module_config = self._merge_env_vars(module_name, module_config)
            
            self.module_configs[module_name] = module_config
            
            logger.debug(f"Loaded config for module: {module_name}")
            
        except Exception as e:
            logger.error(f"Error loading config for module {module_name}: {e}")
            # Use schema defaults if available
            if module_name in self.schemas:
                self.module_configs[module_name] = self.schemas[module_name].optional_fields.copy()
            else:
                self.module_configs[module_name] = {}
    
    def _apply_schema(self, module_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply schema validation and defaults to module config"""
        schema = self.schemas[module_name]
        validated_config = config.copy()
        
        # Check required fields
        for field in schema.required_fields:
            if field not in validated_config:
                raise ValueError(f"Required field '{field}' missing from {module_name} config")
        
        # Apply optional field defaults
        for field, default_value in schema.optional_fields.items():
            if field not in validated_config:
                validated_config[field] = default_value
        
        # Type validation
        for field, expected_type in schema.field_types.items():
            if field in validated_config:
                value = validated_config[field]
                if not isinstance(value, expected_type):
                    try:
                        # Try to convert
                        validated_config[field] = expected_type(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Type mismatch for {module_name}.{field}: expected {expected_type.__name__}, got {type(value).__name__}")
        
        # Custom validation rules
        for field, validation_func in schema.validation_rules.items():
            if field in validated_config:
                if not validation_func(validated_config[field]):
                    logger.warning(f"Validation failed for {module_name}.{field}: {validated_config[field]}")
        
        return validated_config
    
    def _merge_env_vars(self, module_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge environment variables into config"""
        env_prefix = f"AI_{module_name.upper()}_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                
                # Try to parse as JSON first, then as string
                try:
                    config[config_key] = json.loads(value)
                except json.JSONDecodeError:
                    config[config_key] = value
        
        return config
    
    def update_config(self, module_name: str, updates: Dict[str, Any], persist: bool = True) -> bool:
        """Update configuration for a module"""
        with self._config_lock:
            try:
                # Get current config
                current_config = self.get_config(module_name)
                
                # Apply updates
                updated_config = current_config.copy()
                updated_config.update(updates)
                
                # Validate against schema if available
                if module_name in self.schemas:
                    updated_config = self._apply_schema(module_name, updated_config)
                
                # Update in memory
                self.module_configs[module_name] = updated_config
                
                # Persist to disk if requested
                if persist:
                    self._save_module_config(module_name, updated_config)
                
                logger.info(f"Updated config for {module_name}: {list(updates.keys())}")
                return True
                
            except Exception as e:
                logger.error(f"Error updating config for {module_name}: {e}")
                return False
    
    def _save_module_config(self, module_name: str, config: Dict[str, Any]):
        """Save module configuration to disk"""
        try:
            # Save to dedicated module file
            module_config_file = self.config_dir / f"{module_name}.json"
            
            with open(module_config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Also update main config if section exists there
            if module_name in self.main_config:
                self.main_config[module_name].update(config)
                self._save_main_config()
                
        except Exception as e:
            logger.error(f"Error saving config for {module_name}: {e}")
    
    def get_value(self, module_name: str, key: str, default: Any = None) -> Any:
        """Get a specific configuration value"""
        config = self.get_config(module_name)
        return config.get(key, default)
    
    def set_value(self, module_name: str, key: str, value: Any, persist: bool = True) -> bool:
        """Set a specific configuration value"""
        return self.update_config(module_name, {key: value}, persist)
    
    def validate_all_configs(self) -> Dict[str, List[str]]:
        """Validate all module configurations"""
        validation_errors = {}
        
        for module_name in self.schemas.keys():
            errors = []
            try:
                config = self.get_config(module_name)
                self._apply_schema(module_name, config)
            except Exception as e:
                errors.append(str(e))
            
            if errors:
                validation_errors[module_name] = errors
        
        return validation_errors
    
    def reload_all_configs(self):
        """Reload all module configurations from disk"""
        with self._config_lock:
            self._load_main_config()
            
            # Clear module configs to force reload
            module_names = list(self.module_configs.keys())
            self.module_configs.clear()
            
            # Reload each module
            for module_name in module_names:
                self._load_module_config(module_name)
            
            logger.info("Reloaded all configurations")
    
    def export_config(self, format: str = "json") -> str:
        """Export all configurations"""
        if format.lower() == "json":
            export_data = {
                "main_config": self.main_config,
                "module_configs": self.module_configs,
                "exported_at": datetime.now().isoformat()
            }
            return json.dumps(export_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of all configurations"""
        return {
            "config_dir": str(self.config_dir),
            "main_config_file": str(self.main_config_file),
            "registered_modules": list(self.schemas.keys()),
            "loaded_modules": list(self.module_configs.keys()),
            "main_config_sections": list(self.main_config.keys())
        }

# Global configuration manager instance
config_manager = ConfigManager()

# Convenience functions for common usage patterns
def get_ai_config() -> Dict[str, Any]:
    """Get AI core configuration"""
    return config_manager.get_config("ai_core")

def get_emotional_config() -> Dict[str, Any]:
    """Get emotional system configuration"""
    return config_manager.get_config("emotional_system")

def get_external_services_config() -> Dict[str, Any]:
    """Get external services configuration"""
    return config_manager.get_config("external_services")

def update_ai_config(updates: Dict[str, Any]) -> bool:
    """Update AI core configuration"""
    return config_manager.update_config("ai_core", updates)

def get_config_value(module: str, key: str, default: Any = None) -> Any:
    """Get a specific configuration value"""
    return config_manager.get_value(module, key, default)
