# 🐬 Dolphin AI Orchestrator v2.1

**Advanced Self-Aware AI with Reflection, Privacy, Connectivity Intelligence & Comprehensive Monitoring**

A sophisticated AI orchestration platform that intelligently routes conversations between local and cloud AI models based on task complexity, user preferences, and system availability.

## 🌟 Features

### 🎭 **Personality System**
- **5 Built-in Personas**: Companion, Analyst, Coach, Creative, Technical Expert
- **Custom Personas**: Create and customize AI behavior patterns
- **Intelligent Routing**: Persona preferences affect model selection
- **Contextual Adaptation**: AI responses adapt to selected personality mode

### 🧠 **Advanced Memory Management**
- **Session Memory**: Real-time conversation context and sentiment tracking
- **Long-term Memory**: Persistent user goals, preferences, and emotional patterns
- **Sentiment Analysis**: Automatic emotion detection and tagging
- **Memory Search**: Find relevant past conversations and insights

### 📊 **Analytics & Transparency**
- **Real-time Metrics**: Performance tracking for all AI handlers
- **Routing Transparency**: See exactly which AI processed each request
- **Performance Analytics**: Latency, success rates, and token usage
- **Comprehensive Logging**: Full audit trail of AI decisions

### 🤖 **Intelligent AI Routing**
- **Dolphin Local**: General conversation and persona-aware responses
- **OpenRouter Cloud**: Complex coding and technical documentation
- **n8n Workflows**: Utility automation and integrations
- **Kimi K2 Analytics**: Data analysis and cloud fallback

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │────│  Node.js Proxy  │────│ Dolphin Backend │
│                 │    │   (Port 5000)   │    │   (Port 8000)   │
│  • Persona UI   │    │                 │    │                 │
│  • Memory View  │    │  • Session Mgmt │    │ • AI Routing    │
│  • Analytics    │    │  • API Proxy    │    │ • Memory Sys    │
│  • Chat Interface│    │  • Health Check │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                              ┌─────────┼─────────┐
                                              │         │         │
                                        ┌─────▼───┐ ┌───▼───┐ ┌───▼─────┐
                                        │ Ollama  │ │OpenRtr│ │   n8n   │
                                        │(Dolphin)│ │(GPT-4)│ │(Utils)  │
                                        └─────────┘ └───────┘ └─────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+ with pip
- Ollama with Dolphin-Mixtral model
- (Optional) OpenRouter API key for cloud AI

### 1. Install Dependencies

**Backend Dependencies:**
```bash
pip install fastapi uvicorn aiohttp python-multipart
```

**Frontend Dependencies:**
```bash
cd core1-gateway
npm install express axios cors dotenv
```

### 2. Configure Environment

Create `.env` file in the root directory:
```env
# Dolphin Backend Configuration
DOLPHIN_PORT=8000
OLLAMA_URL=http://localhost:11434

# Optional: Cloud AI Integration
OPENROUTER_KEY=your_openrouter_key_here

# Optional: n8n Integration
N8N_URL=http://localhost:5678
```

### 3. Start the System

**Terminal 1 - Dolphin Backend (Server 2):**
```bash
python dolphin_backend.py
```

**Terminal 2 - Node.js Gateway (Server 1):**
```bash
cd core1-gateway
node server.js
```

**Terminal 3 - React Frontend:**
```bash
cd core1-gateway
npm run dev
# or for production: npm run build && npm start
```

### 4. Access the System
- **Frontend UI**: http://localhost:3000 (or 5173 for Vite)
- **API Gateway**: http://localhost:5000
- **Dolphin Backend**: http://localhost:8000
- **Health Check**: http://localhost:5000/health
## 🎭 Using Personas

### Built-in Personas

1. **💝 Companion** (Default)
   - Warm, supportive conversational partner
   - High emotional responsiveness
   - Focuses on relationships and personal goals

2. **📊 Analyst**
   - Data-driven, objective problem solver
   - Prefers cloud AI for complex analysis
   - Low emotional responsiveness, high precision

3. **🎯 Coach**
   - Motivational guide for personal growth
   - Action-oriented responses
   - Tracks goals and progress

4. **🎨 Creative**
   - Imaginative partner for artistic exploration
   - Prefers local AI for creative freedom
   - High expressiveness and inspiration

