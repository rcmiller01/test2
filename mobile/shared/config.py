# config.py
# Shared configuration for mobile app

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class MobileConfig:
    # API Configuration
    api_base_url: str
    api_timeout: int = 30
    api_retry_attempts: int = 3
    
    # Feature Flags
    enable_haptic_feedback: bool = True
    enable_biometric_monitoring: bool = True
    enable_vr_features: bool = True
    enable_voice_synthesis: bool = True
    enable_avatar_animations: bool = True
    
    # UI Configuration
    theme: str = "romantic"  # romantic, dark, light, custom
    animation_speed: float = 1.0
    haptic_intensity: str = "moderate"
    
    # Privacy Settings
    store_data_locally: bool = True
    enable_analytics: bool = False
    share_usage_data: bool = False
    
    # Performance Settings
    cache_duration: int = 3600  # seconds
    max_memory_cache: int = 100  # MB
    auto_sync_interval: int = 300  # seconds

class ConfigManager:
    def __init__(self):
        self.configs = {
            'development': MobileConfig(
                api_base_url="http://localhost:8000",
                enable_analytics=True,
                share_usage_data=True
            ),
            'staging': MobileConfig(
                api_base_url="https://staging.miasolene.com",
                enable_analytics=True,
                share_usage_data=False
            ),
            'production': MobileConfig(
                api_base_url="https://api.miasolene.com",
                enable_analytics=False,
                share_usage_data=False,
                store_data_locally=True
            )
        }
        self.current_env = os.getenv('MOBILE_ENV', 'development')
    
    def get_config(self, environment: str = None) -> MobileConfig:
        """Get configuration for specified environment"""
        env = environment or self.current_env
        return self.configs.get(env, self.configs['development'])
    
    def update_config(self, environment: str, **kwargs):
        """Update configuration for specified environment"""
        if environment in self.configs:
            current_config = self.configs[environment]
            for key, value in kwargs.items():
                if hasattr(current_config, key):
                    setattr(current_config, key, value)
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get current feature flags"""
        config = self.get_config()
        return {
            'haptic_feedback': config.enable_haptic_feedback,
            'biometric_monitoring': config.enable_biometric_monitoring,
            'vr_features': config.enable_vr_features,
            'voice_synthesis': config.enable_voice_synthesis,
            'avatar_animations': config.enable_avatar_animations
        }

# Default configuration instance
config_manager = ConfigManager()

# Convenience functions
def get_config() -> MobileConfig:
    """Get current configuration"""
    return config_manager.get_config()

def get_feature_flags() -> Dict[str, bool]:
    """Get current feature flags"""
    return config_manager.get_feature_flags()

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled"""
    flags = get_feature_flags()
    return flags.get(feature, False) 