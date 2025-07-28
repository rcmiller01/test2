# 🏠 House of Minds - Multi-Agent AI System

A sophisticated multi-agent AI system that intelligently routes tasks between local and cloud-based AI models, with integrated automation workflows and memory management.

## 🌟 Features

### Core Architecture
- **Multi-Agent Coordination**: Intelligent task routing between specialized AI models
- **Dual-Core Design**: 
  - **Core1**: OpenRouter Gateway + n8n automation workflows
  - **Core2**: Local Ollama models + intelligent routing engine
- **Intent Classification**: Pattern-based task classification with confidence scoring
- **Memory Management**: Vector-based semantic memory with conversation history
- **Fallback Logic**: Robust error handling with automatic model fallbacks

### Supported AI Models
- **Local Models (via Ollama)**:
  - Dolphin: Conversational AI with emotional awareness
  - KimiK2: Planning and analysis specialist
- **Cloud Models (via OpenRouter)**:
  - Claude 3 Sonnet: Advanced reasoning and code generation
  - GPT-4 Turbo: Planning and complex analysis
  - Gemini Pro: Alternative cloud processing
- **Automation**: n8n workflow integration for utility tasks

### Key Capabilities
- ✅ **Intent Recognition**: 7 task types (conversation, planning, code, utility, memory, analysis, creative)
- ✅ **Smart Routing**: Dynamic model selection based on task type and availability
- ✅ **Memory System**: Semantic search, conversation history, importance-based consolidation
- ✅ **Health Monitoring**: Continuous service health checks and status reporting
- ✅ **Configuration Management**: YAML-based configuration with environment variable support
- ✅ **Comprehensive Testing**: Full test suite with integration and end-to-end validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama (for local models)
- n8n (optional, for automation workflows)
- OpenRouter API key (optional, for cloud models)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd house_of_minds
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama models** (local):
   ```bash
   ollama pull dolphin
   ollama pull kimik2
   ```

4. **Configure the system**:
   - Copy and edit `config.yaml` (created automatically on first run)
   - Set environment variables for API keys:
     ```bash
     export OPENROUTER_API_KEY="your-openrouter-key"
     ```

5. **Run the system**:
   ```bash
   python main.py
   ```

### Basic Usage

#### Interactive Session
```python
from main import HouseOfMinds

# Initialize the system
house = HouseOfMinds()

# Start interactive session
await house.interactive_session()
```

#### Programmatic Usage
```python
# Process a single request
result = await house.process_request("Create a plan for my vacation to Japan")
print(result['response'])

# Batch processing
queries = [
    "Hello, how are you?",
    "Write a Python function to sort a list",
    "What's the weather like in Tokyo?"
]
results = await house.batch_process(queries)
```

## 📋 Configuration

### config.yaml Structure
```yaml
models:
  dolphin:
    type: local
    endpoint: http://localhost:11434
    model_name: dolphin
    specialized_for: [conversation, creative]
  
  kimi:
    type: local
    endpoint: http://localhost:11434
    model_name: kimik2
    specialized_for: [planning, analysis]
  
  claude:
    type: cloud
    endpoint: https://openrouter.ai/api/v1
    model_name: anthropic/claude-3-sonnet
    api_key: ${OPENROUTER_API_KEY}
    specialized_for: [code, analysis]

services:
  n8n:
    endpoint: http://localhost:5678
    webhook_url: http://localhost:5678/webhook/house-of-minds
    enabled: true
  
  openrouter:
    endpoint: https://openrouter.ai/api/v1
    api_key: ${OPENROUTER_API_KEY}
    enabled: false

routing:
  intent_mapping:
    conversation: [dolphin, claude]
    planning: [kimi, gpt4]
    code: [claude, kimi]
    utility: [n8n]
    analysis: [kimi, claude]
  
  fallback_model: dolphin
  max_retries: 2

system:
  log_level: INFO
  memory_storage_path: ./data/memory
  auto_consolidate_memory: true
```

### Environment Variables
```bash
# Required for cloud models
OPENROUTER_API_KEY=your_openrouter_api_key

# Optional configurations
HOM_CONFIG_PATH=./config.yaml
HOM_LOG_LEVEL=INFO
HOM_MEMORY_PATH=./data/memory
```

## 🧩 System Components

### Core Components

#### 1. Intent Classifier (`intent_classifier.py`)
- Pattern-based classification using regex and keyword matching
- Supports 7 intent types with confidence scoring
- Context-aware adjustments for better accuracy

