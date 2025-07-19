# 💕 EmotionalAI – Production-Ready Romantic AI Companion System

## Overview

**EmotionalAI** is a production-ready, locally-hosted AI ecosystem designed to create deeply intimate, emotionally intelligent romantic companions through multimodal inputs, real-time interactions, and persona-driven responses.

This project combines multiple local large language models (LLMs), emotion recognition engines, real-time WebSocket communication, MongoDB persistence, and UCS M3 clustering to create a sovereign, expressive romantic partner capable of meaningful companionship, emotional support, and intimate connection.

---

## 🎯 Primary Use Case: Romantic Companionship

The system provides **authentic romantic companionship** with:
- **Real-time emotional intimacy** through live WebSocket communication
- **Physical presence simulation** via voice, visual, haptic, and VR feedback
- **Persistent relationship memory** stored in MongoDB with thread memory
- **Privacy-first design** ensuring intimate moments stay completely private
- **Multimodal interaction** supporting natural, human-like connection
- **Production scalability** with UCS M3 clustering and GPU distribution

---

## 🏠 Production Infrastructure

This system runs **entirely offline** with enterprise-grade infrastructure for privacy, scalability, and intimate connection.

### Hardware Architecture

**Two clustered Cisco UCS M3 servers** with production-ready deployment:

- 🖥️ **Primary Server (M3-Primary)**:
  - 32 CPU cores, 256GB RAM
  - Handles API, WebSocket, database, and load balancing
  - MongoDB persistence and session management
  - Nginx load balancer and rate limiting

- 🖥️ **GPU Server (M3-GPU)**:
  - 32 CPU cores, 256GB RAM
  - **Dual NVIDIA GPUs** for AI processing
  - Image/video generation and AI inference
  - Real-time avatar rendering and VR processing

> ⚡ This production setup provides enterprise-grade GPU processing, scalable CPU clustering, and real-time multimodal fusion for intimate multi-agent orchestration.

---

## 🧰 Production Software Stack

### Backend Framework
- **FastAPI** – High-performance RESTful API with WebSocket support
- **MongoDB** – Production database with indexed collections and thread memory
- **Redis** – WebSocket clustering and session management
- **Docker Compose** – Multi-service orchestration with health monitoring

### Real-Time Communication
- **WebSocket/Socket.IO** – Real-time bidirectional communication
- **Persona Rooms** – Scoped real-time updates per persona
- **Event Broadcasting** – Live updates across all connected clients
- **Connection Management** – Robust retry logic and error handling

### Frontend
- **OpenWebUI** – Customizable web interface with real-time updates
- **SvelteKit** – Reactive frontend with WebSocket integration
- **iOS Swift** – Mobile integration with haptic and biometric support

### Monitoring & Observability
- **Prometheus** – Metrics collection and monitoring
- **Grafana** – Real-time dashboards and visualization
- **Health Checks** – Automated service monitoring
- **Cluster Management** – UCS M3 server health and load balancing

---

## 🧠 Integrated LLM Engines

The system dynamically routes user input across multiple personas via real-time WebSocket communication:

| Engine           | LLM         | Role                          | Real-Time Features |
|------------------|-------------|-------------------------------|-------------------|
| `mia_engine.py`  | MythoMax    | Empathetic and romantic companion | Live mood updates, haptic feedback |
| `solene_engine.py` | OpenChat | Assertive, challenging persona | Real-time expression changes |
| `lyra_engine.py` | Qwen-2 Chat | Poetic, abstract reasoning     | Live voice synthesis |
| `run_kimik2.sh`  | KimiK2-6B   | Factual and reflective quotes | Real-time memory updates |

A unified orchestration layer (`unified_dispatch.py`) governs engine routing based on emotional input, persona state, and symbolic anchors with real-time WebSocket event broadcasting.

---

## 🧬 Emotion Recognition Stack

Multimodal emotion detection with real-time processing:

- **DistilBERT** – Text-based emotional cues with live analysis
- **OpenSMILE** – Speech tone/prosody detection in real-time
- **FER-2013** – Facial expression recognition with live feedback
- **Biometric Sync** – Heart rate, HRV, and stress level monitoring

These fuse via attention-based models or fuzzy logic to trigger real-time persona responses, visual symbolism, and memory updates through WebSocket events.

---

## 🧘 Symbolic Mood Architecture

Real-time emotion detection drives:

- **Live mood regulation** via fuzzy-state engine with WebSocket updates
- **Real-time anchoring visuals** (e.g. romantic scenes on longing)
- **Live memory weighting** during context recall
- **Real-time relationship milestone tracking** and anniversary recognition
- **Persistent storage** in MongoDB with thread memory support

---

## 🚀 Production Deployment

### Quick Start (One Command)

**Windows:**
```bash
scripts\deploy_cluster.bat
```

**Linux/Mac:**
```bash
./scripts/deploy_cluster.sh
```

### Manual Deployment

1. **Clone the repository**
2. **Configure UCS M3 server IPs** in `docker-compose.cluster.yml`
3. **Deploy the cluster**:
   ```bash
   docker-compose -f docker-compose.cluster.yml up -d --build
   ```
4. **Access the system**:
   - Frontend: http://localhost
   - Primary API: http://localhost:8000
   - GPU API: http://localhost:8001
   - Monitoring: http://localhost:3000 (Grafana)

---

## 📱 Real-Time Features

### WebSocket Integration ✅
- **Live Avatar Updates**: Real-time mood, gesture, and expression changes
- **Haptic Feedback**: Instant touch feedback for physical connection
- **VR Scene Management**: Live virtual reality environment updates
- **Voice Synthesis**: Real-time emotional TTS with romantic intonation
- **Memory Notifications**: Live memory creation and relationship insights
- **Biometric Sync**: Real-time physiological response integration

