#!/usr/bin/env python3
"""
Agent Registry Manager - Dynamic agent discovery and management

This module handles loading, reloading, and managing agents from the registry.json file.
It provides hot-swappable agent definitions without requiring server restarts.

Author: Dolphin AI System
Date: July 30, 2025
Tag: #ref-mcp-integration
"""

import json
import logging
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class AgentRegistryHandler(FileSystemEventHandler):
    """File system event handler for registry.json changes"""
    
    def __init__(self, registry_manager):
        self.registry_manager = registry_manager
        
    def on_modified(self, event):
        if event.src_path.endswith('registry.json'):
            logger.info("Agent registry file modified, reloading...")
            asyncio.create_task(self.registry_manager.reload_registry())

class AgentRegistryManager:
    """
    Manages dynamic agent registry with hot-reloading capabilities
    """
    
    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path or self._get_default_registry_path()
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.agent_types: Dict[str, Dict[str, Any]] = {}
        self.global_settings: Dict[str, Any] = {}
        self.registry_version: str = "unknown"
        self.last_loaded: Optional[datetime] = None
        self.file_observer: Optional[Observer] = None
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.agent_health_status: Dict[str, Dict[str, Any]] = {}
        
    def _get_default_registry_path(self) -> str:
        """Get the default path to the agent registry file"""
        current_dir = Path(__file__).parent
        return str(current_dir / "agents" / "registry.json")
    
    async def initialize(self, enable_file_watching: bool = True) -> None:
        """
        Initialize the agent registry manager
        
        Args:
            enable_file_watching: Whether to enable automatic file watching for hot-reload
        """
        logger.info(f"Initializing Agent Registry Manager with path: {self.registry_path}")
        
        await self.load_registry()
        
        if enable_file_watching:
            self._start_file_watching()
            
        # Start health checking for enabled agents
        await self._start_health_checking()
        
    async def shutdown(self) -> None:
        """Shutdown the registry manager and clean up resources"""
        logger.info("Shutting down Agent Registry Manager")
        
        # Stop file watching
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
            
        # Cancel health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()
            
        try:
            await asyncio.gather(*self.health_check_tasks.values(), return_exceptions=True)
        except Exception as e:
            logger.error(f"Error cancelling health check tasks: {e}")
            
    async def load_registry(self) -> None:
        """Load agent registry from JSON file"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
                
            # Validate registry structure
            self._validate_registry_structure(registry_data)
            
            # Load registry data
            self.agents = registry_data.get('agents', {})
            self.agent_types = registry_data.get('agent_types', {})
            self.global_settings = registry_data.get('global_settings', {})
            self.registry_version = registry_data.get('version', 'unknown')
            self.last_loaded = datetime.now()
            
            # Filter enabled agents
            enabled_agents = {name: config for name, config in self.agents.items() 
                            if config.get('enabled', True)}
            
            logger.info(f"Loaded agent registry v{self.registry_version} with {len(enabled_agents)} enabled agents")
            logger.debug(f"Enabled agents: {list(enabled_agents.keys())}")
            
        except FileNotFoundError:
            logger.error(f"Agent registry file not found: {self.registry_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in agent registry: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading agent registry: {e}")
            raise
            
    async def reload_registry(self) -> None:
        """Reload the agent registry (used for hot-reloading)"""
        try:
            old_agents = set(self.agents.keys())
            await self.load_registry()
            new_agents = set(self.agents.keys())
            
            # Calculate differences
            added_agents = new_agents - old_agents
            removed_agents = old_agents - new_agents
            modified_agents = old_agents & new_agents
            
            if added_agents:
                logger.info(f"Added agents: {list(added_agents)}")
                
            if removed_agents:
                logger.info(f"Removed agents: {list(removed_agents)}")
                # Stop health checking for removed agents
                for agent_name in removed_agents:
                    await self._stop_health_check(agent_name)
                    
            if modified_agents:
                logger.info(f"Modified agents: {list(modified_agents)}")
                
            # Restart health checking for all current agents
            await self._restart_health_checking()
            
        except Exception as e:
            logger.error(f"Error reloading agent registry: {e}")
            
    def _validate_registry_structure(self, registry_data: Dict[str, Any]) -> None:
        """Validate the structure of the registry data"""
        required_keys = ['agents', 'agent_types']
        for key in required_keys:
            if key not in registry_data:
                raise ValueError(f"Missing required key in registry: {key}")
                
        # Validate each agent has required fields
        for agent_name, agent_config in registry_data['agents'].items():
            required_agent_keys = ['type', 'description']
            for key in required_agent_keys:
                if key not in agent_config:
                    raise ValueError(f"Agent '{agent_name}' missing required key: {key}")
                    
            # Validate agent type exists
            agent_type = agent_config['type']
            if agent_type not in registry_data['agent_types']:
                raise ValueError(f"Agent '{agent_name}' references unknown type: {agent_type}")
                
    def _start_file_watching(self) -> None:
        """Start watching the registry file for changes"""
        try:
            registry_dir = Path(self.registry_path).parent
            event_handler = AgentRegistryHandler(self)
            self.file_observer = Observer()
            self.file_observer.schedule(event_handler, str(registry_dir), recursive=False)
            self.file_observer.start()
            logger.info(f"Started watching registry directory: {registry_dir}")
        except Exception as e:
            logger.error(f"Failed to start file watching: {e}")
            
    async def _start_health_checking(self) -> None:
        """Start health checking tasks for all enabled agents"""
        if not self.global_settings.get('health_check_enabled', True):
            logger.info("Health checking disabled globally")
            return
            
        for agent_name, agent_config in self.agents.items():
            if agent_config.get('enabled', True):
                await self._start_health_check(agent_name, agent_config)
                
    async def _restart_health_checking(self) -> None:
        """Restart all health checking tasks"""
        # Cancel existing tasks
        for task in self.health_check_tasks.values():
            task.cancel()
        self.health_check_tasks.clear()
        
        # Start new tasks
        await self._start_health_checking()
        
    async def _start_health_check(self, agent_name: str, agent_config: Dict[str, Any]) -> None:
        """Start health checking for a specific agent"""
        health_config = agent_config.get('health_check', {})
        if health_config.get('method') == 'INTERNAL':
            # Internal agents are always considered healthy
            self.agent_health_status[agent_name] = {
                'status': 'online',
                'last_check': datetime.now().isoformat(),
                'response_time_ms': 0
            }
            return
            
        interval = health_config.get('interval', self.global_settings.get('health_check_interval', 60))
        task = asyncio.create_task(self._health_check_loop(agent_name, agent_config, interval))
        self.health_check_tasks[agent_name] = task
        
    async def _stop_health_check(self, agent_name: str) -> None:
        """Stop health checking for a specific agent"""
        if agent_name in self.health_check_tasks:
            self.health_check_tasks[agent_name].cancel()
            del self.health_check_tasks[agent_name]
        if agent_name in self.agent_health_status:
            del self.agent_health_status[agent_name]
            
    async def _health_check_loop(self, agent_name: str, agent_config: Dict[str, Any], interval: int) -> None:
        """Health check loop for a specific agent"""
        import httpx
        
        while True:
            try:
                health_config = agent_config.get('health_check', {})
                url = health_config.get('url')
                method = health_config.get('method', 'GET')
                
                if not url:
                    # Skip health check if no URL configured
                    await asyncio.sleep(interval)
                    continue
                    
                start_time = time.time()
                
                async with httpx.AsyncClient(timeout=5.0) as client:
                    if method.upper() == 'GET':
                        response = await client.get(url)
                    else:
                        response = await client.post(url)
                        
                response_time = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    self.agent_health_status[agent_name] = {
                        'status': 'online',
                        'last_check': datetime.now().isoformat(),
                        'response_time_ms': response_time
                    }
                else:
                    self.agent_health_status[agent_name] = {
                        'status': 'error',
                        'last_check': datetime.now().isoformat(),
                        'response_time_ms': response_time,
                        'error': f"HTTP {response.status_code}"
                    }
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.agent_health_status[agent_name] = {
                    'status': 'offline',
                    'last_check': datetime.now().isoformat(),
                    'error': str(e)
                }
                
            await asyncio.sleep(interval)
            
    def get_enabled_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all enabled agents"""
        return {name: config for name, config in self.agents.items() 
                if config.get('enabled', True)}
                
    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent"""
        return self.agents.get(agent_name)
        
    def is_agent_enabled(self, agent_name: str) -> bool:
        """Check if an agent is enabled"""
        agent_config = self.get_agent_config(agent_name)
        return agent_config.get('enabled', True) if agent_config else False
        
    def get_agents_by_capability(self, capability: str) -> List[str]:
        """Get all enabled agents that have a specific capability"""
        matching_agents = []
        for name, config in self.get_enabled_agents().items():
            capabilities = config.get('capabilities', [])
            if capability in capabilities:
                matching_agents.append(name)
        return matching_agents
        
    def get_agents_by_type(self, agent_type: str) -> List[str]:
        """Get all enabled agents of a specific type"""
        matching_agents = []
        for name, config in self.get_enabled_agents().items():
            if config.get('type') == agent_type:
                matching_agents.append(name)
        return matching_agents
        
    def get_agent_health(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get health status for a specific agent"""
        return self.agent_health_status.get(agent_name)
        
    def get_all_agent_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all agents"""
        return self.agent_health_status.copy()
        
    def get_registry_info(self) -> Dict[str, Any]:
        """Get registry metadata information"""
        return {
            'version': self.registry_version,
            'last_loaded': self.last_loaded.isoformat() if self.last_loaded else None,
            'total_agents': len(self.agents),
            'enabled_agents': len(self.get_enabled_agents()),
            'agent_types': list(self.agent_types.keys()),
            'global_settings': self.global_settings
        }
        
    async def enable_agent(self, agent_name: str) -> bool:
        """Enable an agent (runtime change, not persisted)"""
        if agent_name in self.agents:
            self.agents[agent_name]['enabled'] = True
            await self._start_health_check(agent_name, self.agents[agent_name])
            logger.info(f"Enabled agent: {agent_name}")
            return True
        return False
        
    async def disable_agent(self, agent_name: str) -> bool:
        """Disable an agent (runtime change, not persisted)"""
        if agent_name in self.agents:
            self.agents[agent_name]['enabled'] = False
            await self._stop_health_check(agent_name)
            logger.info(f"Disabled agent: {agent_name}")
            return True
        return False

# Global registry manager instance
registry_manager = AgentRegistryManager()
