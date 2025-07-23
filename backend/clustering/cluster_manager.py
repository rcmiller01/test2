# cluster_manager.py
# Cluster management for UCS M3 servers

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
import socket
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ServerRole(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    GPU_WORKER = "gpu_worker"

class ServerStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"

@dataclass
class ServerInfo:
    server_id: str
    hostname: str
    ip_address: str
    port: int
    role: ServerRole
    status: ServerStatus
    gpu_count: int
    gpu_memory: Dict[str, int]
    cpu_cores: int
    memory_gb: int
    load_average: float
    last_heartbeat: datetime
    capabilities: List[str]

class ClusterManager:
    """Cluster manager for UCS M3 servers"""
    
    def __init__(self):
        self.servers: Dict[str, ServerInfo] = {}
        self.primary_server: Optional[str] = None
        self.gpu_server: Optional[str] = None
        self.load_balancer = None
        self.heartbeat_interval = 30  # seconds
        self.health_check_interval = 60  # seconds
        
        # Server configurations for UCS M3
        self.server_configs = {
            "m3-primary": {
                "hostname": "m3-primary",
                "ip_address": "192.168.1.10",  # Adjust to your network
                "port": 8000,
                "role": ServerRole.PRIMARY,
                "gpu_count": 0,
                "cpu_cores": 32,
                "memory_gb": 256,
                "capabilities": ["api", "websocket", "database", "load_balancer"]
            },
            "m3-gpu": {
                "hostname": "m3-gpu",
                "ip_address": "192.168.1.11",  # Adjust to your network
                "port": 8001,
                "role": ServerRole.GPU_WORKER,
                "gpu_count": 2,
                "cpu_cores": 32,
                "memory_gb": 256,
                "capabilities": ["gpu_processing", "ai_inference", "image_generation", "video_processing"]
            }
        }
    
    async def initialize_cluster(self):
        """Initialize the cluster with UCS M3 servers"""
        try:
            logger.info("Initializing UCS M3 cluster...")
            
            # Register servers
            for server_id, config in self.server_configs.items():
                server_info = ServerInfo(
                    server_id=server_id,
                    hostname=config["hostname"],
                    ip_address=config["ip_address"],
                    port=config["port"],
                    role=config["role"],
                    status=ServerStatus.OFFLINE,
                    gpu_count=config["gpu_count"],
                    gpu_memory={},
                    cpu_cores=config["cpu_cores"],
                    memory_gb=config["memory_gb"],
                    load_average=0.0,
                    last_heartbeat=datetime.now(),
                    capabilities=config["capabilities"]
                )
                
                self.servers[server_id] = server_info
                
                # Set primary and GPU server
                if config["role"] == ServerRole.PRIMARY:
                    self.primary_server = server_id
                elif config["role"] == ServerRole.GPU_WORKER:
                    self.gpu_server = server_id
            
            # Start health monitoring
            asyncio.create_task(self._health_monitor())
            asyncio.create_task(self._load_balancer())
            
            logger.info(f"Cluster initialized with {len(self.servers)} servers")
            logger.info(f"Primary server: {self.primary_server}")
            logger.info(f"GPU server: {self.gpu_server}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize cluster: {e}")
            return False
    
    async def register_server(self, server_id: str, server_info: ServerInfo):
        """Register a new server in the cluster"""
        try:
            self.servers[server_id] = server_info
            
            # Update primary/GPU server references
            if server_info.role == ServerRole.PRIMARY:
                self.primary_server = server_id
            elif server_info.role == ServerRole.GPU_WORKER:
                self.gpu_server = server_id
            
            logger.info(f"Server {server_id} registered in cluster")
            
        except Exception as e:
            logger.error(f"Failed to register server {server_id}: {e}")
    
    async def unregister_server(self, server_id: str):
        """Unregister a server from the cluster"""
        try:
            if server_id in self.servers:
                del self.servers[server_id]
                
                # Update references
                if self.primary_server == server_id:
                    self.primary_server = None
                if self.gpu_server == server_id:
                    self.gpu_server = None
                
                logger.info(f"Server {server_id} unregistered from cluster")
            
        except Exception as e:
            logger.error(f"Failed to unregister server {server_id}: {e}")
    
    async def get_server_info(self, server_id: str) -> Optional[ServerInfo]:
        """Get information about a specific server"""
        return self.servers.get(server_id)
    
    async def get_available_servers(self, capability: str = None) -> List[ServerInfo]:
        """Get list of available servers, optionally filtered by capability"""
        available_servers = []
        
        for server in self.servers.values():
            if server.status == ServerStatus.ONLINE:
                if capability is None or capability in server.capabilities:
                    available_servers.append(server)
        
        return available_servers
    
    async def get_gpu_server(self) -> Optional[ServerInfo]:
        """Get the GPU server for AI processing tasks"""
        if self.gpu_server and self.gpu_server in self.servers:
            server = self.servers[self.gpu_server]
            if server.status == ServerStatus.ONLINE:
                return server
        return None
    
    async def get_primary_server(self) -> Optional[ServerInfo]:
        """Get the primary server for API and database operations"""
        if self.primary_server and self.primary_server in self.servers:
            server = self.servers[self.primary_server]
            if server.status == ServerStatus.ONLINE:
                return server
        return None
    
    async def route_request(self, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Route requests to appropriate servers based on type"""
        try:
            if request_type in ["image_generation", "video_generation", "ai_inference"]:
                # Route to GPU server
                gpu_server = await self.get_gpu_server()
                if gpu_server:
                    return await self._send_request_to_server(gpu_server, request_type, data)
                else:
                    raise Exception("No GPU server available")
            
            elif request_type in ["api", "websocket", "database"]:
                # Route to primary server
                primary_server = await self.get_primary_server()
                if primary_server:
                    return await self._send_request_to_server(primary_server, request_type, data)
                else:
                    raise Exception("No primary server available")
            
            else:
                # Use load balancer for other requests
                return await self._load_balance_request(request_type, data)
                
        except Exception as e:
            logger.error(f"Failed to route request {request_type}: {e}")
            raise
    
    async def _send_request_to_server(self, server: ServerInfo, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to a specific server"""
        try:
            url = f"http://{server.ip_address}:{server.port}/api/cluster/{request_type}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Server {server.server_id} returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send request to server {server.server_id}: {e}")
            raise
    
    async def _load_balance_request(self, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Load balance request across available servers"""
        try:
            available_servers = await self.get_available_servers()
            
            if not available_servers:
                raise Exception("No servers available")
            
            # Simple round-robin load balancing
            # In production, you might want more sophisticated algorithms
            server = available_servers[0]  # For now, just use the first available
            
            return await self._send_request_to_server(server, request_type, data)
            
        except Exception as e:
            logger.error(f"Failed to load balance request: {e}")
            raise
    
    async def _health_monitor(self):
        """Monitor health of all servers in the cluster"""
        while True:
            try:
                for server_id, server in self.servers.items():
                    await self._check_server_health(server_id, server)
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _check_server_health(self, server_id: str, server: ServerInfo):
        """Check health of a specific server"""
        try:
            url = f"http://{server.ip_address}:{server.port}/health"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        
                        # Update server status
                        server.status = ServerStatus.ONLINE
                        server.last_heartbeat = datetime.now()
                        server.load_average = health_data.get("load_average", 0.0)
                        
                        # Update GPU memory if available
                        if "gpu_memory" in health_data:
                            server.gpu_memory = health_data["gpu_memory"]
                        
                        logger.debug(f"Server {server_id} health check passed")
                        
                    else:
                        server.status = ServerStatus.OFFLINE
                        logger.warning(f"Server {server_id} health check failed: status {response.status}")
                        
        except Exception as e:
            server.status = ServerStatus.OFFLINE
            logger.warning(f"Server {server_id} health check failed: {e}")
    
    async def _load_balancer(self):
        """Load balancer for distributing requests"""
        while True:
            try:
                # Monitor server loads and redistribute if necessary
                for server_id, server in self.servers.items():
                    if server.status == ServerStatus.ONLINE:
                        if server.load_average > 0.8:  # 80% load threshold
                            server.status = ServerStatus.OVERLOADED
                            logger.warning(f"Server {server_id} is overloaded (load: {server.load_average})")
                        elif server.status == ServerStatus.OVERLOADED and server.load_average < 0.6:
                            server.status = ServerStatus.ONLINE
                            logger.info(f"Server {server_id} load normalized (load: {server.load_average})")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Load balancer error: {e}")
                await asyncio.sleep(10)
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster status"""
        try:
            total_servers = len(self.servers)
            online_servers = len([s for s in self.servers.values() if s.status == ServerStatus.ONLINE])
            overloaded_servers = len([s for s in self.servers.values() if s.status == ServerStatus.OVERLOADED])
            
            # Calculate total GPU resources
            total_gpus = sum(s.gpu_count for s in self.servers.values() if s.status == ServerStatus.ONLINE)
            total_gpu_memory = sum(sum(s.gpu_memory.values()) for s in self.servers.values() if s.status == ServerStatus.ONLINE)
            
            return {
                "cluster_status": "healthy" if online_servers > 0 else "unhealthy",
                "total_servers": total_servers,
                "online_servers": online_servers,
                "overloaded_servers": overloaded_servers,
                "total_gpus": total_gpus,
                "total_gpu_memory_gb": total_gpu_memory,
                "primary_server_online": self.primary_server is not None and self.servers.get(self.primary_server, {}).status == ServerStatus.ONLINE,
                "gpu_server_online": self.gpu_server is not None and self.servers.get(self.gpu_server, {}).status == ServerStatus.ONLINE,
                "servers": {
                    server_id: {
                        "hostname": server.hostname,
                        "ip_address": server.ip_address,
                        "role": server.role.value,
                        "status": server.status.value,
                        "gpu_count": server.gpu_count,
                        "cpu_cores": server.cpu_cores,
                        "memory_gb": server.memory_gb,
                        "load_average": server.load_average,
                        "capabilities": server.capabilities,
                        "last_heartbeat": server.last_heartbeat.isoformat()
                    }
                    for server_id, server in self.servers.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster status: {e}")
            return {"error": str(e)}

# Global cluster manager instance
cluster_manager = ClusterManager()

# Initialize function
async def initialize_cluster():
    """Initialize the cluster"""
    return await cluster_manager.initialize_cluster()

# Health check endpoint for servers
async def server_health_check() -> Dict[str, Any]:
    """Health check endpoint for individual servers"""
    try:
        import psutil
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        load_average = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
        
        # Get GPU information if available
        gpu_memory = {}
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_memory[f"gpu_{i}"] = info.used // (1024**3)  # Convert to GB
                
        except ImportError:
            # pynvml not available, skip GPU info
            pass
        
        return {
            "status": "healthy",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available // (1024**3),
            "load_average": load_average,
            "gpu_memory": gpu_memory,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } 