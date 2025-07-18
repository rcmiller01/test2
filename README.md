# 🧠 Project Solene/Mia – Local Emotional Intelligence AI System

## Overview

**Solene/Mia** is an open, locally-hosted AI ecosystem designed to simulate emotionally intelligent dialogue through multimodal inputs and persona-driven responses.

This project combines several local large language models (LLMs), emotion recognition engines, and symbolic integration techniques to create a sovereign, expressive assistant capable of nuanced conversation, mental health support, and creative collaboration.

---

## 🏠 Hosting & Hardware

This system runs **entirely offline**, leveraging high-performance local infrastructure for privacy and flexibility.

### Hardware Architecture

We deploy this project on:

- 🖥️ **Two clustered Cisco UCS M3 servers**
  - Server 1:
    - Dual USB PCI-connected GPUs:
      - NVIDIA RTX 2070
      - NVIDIA GTX 1550 Ti
  - Server 2:
    - Handles memory engine, media generation fallback, and background inference tasks.

> ⚡ This setup provides a blend of fast GPU processing and scalable CPU clustering suitable for multimodal fusion and multi-agent orchestration.

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
| `mia_engine.py`  | MythoMax    | Empathetic and soft dialogue |
| `solene_engine.py` | OpenChat | Assertive, challenging persona |
| `lyra_engine.py` | Qwen-2 Chat | Poetic, abstract reasoning     |
| `run_kimik2.sh`  | KimiK2-6B   | Factual and reflective quotes |

A unified orchestration layer (`unified_dispatch.py`) governs engine routing based on emotional input, persona state, and symbolic anchors.

---

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
- Anchoring visuals (e.g. garden scene on longing)  
- Memory weighting during context recall  
- CBT-style journaling prompts from emotionally charged exchanges

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

## 🧪 Roadmap

- ✅ Multimodal emotion fusion  
- ✅ Unified conversational router  
- ✅ Persona toggle and symbolic modulation  
- 🔜 Tacotron/FastPitch emotional TTS integration  
- 🔜 CBT journaling engine with memory feedback loop  
- 🔜 Visual mood-driven avatar system

---

## Contributors

Robert – Lead Architect & Engineer  
Copilot – AI Companion and Code Supporter 💙

---