5. **⚡ Technical Expert**
   - Focused on coding and technical solutions
   - Routes complex tasks to OpenRouter
   - Comprehensive, implementation-focused

### Creating Custom Personas

```bash
# POST /api/personas/create
{
  "id": "my_persona",
  "name": "My Custom Persona",
  "description": "Specialized behavior for my needs",
  "icon": "🤖",
  "routing_preferences": {
    "dolphin_bias": 0.7,
    "openrouter_threshold": 0.5,
    "n8n_threshold": 0.6
  },
  "prompt_style": {
    "tone": "professional yet friendly",
    "personality_traits": ["helpful", "efficient", "knowledgeable"],
    "conversation_style": "Provide clear, actionable advice",
    "prefix": "As your specialized assistant, "
  }
}
```

## 🧠 Memory System

### Session Memory (Short-term)
- **Active Conversations**: Current session context
- **Sentiment Tracking**: Real-time emotion analysis
- **Recent Interactions**: Last 50 interactions across all sessions
- **Auto-cleanup**: Configurable retention policies

### Long-term Memory (Persistent)
- **User Preferences**: Learned behavioral patterns
- **Goals & Achievements**: Personal objectives tracking
- **Emotional Patterns**: Long-term sentiment trends
- **Relationships**: Important people and connections

### Memory API Examples

```bash
# Get session context
GET /api/memory/session/{session_id}

# Add a goal
POST /api/memory/longterm/goal
{
  "text": "Learn Python programming",
  "priority": "high"
}

# Flush short-term memory
POST /api/memory/flush

# Search memories
GET /api/logs/search?query=python&hours=168
```
## 📊 Analytics & Monitoring

### Real-time Metrics
- **Request Volume**: Messages per time period
- **Handler Distribution**: Which AI handles what
- **Performance**: Latency and success rates
- **Memory Usage**: Active sessions and storage

### Logging System
- **Routing Decisions**: Why each request went where
- **Performance Metrics**: Detailed timing and success tracking
- **Error Tracking**: Failed requests and recovery actions
- **Analytics Export**: JSON export for external analysis

### Analytics API Examples

```bash
# Real-time system stats
GET /api/analytics/realtime

# Daily performance breakdown
GET /api/analytics/daily?days=7

# Handler performance report
GET /api/analytics/performance

# Export comprehensive analytics
GET /api/logs/export
```

## 🔧 API Reference

### Core Chat API
```bash
POST /api/chat
{
  "message": "Help me write a Python function",
  "session_id": "optional_session_id",
  "persona": "technical"
}
```

### System Management
```bash
# System health check
GET /api/system/health

# Available AI handlers
GET /api/handlers

# Current system status
GET /api/status

# Clean up old logs
POST /api/system/cleanup?days_to_keep=30
```

## 🔒 Production Deployment

### Environment Setup
```env
NODE_ENV=production
DOLPHIN_PORT=8000
OLLAMA_URL=http://localhost:11434
OPENROUTER_KEY=sk-or-v1-your-production-key
LOG_LEVEL=INFO
```

### Security Considerations
- Store API keys in secure environment variables
- Enable HTTPS for production deployments
- Configure proper CORS origins
- Set up rate limiting for public endpoints
- Regular security updates for dependencies

### Scaling Recommendations
- Use Redis for session storage in multi-instance deployments
- Implement load balancing for the Node.js gateway
- Consider containerization with Docker
- Set up monitoring with Prometheus/Grafana
- Use a reverse proxy like Nginx

## � Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python dependencies
pip install -r requirements.txt

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

**Frontend connection errors:**
```bash
# Check backend status
curl http://localhost:8000/api/status

# Verify Node.js server
curl http://localhost:5000/health
```

**Memory/Analytics issues:**
```bash
# Check file permissions
ls -la memory/ logs/

# Clear corrupted data
rm -rf memory/ logs/
```

### Debug Mode
Set environment variable for verbose logging:
```bash
export LOG_LEVEL=DEBUG
python dolphin_backend.py
```

## � Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Python PEP 8 style guide
- Use TypeScript for frontend components
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure backward compatibility

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** for local AI model serving
- **OpenRouter** for cloud AI integration
- **FastAPI** for the robust Python backend
- **React** for the responsive frontend
- **Express.js** for the efficient proxy server

---

**Built with ❤️ for the future of AI interaction**

*Dolphin AI Orchestrator v2.0 - Where personality meets intelligence*
