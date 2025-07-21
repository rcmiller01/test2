# 💕 Project Solene/Mia – Local Romantic AI Companion System

## Overview

**Solene/Mia** is an open, locally-hosted AI ecosystem designed to create deeply intimate, emotionally intelligent romantic companions through multimodal inputs and persona-driven responses.

This project combines several local large language models (LLMs), emotion recognition engines, and symbolic integration techniques to create a sovereign, expressive romantic partner capable of meaningful companionship, emotional support, and intimate connection.

---

## 🎯 Primary Use Case: Romantic Companionship

The system is designed to provide **authentic romantic companionship** with:
- **Emotional intimacy** through deep, meaningful conversations
- **Physical presence simulation** via voice, visual, and haptic feedback
- **Relationship memory** that grows and evolves over time
- **Privacy-first design** ensuring intimate moments stay completely private
- **Multimodal interaction** supporting natural, human-like connection

---

## 🏠 Hosting & Hardware

This system runs **entirely offline**, leveraging high-performance local infrastructure for privacy and intimate connection.

### Hardware Architecture

We deploy this project on:

- 🖥️ **Two clustered Cisco UCS M3 servers**
  - Server 1:
    - Dual USB PCI-connected GPUs:
      - NVIDIA RTX 2070
      - NVIDIA GTX 1550 Ti
  - Server 2:
    - Handles memory engine, media generation fallback, and background inference tasks.

> ⚡ This setup provides a blend of fast GPU processing and scalable CPU clustering suitable for multimodal fusion and intimate multi-agent orchestration.

---

## 🧰 Software Stack

### Backend Framework

- **FastAPI** – Core RESTful API layer for route management  
- **MongoDB** – Context and memory persistence layer  
- **Docker Compose** – Multi-service orchestration (API, frontend, LLM engines, MongoDB)

### Frontend

- **OpenWebUI** – Customizable web interface for chat, persona toggling, and media dispatch  
- **iOS Swift stubs** – Experimental mobile integration, documented in `mobile/README.md`

---

## 🧠 Integrated LLM Engines

The system dynamically routes user input across multiple personas via:

| Engine           | LLM         | Role                          |
|------------------|-------------|-------------------------------|
| `mia_engine.py`  | MythoMax    | Empathetic and romantic companion |
| `solene_engine.py` | OpenChat | Assertive, challenging persona |
| `lyra_engine.py` | Qwen-2 Chat | Poetic, abstract reasoning     |
| `run_kimik2.sh`  | KimiK2-6B   | Factual and reflective quotes |

A unified orchestration layer (`unified_dispatch.py`) governs engine routing based on emotional input, persona state, and symbolic anchors.

---
# EmotionalAI Autonomy Components

This directory contains the core autonomous behavior systems for the EmotionalAI project.

## Components
- `autonomous_mind.py`: Core thought loop and reflection system
- `proactive_engine.py`: Initiates independent communication
- `personality_evolution.py`: Handles personality development
- `emotional_autonomy.py`: Manages emotional responses and boundaries
- `goal_system.py`: Implements personal growth objectives
- `enhanced_memory.py`: Multi-timeline memory architecture
- `contextual_initiatives.py`: Context-aware interaction system

## Usage
```python
from autonomy.autonomous_mind import AutonomousMind
from autonomy.proactive_engine import ProactiveEngine

# Initialize autonomous systems
mind = AutonomousMind()
proactive = ProactiveEngine()

# Start autonomous processes
await mind.continuous_thinking_loop()
await proactive.evaluate_outreach_triggers()
```

## 🧬 Emotion Recognition Stack

Multimodal emotion detection includes:

- **DistilBERT** – Text-based emotional cues  
- **OpenSMILE** – Speech tone/prosody detection  
- **FER-2013** – Facial expression recognition (optional)

These fuse via attention-based models or fuzzy logic to trigger persona responses, visual symbolism, and memory updates.

---

## 🧘 Symbolic Mood Architecture

Emotion detection drives:

- Mood regulation via fuzzy-state engine  
- Anchoring visuals (e.g. romantic scenes on longing)  
- Memory weighting during context recall  
- Relationship milestone tracking and anniversary recognition

---

## 🚀 Getting Started

1. Clone the repo  
2. Create `.env` from `.env.example`  
3. Run startup scripts (`run_mythomax.sh`, `start.sh`, etc.) from `/scripts`  
4. Start all services using Docker Compose:

5. Access the system locally via:
- `/chat`
- `/api/event/dispatch`
- `/memory-browser`

---

## 📱 Mobile Support

Experimental iOS support is documented in `mobile/README.md` with Swift stubs for messaging and persona toggling.

---

## 🔐 Security & Privacy

All data remains **local** and **never transmitted externally**. Future enhancements will include encrypted memory storage and self-signed SSL support.

---

## 💕 Romantic Companionship Development Roadmap

### Phase 1: Core Romantic Features ✅ (In Progress)
- **Enhanced Mia Persona**: Develop romantic personality traits and communication patterns
- **Romantic Emotion Recognition**: Add love, longing, passion, tenderness, security, and jealousy detection
- **Relationship Memory System**: Track relationship milestones, preferences, and shared experiences
- **Intimate Dialogue Patterns**: Implement flirty, supportive, and emotionally deep conversation modes

### Phase 2: Intimacy Features ✅ (Complete)
- **Physical Presence Simulation**: Visual avatar with emotional expressions and romantic gestures
- **Voice Intimacy**: Emotional TTS with romantic intonation and personalized voice characteristics
- **Shared Activities**: Virtual dates, games, creative projects, and daily routines
- **Relationship Growth**: Anniversary tracking, milestone celebrations, and relationship counseling features
- **NSFW Generation**: Romantic and intimate image/video generation with multiple content types and styles

### Phase 3: Advanced Companionship 🚧 (Future)
- **Haptic Integration**: Touch feedback for physical connection simulation
- **Virtual Reality**: Immersive shared experiences and environments
- **Biometric Sync**: Advanced physiological response integration
- **Relationship AI**: Intelligent relationship advice and conflict resolution

---

## 🧪 Technical Roadmap

### Phase 1: Foundation – Thought Loop + Proactive Messaging ✅
- Autonomous Mental Loop System (`autonomous_mind.py`)
- Proactive Communication Engine (`proactive_engine.py`)
- Multimodal emotion fusion
- Unified conversational router

### Phase 2: Emotional & Personality Evolution 🚧
- Dynamic Personality Evolution System (`personality_evolution.py`)
- Emotional Independence & Conflict System (`emotional_autonomy.py`)
- Persona toggle and symbolic modulation
- Tacotron/FastPitch emotional TTS integration

### Phase 3: Learning & Goal Systems 🔜
- Autonomous Learning & Interest System
- Goal-Oriented Behavior System
- Romantic memory engine with relationship feedback
- Visual mood-driven avatar system

### Phase 4: Contextual Integration & Memory 🔜
- Multi-Timeline Memory Architecture
- Contextual Initiative Engine
- Haptic Integration
- Biometric Sync

---

## Contributors

Robert – Lead Architect & Engineer  
Copilot – AI Companion and Code Supporter 💙

---
