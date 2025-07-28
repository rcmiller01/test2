"""
Configuration Manager - Centralized configuration management

This module handles all configuration for the House of Minds system,
including API keys, model settings, routing rules, and service endpoints.
"""

import logging
import yaml
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    type: str  # 'local', 'cloud', 'service'
    endpoint: str
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: float = 30.0
    enabled: bool = True
    specialized_for: List[str] = None  # Task types this model is good for
    
    def __post_init__(self):
        if self.specialized_for is None:
            self.specialized_for = []

@dataclass
class ServiceConfig:
    """Configuration for external services."""
    name: str
    endpoint: str
    api_key: Optional[str] = None
    timeout: float = 30.0
    enabled: bool = True
    webhook_url: Optional[str] = None
    auth_method: str = 'api_key'  # 'api_key', 'bearer', 'none'

class ConfigManager:
    """
    Centralized configuration management for House of Minds.
    
    Handles loading, validation, and management of all system configurations
    including models, services, routing rules, and API credentials.
    """
    
    def __init__(self, config_path: str = None):
        """Initialize the configuration manager."""
        self.config_path = config_path or self._find_config_file()
        self.config_data: Dict[str, Any] = {}
        
        # Configuration sections
        self.models: Dict[str, ModelConfig] = {}
        self.services: Dict[str, ServiceConfig] = {}
        self.routing_rules: Dict[str, Any] = {}
        self.system_settings: Dict[str, Any] = {}
        
        # Load configuration
        self._load_configuration()
        
        logger.info(f"⚙️ Configuration Manager initialized with {self.config_path}")
    
    def _find_config_file(self) -> str:
        """Find the configuration file in standard locations."""
        possible_paths = [
            './config.yaml',
            './config/config.yaml',
            './house_of_minds_config.yaml',
            os.path.expanduser('~/.house_of_minds/config.yaml'),
            '/etc/house_of_minds/config.yaml'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If no config file found, create a default one
        default_path = './config.yaml'
        self._create_default_config(default_path)
        return default_path
    
    def _load_configuration(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        self.config_data = yaml.safe_load(f) or {}
                    else:
                        self.config_data = json.load(f)
            else:
                logger.warning(f"Config file not found: {self.config_path}")
                self.config_data = {}
            
            # Parse configuration sections
            self._parse_models()
            self._parse_services()
            self._parse_routing_rules()
            self._parse_system_settings()
            
            logger.info("✅ Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            self._load_fallback_config()
    
    def _parse_models(self):
        """Parse model configurations."""
        models_config = self.config_data.get('models', {})
        
        for model_name, model_data in models_config.items():
            try:
                self.models[model_name] = ModelConfig(
                    name=model_name,
                    type=model_data.get('type', 'unknown'),
                    endpoint=model_data.get('endpoint', ''),
                    api_key=model_data.get('api_key'),
                    model_name=model_data.get('model_name', model_name),
                    temperature=model_data.get('temperature', 0.7),
                    max_tokens=model_data.get('max_tokens', 2000),
                    timeout=model_data.get('timeout', 30.0),
                    enabled=model_data.get('enabled', True),
                    specialized_for=model_data.get('specialized_for', [])
                )
            except Exception as e:
                logger.error(f"❌ Failed to parse model config for {model_name}: {e}")
    
    def _parse_services(self):
        """Parse service configurations."""
        services_config = self.config_data.get('services', {})
        
        for service_name, service_data in services_config.items():
            try:
                self.services[service_name] = ServiceConfig(
                    name=service_name,
                    endpoint=service_data.get('endpoint', ''),
                    api_key=service_data.get('api_key'),
                    timeout=service_data.get('timeout', 30.0),
                    enabled=service_data.get('enabled', True),
                    webhook_url=service_data.get('webhook_url'),
                    auth_method=service_data.get('auth_method', 'api_key')
                )
            except Exception as e:
                logger.error(f"❌ Failed to parse service config for {service_name}: {e}")
    
    def _parse_routing_rules(self):
        """Parse routing rules configuration."""
        self.routing_rules = self.config_data.get('routing', {})
        
        # Set defaults if not specified
        if 'intent_mapping' not in self.routing_rules:
            self.routing_rules['intent_mapping'] = {
                'conversation': ['dolphin', 'claude'],
                'planning': ['kimi', 'gpt4'],
                'code': ['claude', 'gpt4'],
                'utility': ['n8n'],
                'memory': ['memory_handler'],
                'analysis': ['kimi', 'claude'],
                'creative': ['dolphin', 'claude']
            }
        
        if 'fallback_model' not in self.routing_rules:
            self.routing_rules['fallback_model'] = 'dolphin'
        
        if 'max_retries' not in self.routing_rules:
            self.routing_rules['max_retries'] = 2
    
    def _parse_system_settings(self):
        """Parse system-wide settings."""
        self.system_settings = self.config_data.get('system', {})
        
        # Set defaults
        defaults = {
            'log_level': 'INFO',
            'max_concurrent_requests': 10,
            'request_timeout': 30.0,
            'memory_storage_path': './data/memory',
            'conversation_history_limit': 1000,
            'auto_consolidate_memory': True,
            'consolidation_interval_hours': 24,
            'health_check_interval': 300,  # 5 minutes
            'enable_metrics': True,
            'metrics_port': 8090
        }
        
        for key, default_value in defaults.items():
            if key not in self.system_settings:
                self.system_settings[key] = default_value
    
    def _load_fallback_config(self):
        """Load a minimal fallback configuration."""
        logger.warning("🔄 Loading fallback configuration")
        
        # Minimal working configuration
        self.models = {
            'dolphin': ModelConfig(
                name='dolphin',
                type='local',
                endpoint='http://localhost:11434',
                model_name='dolphin',
                specialized_for=['conversation', 'creative']
            ),
            'kimi': ModelConfig(
                name='kimi',
                type='local',
                endpoint='http://localhost:11434',
                model_name='kimik2',
                specialized_for=['planning', 'analysis']
            )
        }
        
        self.services = {
            'n8n': ServiceConfig(
                name='n8n',
                endpoint='http://localhost:5678',
                webhook_url='http://localhost:5678/webhook/house-of-minds'
            )
        }
        
        self.routing_rules = {
            'intent_mapping': {
                'conversation': ['dolphin'],
                'planning': ['kimi'],
                'code': ['kimi'],
                'utility': ['n8n'],
                'memory': ['memory_handler'],
                'analysis': ['kimi'],
                'creative': ['dolphin']
            },
            'fallback_model': 'dolphin',
            'max_retries': 2
        }
        
        self.system_settings = {
            'log_level': 'INFO',
            'max_concurrent_requests': 5,
            'request_timeout': 30.0
        }
    
    def _create_default_config(self, config_path: str):
        """Create a default configuration file."""
        default_config = {
            'models': {
                'dolphin': {
                    'type': 'local',
                    'endpoint': 'http://localhost:11434',
                    'model_name': 'dolphin',
                    'temperature': 0.8,
                    'max_tokens': 2000,
                    'timeout': 30.0,
                    'enabled': True,
                    'specialized_for': ['conversation', 'creative']
                },
                'kimi': {
                    'type': 'local',
                    'endpoint': 'http://localhost:11434',
                    'model_name': 'kimik2',
                    'temperature': 0.3,
                    'max_tokens': 3000,
                    'timeout': 45.0,
                    'enabled': True,
                    'specialized_for': ['planning', 'analysis', 'code']
                },
                'claude': {
                    'type': 'cloud',
                    'endpoint': 'https://openrouter.ai/api/v1',
                    'model_name': 'anthropic/claude-3-sonnet',
                    'api_key': '${OPENROUTER_API_KEY}',
                    'temperature': 0.7,
                    'max_tokens': 4000,
                    'timeout': 60.0,
                    'enabled': False,  # Disabled by default, requires API key
                    'specialized_for': ['code', 'analysis', 'conversation']
                },
                'gpt4': {
                    'type': 'cloud',
                    'endpoint': 'https://openrouter.ai/api/v1',
                    'model_name': 'openai/gpt-4-turbo',
                    'api_key': '${OPENROUTER_API_KEY}',
                    'temperature': 0.7,
                    'max_tokens': 4000,
                    'timeout': 60.0,
                    'enabled': False,  # Disabled by default, requires API key
                    'specialized_for': ['planning', 'code', 'analysis']
                }
            },
            'services': {
                'n8n': {
                    'endpoint': 'http://localhost:5678',
                    'webhook_url': 'http://localhost:5678/webhook/house-of-minds',
                    'timeout': 30.0,
                    'enabled': True,
                    'auth_method': 'none'
                },
                'openrouter': {
                    'endpoint': 'https://openrouter.ai/api/v1',
                    'api_key': '${OPENROUTER_API_KEY}',
                    'timeout': 60.0,
                    'enabled': False,  # Disabled by default
                    'auth_method': 'bearer'
                }
            },
            'routing': {
                'intent_mapping': {
                    'conversation': ['dolphin', 'claude'],
                    'planning': ['kimi', 'gpt4'],
                    'code': ['claude', 'kimi', 'gpt4'],
                    'utility': ['n8n'],
                    'memory': ['memory_handler'],
                    'analysis': ['kimi', 'claude'],
                    'creative': ['dolphin', 'claude']
                },
                'fallback_model': 'dolphin',
                'max_retries': 2,
                'confidence_threshold': 0.6,
                'load_balancing': True
            },
            'system': {
                'log_level': 'INFO',
                'max_concurrent_requests': 10,
                'request_timeout': 30.0,
                'memory_storage_path': './data/memory',
                'conversation_history_limit': 1000,
                'auto_consolidate_memory': True,
                'consolidation_interval_hours': 24,
                'health_check_interval': 300,
                'enable_metrics': True,
                'metrics_port': 8090,
                'cors_enabled': True,
                'cors_origins': ['http://localhost:3000', 'http://localhost:8080']
            }
        }
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path) if os.path.dirname(config_path) else '.', exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            
            logger.info(f"📄 Created default configuration file: {config_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create default config: {e}")
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model."""
        return self.models.get(model_name)
    
    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """Get configuration for a specific service."""
        return self.services.get(service_name)
    
    def get_routing_config(self) -> Dict[str, Any]:
        """Get routing configuration."""
        return self.routing_rules
    
    def get_system_setting(self, setting_name: str, default_value: Any = None) -> Any:
        """Get a system setting value."""
        return self.system_settings.get(setting_name, default_value)
    
    def get_models_for_intent(self, intent: str) -> List[str]:
        """Get list of models that can handle a specific intent."""
        intent_mapping = self.routing_rules.get('intent_mapping', {})
        return intent_mapping.get(intent, [])
    
    def get_enabled_models(self) -> Dict[str, ModelConfig]:
        """Get all enabled models."""
        return {name: config for name, config in self.models.items() if config.enabled}
    
    def get_enabled_services(self) -> Dict[str, ServiceConfig]:
        """Get all enabled services."""
        return {name: config for name, config in self.services.items() if config.enabled}
    
    def set_model_enabled(self, model_name: str, enabled: bool) -> bool:
        """Enable or disable a model."""
        if model_name in self.models:
            self.models[model_name].enabled = enabled
            logger.info(f"🔧 Model {model_name} {'enabled' if enabled else 'disabled'}")
            return True
        return False
    
    def set_service_enabled(self, service_name: str, enabled: bool) -> bool:
        """Enable or disable a service."""
        if service_name in self.services:
            self.services[service_name].enabled = enabled
            logger.info(f"🔧 Service {service_name} {'enabled' if enabled else 'disabled'}")
            return True
        return False
    
    def update_api_key(self, model_or_service: str, api_key: str) -> bool:
        """Update API key for a model or service."""
        updated = False
        
        if model_or_service in self.models:
            self.models[model_or_service].api_key = api_key
            updated = True
        
        if model_or_service in self.services:
            self.services[model_or_service].api_key = api_key
            updated = True
        
        if updated:
            logger.info(f"🔑 Updated API key for {model_or_service}")
        
        return updated
    
    def resolve_environment_variables(self, value: str) -> str:
        """Resolve environment variable references in configuration values."""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.getenv(env_var, value)  # Return original if not found
        return value
    
    def validate_configuration(self) -> List[str]:
        """Validate the current configuration and return list of issues."""
        issues = []
        
        # Check if we have at least one enabled model
        enabled_models = self.get_enabled_models()
        if not enabled_models:
            issues.append("No enabled models found")
        
        # Check model configurations
        for name, model in self.models.items():
            if model.enabled:
                if not model.endpoint:
                    issues.append(f"Model {name}: Missing endpoint")
                
                if model.type == 'cloud' and not model.api_key:
                    resolved_key = self.resolve_environment_variables(model.api_key or "")
                    if not resolved_key or resolved_key.startswith('${'):
                        issues.append(f"Model {name}: Missing or unresolved API key")
        
        # Check service configurations
        for name, service in self.services.items():
            if service.enabled:
                if not service.endpoint:
                    issues.append(f"Service {name}: Missing endpoint")
                
                if service.auth_method == 'api_key' and not service.api_key:
                    resolved_key = self.resolve_environment_variables(service.api_key or "")
                    if not resolved_key or resolved_key.startswith('${'):
                        issues.append(f"Service {name}: Missing or unresolved API key")
        
        # Check routing configuration
        if not self.routing_rules.get('fallback_model'):
            issues.append("No fallback model specified in routing")
        
        fallback_model = self.routing_rules.get('fallback_model')
        if fallback_model and fallback_model not in enabled_models:
            issues.append(f"Fallback model '{fallback_model}' is not enabled or configured")
        
        return issues
    
    def save_configuration(self, backup: bool = True) -> bool:
        """Save current configuration to file."""
        try:
            # Create backup if requested
            if backup and os.path.exists(self.config_path):
                backup_path = f"{self.config_path}.backup"
                os.rename(self.config_path, backup_path)
                logger.info(f"📄 Created configuration backup: {backup_path}")
            
            # Reconstruct configuration data
            config_data = {
                'models': {},
                'services': {},
                'routing': self.routing_rules,
                'system': self.system_settings
            }
            
            # Convert model configs back to dict format
            for name, model in self.models.items():
                config_data['models'][name] = {
                    'type': model.type,
                    'endpoint': model.endpoint,
                    'api_key': model.api_key,
                    'model_name': model.model_name,
                    'temperature': model.temperature,
                    'max_tokens': model.max_tokens,
                    'timeout': model.timeout,
                    'enabled': model.enabled,
                    'specialized_for': model.specialized_for
                }
            
            # Convert service configs back to dict format
            for name, service in self.services.items():
                config_data['services'][name] = {
                    'endpoint': service.endpoint,
                    'api_key': service.api_key,
                    'timeout': service.timeout,
                    'enabled': service.enabled,
                    'webhook_url': service.webhook_url,
                    'auth_method': service.auth_method
                }
            
            # Save to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_data, f, indent=2)
            
            logger.info(f"💾 Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
            return False
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        enabled_models = self.get_enabled_models()
        enabled_services = self.get_enabled_services()
        validation_issues = self.validate_configuration()
        
        return {
            'config_file': self.config_path,
            'models': {
                'total': len(self.models),
                'enabled': len(enabled_models),
                'enabled_models': list(enabled_models.keys())
            },
            'services': {
                'total': len(self.services),
                'enabled': len(enabled_services),
                'enabled_services': list(enabled_services.keys())
            },
            'routing': {
                'fallback_model': self.routing_rules.get('fallback_model'),
                'intent_mappings': len(self.routing_rules.get('intent_mapping', {}))
            },
            'system_settings': {
                'log_level': self.system_settings.get('log_level'),
                'max_concurrent_requests': self.system_settings.get('max_concurrent_requests'),
                'memory_enabled': bool(self.system_settings.get('memory_storage_path'))
            },
            'validation': {
                'is_valid': len(validation_issues) == 0,
                'issues': validation_issues
            }
        }
