# MCP Server - Master Control Program

## 🚀 **Dynamic Agent Discovery & Registry System**

The MCP Server now features a powerful dynamic agent registry system that allows for hot-swappable agent definitions without requiring server restarts. This enables Dolphin AI and other systems to programmatically discover available capabilities and route tasks efficiently.

## 📋 **Features**

### **Dynamic Agent Registry**
- **Hot-Reloadable Configuration**: Agents defined in `agents/registry.json` with automatic file watching
- **Runtime Agent Management**: Enable/disable agents without server restart
- **Capability-Based Discovery**: Query agents by their capabilities
- **Health Monitoring**: Automatic health checking for all agent types
- **Type-Safe Configuration**: Comprehensive validation of agent definitions

### **Agent Types Supported**
- **n8n Workflows**: Webhook-based automation platform integration
- **OpenRouter APIs**: AI model routing and chat capabilities  
- **Local Handlers**: File system, system monitoring, and local operations
- **External Services**: Weather, web search, and third-party APIs

### **Advanced Management**
- **Priority-Based Routing**: Agents have configurable priority levels
- **Timeout Management**: Per-agent timeout configuration
- **Input Schema Validation**: Structured payload requirements
- **Concurrent Health Checks**: Parallel agent monitoring
- **Automatic Failure Handling**: Auto-disable failed agents

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Dolphin AI    │────│   MCP Server     │────│   Agent Pool    │
│                 │    │                  │    │                 │
│ - Chat Analysis │    │ - Route Tasks    │    │ - n8n Workflows │
│ - Intent Detect │    │ - Load Balance   │    │ - OpenRouter    │
│ - Task Routing  │    │ - Health Monitor │    │ - Local Handlers│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 **File Structure**

```
core1-gateway/
├── mcp_server.py              # Main FastAPI server
├── agent_registry.py          # Dynamic registry manager
├── start_mcp_server.py        # Startup script
├── test_mcp_registry.py       # Test suite
├── requirements_mcp.txt       # Dependencies
└── agents/
    └── registry.json          # Agent definitions
```

## 🔧 **Configuration**

### **Agent Registry (agents/registry.json)**

```json
{
  "version": "1.0.0",
  "agents": {
    "reminder": {
      "type": "n8n",
      "enabled": true,
      "webhook": "http://localhost:5678/webhook/create-reminder",
      "timeout": 30,
      "priority": 5,
      "description": "Creates reminders via n8n workflow",
      "capabilities": ["scheduling", "reminders", "notifications"],
      "input_schema": {
        "required": ["message", "datetime"],
        "optional": ["priority", "category"]
      },
      "health_check": {
        "method": "GET",
        "url": "http://localhost:5678/healthz",
        "interval": 60
      }
    }
  },
  "global_settings": {
    "max_concurrent_requests": 10,
    "health_check_enabled": true,
    "auto_disable_failed_agents": true
  }
}
```

## 🚦 **API Endpoints**

### **Core Routing**
- `POST /api/mcp/route-task` - Route tasks to agents
- `GET /api/mcp/status` - System health and metrics

### **Agent Management**
- `GET /api/mcp/agents` - List all agents
- `GET /api/mcp/agents/{name}` - Get agent details
- `POST /api/mcp/agents/{name}/enable` - Enable agent
- `POST /api/mcp/agents/{name}/disable` - Disable agent

### **Discovery & Capabilities**
- `GET /api/mcp/agents/capabilities` - List capabilities
- `GET /api/mcp/agents/capabilities?capability=X` - Filter by capability

### **Registry Management**
- `GET /api/mcp/registry/info` - Registry metadata
- `POST /api/mcp/registry/reload` - Hot-reload registry

## 🛠️ **Installation & Setup**

### **1. Install Dependencies**
```bash
cd core1-gateway
pip install -r requirements_mcp.txt
```

### **2. Configure Agents**
Edit `agents/registry.json` to define your agent endpoints and capabilities.

### **3. Start Server**
```bash
# Simple start
python start_mcp_server.py

# Development mode with auto-reload
python start_mcp_server.py --reload --log-level debug

# Production mode
python start_mcp_server.py --host 0.0.0.0 --port 8000 --workers 4
```

### **4. Test Registry**
```bash
python test_mcp_registry.py
```

## 📡 **Usage Examples**

### **Route a Task**
```python
import httpx

task_request = {
    "intent_type": "reminder",
    "payload": {
        "message": "Review quantization results",
        "datetime": "2025-07-30T15:00:00Z"
    },
    "source": "dolphin",
    "request_id": "task_001"
}

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/mcp/route-task",
        json=task_request
    )
    result = response.json()
```

### **Query Agent Capabilities**
```python
# Get all agents with file system capabilities
response = await client.get(
    "http://localhost:8000/api/mcp/agents/capabilities?capability=filesystem"
)
agents = response.json()["agents"]
```

### **Monitor Agent Health**
```python
# Get system status with agent health
response = await client.get("http://localhost:8000/api/mcp/status")
status = response.json()

for agent in status["agents"]:
    print(f"{agent['agent_name']}: {agent['status']}")
```

## 🔄 **Hot-Reload Workflow**

1. **Edit Registry**: Modify `agents/registry.json`
2. **Automatic Detection**: File watcher detects changes
3. **Validation**: New configuration is validated
4. **Hot-Reload**: Agents updated without restart
5. **Health Check**: New agents automatically monitored

## 🧪 **Testing**

The test suite validates:
- Registry loading and validation
- Agent health checking  
- Runtime enable/disable
- Capability queries
- Hot-reload functionality

```bash
python test_mcp_registry.py
```

## 🔮 **Next Steps**

### **1. Dolphin ↔ MCP Integration**
Create `mcp_bridge.py` in Dolphin for:
- Automatic utility task detection
- Structured payload generation
- Response handling and integration

### **2. Frontend Agent Dashboard**
React dashboard for:
- Real-time agent status monitoring
- Manual task dispatch testing
- Registry configuration management

### **3. Advanced Features**
- Load balancing across agent instances
- Circuit breaker patterns for failed agents
- Message queue integration for async tasks
- Authentication and rate limiting

## 📊 **Monitoring**

The MCP server provides comprehensive monitoring:
- **Request Metrics**: Success/failure rates, response times
- **Agent Health**: Real-time status and availability
- **Registry Status**: Configuration version and load time
- **System Resources**: Uptime and performance metrics

## 🎯 **Benefits**

✅ **Flexibility**: Add new agents without code changes
✅ **Reliability**: Automatic health monitoring and failover
✅ **Scalability**: Priority-based routing and load balancing
✅ **Observability**: Comprehensive metrics and logging
✅ **Developer Experience**: Hot-reload and test automation

The dynamic agent registry transforms the MCP system from a static routing layer into a flexible, self-managing orchestration platform that can adapt to changing requirements and agent availability in real-time! 🚀