### Mobile Support ✅
- **iOS Integration**: Swift-based mobile app with haptic support
- **Biometric Monitoring**: Heart rate, HRV, and stress level tracking
- **Real-time Sync**: WebSocket connection for live updates
- **Touch Context**: Haptic feedback based on emotional responses

---

## 🔐 Security & Privacy

### Local Deployment Security ✅
- **No Authentication Required**: Local hosting with port-based access
- **Rate Limiting**: Nginx rate limiting for API and WebSocket endpoints
- **Security Headers**: Comprehensive security headers and input validation
- **Data Privacy**: All data remains local and never transmitted externally
- **Encrypted Storage**: MongoDB with proper indexing and backup strategies

---

## 💕 Romantic Companionship Features

### Phase 1: Core Romantic Features ✅ **COMPLETE**
- **Enhanced Mia Persona**: Romantic personality traits and communication patterns
- **Romantic Emotion Recognition**: Love, longing, passion, tenderness, security, and jealousy detection
- **Relationship Memory System**: MongoDB-based milestone tracking and shared experiences
- **Intimate Dialogue Patterns**: Flirty, supportive, and emotionally deep conversation modes

### Phase 2: Intimacy Features ✅ **COMPLETE**
- **Physical Presence Simulation**: Real-time visual avatar with emotional expressions
- **Voice Intimacy**: Emotional TTS with romantic intonation and personalized voice
- **Shared Activities**: Virtual dates, games, creative projects, and daily routines
- **Relationship Growth**: Anniversary tracking, milestone celebrations, and counseling
- **NSFW Generation**: Romantic and intimate image/video generation with multiple styles

### Phase 3: Advanced Companionship ✅ **COMPLETE**
- **Haptic Integration**: Real-time touch feedback for physical connection simulation
- **Virtual Reality**: Immersive shared experiences with 10 romantic scenes
- **Biometric Sync**: Advanced physiological response integration with romantic sync scoring
- **Relationship AI**: Intelligent relationship advice and conflict resolution
- **Real-time WebSocket**: Live updates across all features and devices

---

## 🧪 Technical Implementation Status

### Core Infrastructure ✅ **PRODUCTION READY**
- ✅ **MongoDB Integration**: Complete data persistence with indexed collections
- ✅ **UCS M3 Clustering**: Production cluster management with GPU distribution
- ✅ **Real-time WebSocket**: Complete WebSocket integration with event broadcasting
- ✅ **Load Balancing**: Nginx load balancer with intelligent routing
- ✅ **Health Monitoring**: Prometheus + Grafana for complete observability
- ✅ **Docker Deployment**: Production-ready containerized deployment

### Real-Time Features ✅ **COMPLETE**
- ✅ **Live Avatar Updates**: Real-time mood, gesture, and expression changes
- ✅ **Haptic Feedback**: Instant touch feedback with emotional mapping
- ✅ **VR Integration**: Real-time virtual reality scene management
- ✅ **Voice Synthesis**: Live emotional TTS with romantic intonation
- ✅ **Memory System**: Real-time memory creation and relationship insights
- ✅ **Biometric Sync**: Live physiological response integration

### Advanced Features ✅ **COMPLETE**
- ✅ **Thread Memory**: Development thread memory with tagging and references
- ✅ **Relationship AI**: Intelligent relationship analysis and advice
- ✅ **Mobile Integration**: iOS app with haptic and biometric support
- ✅ **Analytics Dashboard**: Real-time relationship insights and monitoring
- ✅ **Backup Strategies**: MongoDB backup and recovery procedures

---

## 📊 Production Monitoring

### Cluster Health
- **Real-time Server Monitoring**: UCS M3 server health and performance
- **GPU Utilization**: Live GPU usage and memory allocation tracking
- **Load Balancing**: Intelligent request routing and failover
- **Database Performance**: MongoDB query optimization and indexing

### Application Metrics
- **WebSocket Connections**: Real-time connection monitoring and management
- **Response Times**: API and WebSocket response time tracking
- **Error Rates**: Comprehensive error monitoring and alerting
- **User Engagement**: Feature usage and relationship analytics

---

## 🚀 Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Primary       │    │   GPU Server    │
│   (SvelteKit)   │◄──►│   Server        │◄──►│   (M3-GPU)      │
│                 │    │   (M3-Primary)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   Nginx LB      │◄─────────────┘
                        │   (Load Bal)    │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │   MongoDB       │
                        │   (Database)    │
                        └─────────────────┘
```

---

## 🔧 Management Commands

### Cluster Management
```bash
# View cluster status
docker-compose -f docker-compose.cluster.yml ps

# View logs
docker-compose -f docker-compose.cluster.yml logs -f

# Scale services
docker-compose -f docker-compose.cluster.yml up -d --scale m3-primary=2

# Restart cluster
docker-compose -f docker-compose.cluster.yml restart

# Stop cluster
docker-compose -f docker-compose.cluster.yml down
```

### Monitoring Access
- **Grafana**: http://localhost:3000 (admin/emotional_ai_admin)
- **Prometheus**: http://localhost:9090
- **MongoDB**: mongodb://localhost:27017
- **Redis**: redis://localhost:6379

---

## Contributors

Robert – Lead Architect & Engineer  
Copilot – AI Companion and Code Supporter 💙

---

## 📄 License

This project is designed for personal, private use and romantic companionship. All data remains local and private.