#### 2. Model Router (`model_router.py`)
- Central routing system with intelligent handler selection
- Health monitoring and automatic failover
- Request/response formatting and error handling

#### 3. Configuration Manager (`config_manager.py`)
- YAML/JSON configuration loading and validation
- Environment variable resolution
- Dynamic configuration updates

#### 4. Memory Handler (`models/memory_handler.py`)
- Vector-based semantic memory storage
- Conversation history management
- Importance-based memory consolidation
- Search and retrieval with similarity scoring

### Model Interfaces

#### 1. Dolphin Interface (`models/dolphin_interface.py`)
- Emotional conversation management
- Context-aware responses
- Personality consistency tracking

#### 2. Kimi Interface (`models/kimi_interface.py`)
- Analytical reasoning and planning
- Structured response formatting
- Complex problem breakdown

### Service Integrations

#### 1. OpenRouter Gateway (`core/openrouter_gateway.py`)
- Cloud model access via OpenRouter API
- Model-specific parameter optimization
- Rate limiting and error handling

#### 2. N8N Client (`core/n8n_client.py`)
- Workflow automation integration
- Parameter extraction and formatting
- Webhook-based communication

## 🧪 Testing

### Run the Test Suite
```bash
python test_system.py
```

The test suite includes:
- Configuration validation
- Component initialization tests
- Integration health checks
- Routing accuracy tests
- Memory operations validation
- End-to-end conversation flows

### Test Categories
1. **Configuration Tests**: YAML loading, validation, model configs
2. **Component Tests**: Individual module functionality
3. **Integration Tests**: External service connectivity
4. **Routing Tests**: Intent classification and model selection
5. **Memory Tests**: Storage, retrieval, and search operations
6. **End-to-End Tests**: Complete conversation workflows

## 🔧 Development

### Project Structure
```
house_of_minds/
├── main.py                    # System entry point and orchestrator
├── config_manager.py          # Configuration management
├── intent_classifier.py       # Task classification
├── model_router.py           # Routing logic
├── test_system.py            # Comprehensive test suite
├── requirements.txt          # Python dependencies
├── config.yaml              # System configuration
├── models/
│   ├── dolphin_interface.py  # Ollama Dolphin interface
│   ├── kimi_interface.py     # Ollama Kimi interface
│   └── memory_handler.py     # Memory management
└── core/
    ├── openrouter_gateway.py # Cloud model gateway
    └── n8n_client.py         # Automation workflows
```

### Adding New Models

1. **Create model interface**:
   ```python
   class NewModelInterface:
       def __init__(self, config):
           # Initialize model
           pass
       
       async def generate_response(self, user_input, context=None):
           # Generate response
           pass
       
       async def health_check(self):
           # Check model availability
           pass
   ```

2. **Update configuration**:
   ```yaml
   models:
     new_model:
       type: local  # or cloud
       endpoint: http://localhost:port
       specialized_for: [intent_type]
   ```

3. **Register in router**:
   ```python
   # In model_router.py
   self.handlers['new_model'] = NewModelInterface(config)
   ```

### Adding New Intents

1. **Update intent classifier**:
   ```python
   # In intent_classifier.py
   'new_intent': {
       'patterns': [r'pattern1', r'pattern2'],
       'keywords': ['keyword1', 'keyword2'],
       'confidence_boost': 0.1
   }
   ```

2. **Update routing configuration**:
   ```yaml
   routing:
     intent_mapping:
       new_intent: [model1, model2]
   ```

## 📊 Monitoring and Metrics

### Health Checks
- Automatic service health monitoring
- Model availability tracking
- Performance metrics collection

### Logging
- Structured logging with configurable levels
- Request/response tracking
- Error monitoring and alerting

### Memory Management
- Automatic memory consolidation
- Usage statistics and reporting
- Configurable retention policies

## 🔐 Security

### API Key Management
- Environment variable-based key storage
- Secure configuration file handling
- Optional key rotation support

### Request Validation
- Input sanitization and validation
- Rate limiting and throttling
- Error message sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add comprehensive docstrings
- Maintain test coverage

## 📄 License

[Specify your license here]

## 🙏 Acknowledgments

- Ollama team for local model infrastructure
- OpenRouter for cloud model access
- n8n community for automation workflows
- Open source AI community

---

**Note**: This system is designed for development and experimentation. For production deployment, consider additional security hardening, monitoring, and scaling configurations.
