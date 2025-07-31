#!/usr/bin/env python3
"""
Configuration Manager for Dolphin AI House of Minds

This module provides comprehensive configuration management for the entire
Dolphin AI system including MCP integration, Ollama settings, and service endpoints.

Author: Dolphin AI System
Date: July 30, 2025
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)

@dataclass
class MCPConfig:
    """MCP (Model Context Protocol) configuration"""
    enabled: bool = True
    host: str = "localhost"
    port: int = 8000
    base_url: str = ""
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    health_check_interval: int = 60
    
    def __post_init__(self):
        if not self.base_url:
            self.base_url = f"http://{self.host}:{self.port}"

@dataclass
class OllamaConfig:
    """Ollama API configuration"""
    enabled: bool = False  # Disabled by default since it requires Ollama server
    host: str = "localhost"
    port: int = 11434
    base_url: str = ""
    default_model: str = "llama2"
    timeout: int = 120
    max_retries: int = 3
    stream: bool = True
    
    def __post_init__(self):
        if not self.base_url:
            self.base_url = f"http://{self.host}:{self.port}"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "dolphin_ai"
    username: str = ""
    password: str = ""
    url: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False
    
    def __post_init__(self):
        if not self.url:
            if self.type == "sqlite":
                self.url = f"sqlite:///./storage/{self.database}.db"
            elif self.type == "postgresql":
                self.url = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "./logs/dolphin_ai.log"
    console_enabled: bool = True
    max_file_size: int = 10_000_000  # 10MB
    backup_count: int = 5

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    api_rate_limit: int = 100  # requests per minute
    enable_authentication: bool = False

@dataclass
class PerformanceConfig:
    """Performance and concurrency configuration"""
    max_concurrent_requests: int = 10
    worker_processes: int = 1
    memory_limit_mb: int = 1024
    request_timeout: int = 300
    keep_alive_timeout: int = 65
    max_request_size: int = 16_777_216  # 16MB

@dataclass
class DolphinConfig:
    """
    Main configuration class for Dolphin AI system
    """
    
    # Environment and deployment
    environment: str = "development"
    debug: bool = True
    version: str = "2.1.0"
    
    # Service configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Component configurations
    mcp: MCPConfig = field(default_factory=MCPConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Feature flags
    enable_mcp_integration: bool = True
    enable_ollama_integration: bool = False  # Disabled by default
    enable_memory_system: bool = True
    enable_quantization: bool = True
    enable_analytics: bool = True
    
    def update_from_env(self):
        """Update configuration from environment variables"""
        # Basic settings
        self.environment = os.getenv("DOLPHIN_ENV", self.environment)
        self.debug = os.getenv("DOLPHIN_DEBUG", str(self.debug)).lower() == "true"
        self.host = os.getenv("DOLPHIN_HOST", self.host)
        self.port = int(os.getenv("DOLPHIN_PORT", str(self.port)))
        
        # Feature flags
        self.enable_mcp_integration = os.getenv("ENABLE_MCP", str(self.enable_mcp_integration)).lower() == "true"
        self.enable_ollama_integration = os.getenv("ENABLE_OLLAMA", str(self.enable_ollama_integration)).lower() == "true"
        self.enable_memory_system = os.getenv("ENABLE_MEMORY", str(self.enable_memory_system)).lower() == "true"
        self.enable_quantization = os.getenv("ENABLE_QUANTIZATION", str(self.enable_quantization)).lower() == "true"
        self.enable_analytics = os.getenv("ENABLE_ANALYTICS", str(self.enable_analytics)).lower() == "true"
        
        # MCP configuration
        mcp_host = os.getenv("MCP_HOST")
        if mcp_host:
            self.mcp.host = mcp_host
        
        mcp_port = os.getenv("MCP_PORT")
        if mcp_port:
            self.mcp.port = int(mcp_port)
            
        mcp_base_url = os.getenv("MCP_BASE_URL")
        if mcp_base_url:
            self.mcp.base_url = mcp_base_url
        else:
            self.mcp.base_url = f"http://{self.mcp.host}:{self.mcp.port}"
            
        # Ollama configuration
        ollama_host = os.getenv("OLLAMA_HOST")
        if ollama_host:
            self.ollama.host = ollama_host
            
        ollama_port = os.getenv("OLLAMA_PORT")
        if ollama_port:
            self.ollama.port = int(ollama_port)
            
        ollama_base_url = os.getenv("OLLAMA_BASE_URL")
        if ollama_base_url:
            self.ollama.base_url = ollama_base_url
        else:
            self.ollama.base_url = f"http://{self.ollama.host}:{self.ollama.port}"
            
        ollama_model = os.getenv("OLLAMA_MODEL")
        if ollama_model:
            self.ollama.default_model = ollama_model
            
        # Database configuration
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            self.database.url = database_url
    
    def save_to_file(self, file_path: str):
        """Save configuration to JSON file"""
        config_dict = self.to_dict()
        
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
        
        logger.info(f"Configuration saved to {file_path}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'environment': self.environment,
            'debug': self.debug,
            'version': self.version,
            'host': self.host,
            'port': self.port,
            'mcp': {
                'enabled': self.mcp.enabled,
                'host': self.mcp.host,
                'port': self.mcp.port,
                'base_url': self.mcp.base_url,
                'timeout': self.mcp.timeout,
                'retry_attempts': self.mcp.retry_attempts,
                'retry_delay': self.mcp.retry_delay,
                'health_check_interval': self.mcp.health_check_interval
            },
            'ollama': {
                'enabled': self.ollama.enabled,
                'host': self.ollama.host,
                'port': self.ollama.port,
                'base_url': self.ollama.base_url,
                'default_model': self.ollama.default_model,
                'timeout': self.ollama.timeout,
                'max_retries': self.ollama.max_retries,
                'stream': self.ollama.stream
            },
            'database': {
                'type': self.database.type,
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database,
                'url': self.database.url,
                'pool_size': self.database.pool_size,
                'max_overflow': self.database.max_overflow,
                'echo': self.database.echo
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file_enabled': self.logging.file_enabled,
                'file_path': self.logging.file_path,
                'console_enabled': self.logging.console_enabled,
                'max_file_size': self.logging.max_file_size,
                'backup_count': self.logging.backup_count
            },
            'security': {
                'jwt_algorithm': self.security.jwt_algorithm,
                'jwt_expiration_hours': self.security.jwt_expiration_hours,
                'cors_origins': self.security.cors_origins,
                'api_rate_limit': self.security.api_rate_limit,
                'enable_authentication': self.security.enable_authentication
            },
            'performance': {
                'max_concurrent_requests': self.performance.max_concurrent_requests,
                'worker_processes': self.performance.worker_processes,
                'memory_limit_mb': self.performance.memory_limit_mb,
                'request_timeout': self.performance.request_timeout,
                'keep_alive_timeout': self.performance.keep_alive_timeout,
                'max_request_size': self.performance.max_request_size
            },
            'enable_mcp_integration': self.enable_mcp_integration,
            'enable_ollama_integration': self.enable_ollama_integration,
            'enable_memory_system': self.enable_memory_system,
            'enable_quantization': self.enable_quantization,
            'enable_analytics': self.enable_analytics
        }
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'DolphinConfig':
        """Load configuration from JSON file"""
        if not Path(file_path).exists():
            logger.warning(f"Configuration file not found: {file_path}, using defaults")
            return cls()
        
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        
        # Create config with defaults
        config = cls()
        
        # Update basic settings
        if 'environment' in config_data:
            config.environment = config_data['environment']
        if 'debug' in config_data:
            config.debug = config_data['debug']
        if 'host' in config_data:
            config.host = config_data['host']
        if 'port' in config_data:
            config.port = config_data['port']
        
        # Update MCP settings
        if 'mcp' in config_data:
            mcp_data = config_data['mcp']
            config.mcp = MCPConfig(**mcp_data)
        
        # Update Ollama settings
        if 'ollama' in config_data:
            ollama_data = config_data['ollama']
            config.ollama = OllamaConfig(**ollama_data)
        
        # Update other sections as needed
        if 'database' in config_data:
            config.database = DatabaseConfig(**config_data['database'])
        if 'logging' in config_data:
            config.logging = LoggingConfig(**config_data['logging'])
        if 'security' in config_data:
            config.security = SecurityConfig(**config_data['security'])
        if 'performance' in config_data:
            config.performance = PerformanceConfig(**config_data['performance'])
        
        # Update feature flags
        feature_flags = [
            'enable_mcp_integration', 'enable_ollama_integration',
            'enable_memory_system', 'enable_quantization', 'enable_analytics'
        ]
        for flag in feature_flags:
            if flag in config_data:
                setattr(config, flag, config_data[flag])
        
        logger.info(f"Configuration loaded from {file_path}")
        return config
    
    def get_mcp_endpoint(self, path: str = "") -> str:
        """Get full MCP endpoint URL"""
        base = self.mcp.base_url.rstrip('/')
        if path:
            path = path.lstrip('/')
            return f"{base}/{path}"
        return base
    
    def get_ollama_endpoint(self, path: str = "") -> str:
        """Get full Ollama endpoint URL"""
        base = self.ollama.base_url.rstrip('/')
        if path:
            path = path.lstrip('/')
            return f"{base}/{path}"
        return base
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"

class ConfigManager:
    """
    Singleton configuration manager for the Dolphin AI system
    """
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[DolphinConfig] = None
    
    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.reload_config()
    
    def reload_config(self, config_file: Optional[str] = None):
        """Reload configuration from file or environment"""
        if config_file and Path(config_file).exists():
            self._config = DolphinConfig.load_from_file(config_file)
        else:
            self._config = DolphinConfig()
        
        # Update from environment variables
        self._config.update_from_env()
        
        # Setup logging based on configuration
        self._setup_logging()
        
        logger.info("Configuration loaded successfully")
        logger.debug(f"Environment: {self._config.environment}")
        logger.debug(f"MCP enabled: {self._config.enable_mcp_integration}")
        logger.debug(f"Ollama enabled: {self._config.enable_ollama_integration}")
    
    def _setup_logging(self):
        """Setup logging based on configuration"""
        if self._config is None:
            return
            
        log_config = self._config.logging
        
        # Create logs directory if it doesn't exist
        if log_config.file_enabled:
            Path(log_config.file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_config.level),
            format=log_config.format,
            handlers=[]
        )
        
        # Add console handler
        if log_config.console_enabled:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(log_config.format))
            logging.getLogger().addHandler(console_handler)
        
        # Add file handler with rotation
        if log_config.file_enabled:
            try:
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    log_config.file_path,
                    maxBytes=log_config.max_file_size,
                    backupCount=log_config.backup_count
                )
                file_handler.setFormatter(logging.Formatter(log_config.format))
                logging.getLogger().addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Failed to setup file logging: {e}")
    
    @property
    def config(self) -> DolphinConfig:
        """Get the current configuration"""
        if self._config is None:
            self.reload_config()
        assert self._config is not None
        return self._config
    
    def get_config(self) -> DolphinConfig:
        """Get the current configuration (alias for config property)"""
        return self.config
    
    def update_config(self, **kwargs):
        """Update configuration values at runtime"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
                logger.info(f"Configuration updated: {key} = {value}")
            else:
                logger.warning(f"Unknown configuration key: {key}")

# Global configuration manager instance
config_manager = ConfigManager()

# Convenience function to get configuration
def get_config() -> DolphinConfig:
    """Get the global configuration instance"""
    return config_manager.get_config()