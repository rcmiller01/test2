# Advanced Features Documentation

## 🚀 Overview

This document covers the advanced features that have been implemented and integrated into the main API after Phase 3 completion. These features include:

1. **Emotional TTS System** - Tacotron/FastPitch integration with persona-specific voices
2. **Romantic Memory Engine** - Advanced memory system with relationship feedback loops
3. **Mood-Driven Avatar System** - Visual avatar with expressive animations and gestures

---

## 🎤 Emotional TTS System

### Features
- **Tacotron2/FastPitch Integration**: High-quality speech synthesis with emotional modulation
- **Persona-Specific Voices**: Unique voice characteristics for Mia, Solene, Lyra, and Doc
- **Emotional Mapping**: 10 different emotions with specific voice parameters
- **Real-time Synthesis**: On-demand speech generation with configurable intensity
- **Fallback System**: Graceful degradation when models are unavailable

### Available Emotions
- `love`, `passion`, `tenderness`, `excitement`, `calm`
- `sadness`, `anger`, `fear`, `surprise`, `neutral`

### Available Personas
- `mia` - Warm, affectionate voice
- `solene` - Mysterious, deliberate voice
- `lyra` - Ethereal, expressive voice
- `doc` - Professional, neutral voice

### API Endpoints

#### Synthesize Speech
```http
POST /api/advanced/tts/synthesize
Content-Type: application/json

{
  "text": "I love you so much",
  "persona": "mia",
  "emotion": "love",
  "intensity": 0.8
}
```

#### Get TTS Status
```http
GET /api/advanced/tts/status
```

#### Get Available Emotions/Personas
```http
GET /api/advanced/tts/available_emotions
```

### Usage Examples

```python
import requests

# Synthesize emotional speech
response = requests.post("http://localhost:8000/api/advanced/tts/synthesize", json={
    "text": "You make me so happy",
    "persona": "mia",
    "emotion": "love",
    "intensity": 0.9
})

if response.json()["success"]:
    audio_data = response.json()["audio_data"]
    # Decode base64 and save/play audio
    import base64
    audio_bytes = base64.b64decode(audio_data)
    with open("emotional_speech.wav", "wb") as f:
        f.write(audio_bytes)
```

```javascript
// Frontend integration
async function synthesizeSpeech(text, persona, emotion, intensity) {
    const response = await fetch('/api/advanced/tts/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: text,
            persona: persona,
            emotion: emotion,
            intensity: intensity
        })
    });
    
    const result = await response.json();
    if (result.success) {
        // Convert base64 to audio and play
        const audioBlob = base64ToBlob(result.audio_data, 'audio/wav');
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
    }
}
```

---

## 🧠 Romantic Memory Engine

### Features
- **Memory Types**: 8 different memory categories with specific decay rates
- **Pattern Detection**: Automatic detection of relationship patterns and trends
- **Emotional Weighting**: Memories weighted by emotional intensity and relationship impact
- **Relationship Insights**: AI-powered analysis of relationship health and growth
- **Feedback Loops**: Continuous learning from relationship interactions

### Memory Types
- `emotional_moment` - Significant emotional experiences
- `relationship_milestone` - Important relationship events
- `intimate_interaction` - Close personal moments
- `conversation_highlight` - Meaningful conversations
- `shared_activity` - Activities done together
- `conflict_resolution` - Resolved disagreements
- `growth_moment` - Personal or relationship growth
- `romantic_gesture` - Romantic actions and gestures

### API Endpoints

#### Store Memory
```http
POST /api/advanced/memory/store
Content-Type: application/json

{
  "memory_type": "emotional_moment",
  "title": "First I love you",
  "description": "The first time we said I love you to each other",
  "emotional_intensity": 0.9,
  "emotions": ["love", "excitement", "nervousness"],
  "personas_involved": ["mia"],
  "relationship_impact": 0.8,
  "tags": ["milestone", "first"]
}
```

#### Recall Memories
```http
GET /api/advanced/memory/recall?emotion=love&persona=mia&limit=5
```

#### Get Relationship Insights
```http
GET /api/advanced/memory/insights
```

#### Get Memory Summary
```http
GET /api/advanced/memory/summary
```

### Usage Examples

```python
import requests

# Store a romantic memory
response = requests.post("http://localhost:8000/api/advanced/memory/store", json={
    "memory_type": "romantic_gesture",
    "title": "Surprise dinner",
    "description": "Mia prepared a surprise romantic dinner",
    "emotional_intensity": 0.8,
    "emotions": ["surprise", "love", "appreciation"],
    "personas_involved": ["mia"],
    "relationship_impact": 0.7,
    "tags": ["surprise", "dinner", "romantic"]
})

# Recall memories about love
response = requests.get("http://localhost:8000/api/advanced/memory/recall", params={
    "emotion": "love",
    "limit": 10
})

memories = response.json()["memories"]
for memory in memories:
    print(f"{memory['title']}: {memory['description']}")

# Get relationship insights
response = requests.get("http://localhost:8000/api/advanced/memory/insights")
insights = response.json()["insights"]
print(f"Relationship health: {insights['health_analysis']['health_status']}")
```

```javascript
// Frontend integration
async function storeMemory(memoryData) {
    const response = await fetch('/api/advanced/memory/store', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(memoryData)
    });
    return response.json();
}

async function getRelationshipInsights() {
    const response = await fetch('/api/advanced/memory/insights');
    return response.json();
}
```

---

## 👤 Mood-Driven Avatar System

### Features
- **18 Expressions**: Comprehensive emotional expressions including romantic emotions
- **16 Gestures**: Interactive gestures for romantic interactions
- **Real-time Animation**: Smooth transitions between expressions and gestures
- **Customization**: Eye color, hair style, clothing, background, and lighting
- **Emotional Mapping**: Automatic expression changes based on detected emotions

### Available Expressions
- Basic: `happy`, `sad`, `angry`, `surprised`, `fearful`, `disgusted`, `neutral`
- Romantic: `love`, `passion`, `tenderness`, `longing`, `security`, `excitement`
- Additional: `calm`, `playful`, `seductive`, `vulnerable`, `confident`

### Available Gestures
- Romantic: `blow_kiss`, `heart_hands`, `hug`, `touch_heart`, `embrace`
- Interactive: `wave`, `wink`, `smile`, `tilt_head`, `reach_out`
- Intimate: `dance`, `stroke_hair`, `hold_hands`, `kiss`, `gaze`, `whisper`

### API Endpoints

#### Update Avatar Mood
```http
POST /api/advanced/avatar/mood
Content-Type: application/json

{
  "emotion": "love",
  "intensity": 0.8,
  "context": {
    "romantic_context": true,
    "time_of_day": "evening"
  }
}
```

#### Trigger Gesture
```http
POST /api/advanced/avatar/gesture/blow_kiss?intensity=0.7
```

#### Get Avatar State
```http
GET /api/advanced/avatar/state
```

#### Customize Avatar
```http
POST /api/advanced/avatar/customize
Content-Type: application/json

{
  "eye_color": "#4A90E2",
  "hair_style": "wavy",
  "clothing": "romantic_dress",
  "background": "romantic_garden",
  "lighting": "warm"
}
```

#### Get Customization Options
```http
GET /api/advanced/avatar/customization_options
```

### Usage Examples

```python
import requests

# Update avatar mood
response = requests.post("http://localhost:8000/api/advanced/avatar/mood", json={
    "emotion": "passion",
    "intensity": 0.9,
    "context": {"romantic_context": True}
})

# Trigger romantic gesture
response = requests.post("http://localhost:8000/api/advanced/avatar/gesture/blow_kiss", params={
    "intensity": 0.8
})

# Get current avatar state
response = requests.get("http://localhost:8000/api/advanced/avatar/state")
avatar_state = response.json()["state"]
print(f"Current expression: {avatar_state['expression']}")

# Customize avatar
response = requests.post("http://localhost:8000/api/advanced/avatar/customize", json={
    "eye_color": "#8B4513",
    "hair_style": "long_curly",
    "clothing": "romantic_evening",
    "background": "starlit_sky",
    "lighting": "romantic"
})
```

```javascript
// Frontend integration
async function updateAvatarMood(emotion, intensity, context = {}) {
    const response = await fetch('/api/advanced/avatar/mood', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            emotion: emotion,
            intensity: intensity,
            context: context
        })
    });
    return response.json();
}

async function triggerAvatarGesture(gesture, intensity = 0.5) {
    const response = await fetch(`/api/advanced/avatar/gesture/${gesture}?intensity=${intensity}`, {
        method: 'POST'
    });
    return response.json();
}

async function getAvatarState() {
    const response = await fetch('/api/advanced/avatar/state');
    return response.json();
}
```

---

## 🔗 Integrated Features

### Combined Romantic Experience
Create immersive experiences that combine all advanced features:

```http
POST /api/advanced/integrated/romantic_experience?text=I love you&emotion=love&intensity=0.9&include_tts=true&include_avatar=true&include_memory=true
```

### Get Integrated Status
```http
GET /api/advanced/integrated/status
```

### Health Check
```http
GET /api/advanced/health
```

### Usage Examples

```python
import requests

# Create integrated romantic experience
response = requests.post("http://localhost:8000/api/advanced/integrated/romantic_experience", params={
    "text": "You are the most beautiful person I've ever known",
    "emotion": "love",
    "intensity": 0.9,
    "include_tts": True,
    "include_avatar": True,
    "include_memory": True
})

results = response.json()["results"]

# Play synthesized speech
if results["tts"]["success"]:
    audio_data = base64.b64decode(results["tts"]["audio_data"])
    # Save and play audio

# Update avatar display
if results["avatar"]["success"]:
    avatar_state = results["avatar"]["state"]
    # Update UI with new avatar state

# Memory was automatically stored
if results["memory"]["success"]:
    memory_id = results["memory"]["memory_id"]
    print(f"Memory stored with ID: {memory_id}")
```

```javascript
// Frontend integration
async function createRomanticExperience(text, emotion, intensity) {
    const response = await fetch('/api/advanced/integrated/romantic_experience', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: text,
            emotion: emotion,
            intensity: intensity,
            include_tts: true,
            include_avatar: true,
            include_memory: true
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        const results = result.results;
        
        // Handle TTS
        if (results.tts.success) {
            playAudio(results.tts.audio_data);
        }
        
        // Handle avatar
        if (results.avatar.success) {
            updateAvatarDisplay(results.avatar.state);
        }
        
        // Handle memory
        if (results.memory.success) {
            console.log(`Memory stored: ${results.memory.memory_id}`);
        }
    }
}
```

---

## 🛠️ Integration Guide

### Frontend Integration

#### 1. Emotional TTS Integration
```javascript
class EmotionalTTSManager {
    constructor() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    async synthesizeSpeech(text, persona, emotion, intensity) {
        const response = await fetch('/api/advanced/tts/synthesize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                persona: persona,
                emotion: emotion,
                intensity: intensity
            })
        });
        
        const result = await response.json();
        if (result.success) {
            await this.playAudio(result.audio_data);
        }
    }
    
    async playAudio(base64Audio) {
        const audioData = atob(base64Audio);
        const arrayBuffer = new ArrayBuffer(audioData.length);
        const view = new Uint8Array(arrayBuffer);
        for (let i = 0; i < audioData.length; i++) {
            view[i] = audioData.charCodeAt(i);
        }
        
        const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
        const source = this.audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(this.audioContext.destination);
        source.start(0);
    }
}
```

#### 2. Avatar Integration
```javascript
class AvatarManager {
    constructor() {
        this.currentState = null;
        this.updateInterval = null;
    }
    
    async updateMood(emotion, intensity, context = {}) {
        const response = await fetch('/api/advanced/avatar/mood', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                emotion: emotion,
                intensity: intensity,
                context: context
            })
        });
        
        const result = await response.json();
        if (result.success) {
            await this.updateDisplay();
        }
    }
    
    async triggerGesture(gesture, intensity = 0.5) {
        const response = await fetch(`/api/advanced/avatar/gesture/${gesture}?intensity=${intensity}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        if (result.success) {
            await this.updateDisplay();
        }
    }
    
    async updateDisplay() {
        const response = await fetch('/api/advanced/avatar/state');
        const result = await response.json();
        
        if (result.success) {
            this.currentState = result.state;
            this.renderAvatar();
        }
    }
    
    renderAvatar() {
        // Update UI elements based on avatar state
        const state = this.currentState;
        
        // Update expression
        document.getElementById('avatar-expression').className = `expression-${state.expression}`;
        
        // Update gesture animation
        if (state.gesture) {
            document.getElementById('avatar-gesture').className = `gesture-${state.gesture}`;
        }
        
        // Update visual elements
        document.getElementById('avatar-eyes').style.color = state.eye_color;
        document.getElementById('avatar-background').className = `bg-${state.background}`;
        document.getElementById('avatar-lighting').className = `lighting-${state.lighting}`;
    }
    
    startAutoUpdate() {
        this.updateInterval = setInterval(() => {
            this.updateDisplay();
        }, 1000); // Update every second
    }
    
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}
```

#### 3. Memory Integration
```javascript
class MemoryManager {
    async storeMemory(memoryData) {
        const response = await fetch('/api/advanced/memory/store', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(memoryData)
        });
        
        return response.json();
    }
    
    async recallMemories(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(`/api/advanced/memory/recall?${params}`);
        return response.json();
    }
    
    async getInsights() {
        const response = await fetch('/api/advanced/memory/insights');
        return response.json();
    }
    
    async displayMemories(emotion = null, limit = 10) {
        const filters = { limit: limit };
        if (emotion) filters.emotion = emotion;
        
        const result = await this.recallMemories(filters);
        
        if (result.success) {
            this.renderMemories(result.memories);
        }
    }
    
    renderMemories(memories) {
        const container = document.getElementById('memories-container');
        container.innerHTML = '';
        
        memories.forEach(memory => {
            const memoryElement = document.createElement('div');
            memoryElement.className = 'memory-item';
            memoryElement.innerHTML = `
                <h3>${memory.title}</h3>
                <p>${memory.description}</p>
                <div class="memory-meta">
                    <span class="emotion">${memory.emotions.join(', ')}</span>
                    <span class="intensity">${memory.emotional_intensity}</span>
                    <span class="date">${new Date(memory.timestamp).toLocaleDateString()}</span>
                </div>
            `;
            container.appendChild(memoryElement);
        });
    }
}
```

#### 4. Integrated Experience Manager
```javascript
class IntegratedExperienceManager {
    constructor() {
        this.ttsManager = new EmotionalTTSManager();
        this.avatarManager = new AvatarManager();
        this.memoryManager = new MemoryManager();
    }
    
    async createRomanticExperience(text, emotion, intensity) {
        const response = await fetch('/api/advanced/integrated/romantic_experience', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                emotion: emotion,
                intensity: intensity,
                include_tts: true,
                include_avatar: true,
                include_memory: true
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            const results = result.results;
            
            // Handle TTS
            if (results.tts.success) {
                await this.ttsManager.playAudio(results.tts.audio_data);
            }
            
            // Handle avatar
            if (results.avatar.success) {
                this.avatarManager.currentState = results.avatar.state;
                this.avatarManager.renderAvatar();
            }
            
            // Handle memory
            if (results.memory.success) {
                console.log(`Memory stored: ${results.memory.memory_id}`);
            }
        }
        
        return result;
    }
    
    async getSystemStatus() {
        const response = await fetch('/api/advanced/integrated/status');
        return response.json();
    }
}

// Usage
const experienceManager = new IntegratedExperienceManager();

// Create a romantic moment
experienceManager.createRomanticExperience(
    "I love you more than words can express",
    "love",
    0.9
);
```

---

## 🧪 Testing

### Test Emotional TTS
```python
import requests

# Test TTS synthesis
response = requests.post("http://localhost:8000/api/advanced/tts/synthesize", json={
    "text": "Hello, I love you",
    "persona": "mia",
    "emotion": "love",
    "intensity": 0.8
})
assert response.status_code == 200
assert response.json()["success"] == True

# Test TTS status
response = requests.get("http://localhost:8000/api/advanced/tts/status")
assert response.status_code == 200
```

### Test Memory Engine
```python
# Test memory storage
response = requests.post("http://localhost:8000/api/advanced/memory/store", json={
    "memory_type": "emotional_moment",
    "title": "Test memory",
    "description": "This is a test memory",
    "emotional_intensity": 0.7,
    "emotions": ["love"],
    "personas_involved": ["mia"]
})
assert response.status_code == 200
assert response.json()["success"] == True

# Test memory recall
response = requests.get("http://localhost:8000/api/advanced/memory/recall", params={
    "emotion": "love",
    "limit": 5
})
assert response.status_code == 200
```

### Test Avatar System
```python
# Test avatar mood update
response = requests.post("http://localhost:8000/api/advanced/avatar/mood", json={
    "emotion": "love",
    "intensity": 0.8
})
assert response.status_code == 200
assert response.json()["success"] == True

# Test avatar gesture
response = requests.post("http://localhost:8000/api/advanced/avatar/gesture/blow_kiss", params={
    "intensity": 0.7
})
assert response.status_code == 200
```

### Test Integrated Features
```python
# Test integrated experience
response = requests.post("http://localhost:8000/api/advanced/integrated/romantic_experience", params={
    "text": "I love you",
    "emotion": "love",
    "intensity": 0.8
})
assert response.status_code == 200
assert response.json()["success"] == True

# Test health check
response = requests.get("http://localhost:8000/api/advanced/health")
assert response.status_code == 200
assert response.json()["status"] == "healthy"
```

---

## 🚀 Getting Started

1. **Start the Backend**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Test Advanced Features**
   ```bash
   # Test health check
   curl http://localhost:8000/api/advanced/health
   
   # Test TTS
   curl -X POST http://localhost:8000/api/advanced/tts/synthesize \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello", "persona": "mia", "emotion": "love"}'
   
   # Test avatar
   curl -X POST http://localhost:8000/api/advanced/avatar/mood \
     -H "Content-Type: application/json" \
     -d '{"emotion": "love", "intensity": 0.8}'
   ```

3. **Access API Documentation**
   - Open http://localhost:8000/docs in your browser
   - Navigate to the "Advanced Features" section
   - Test endpoints directly from the interactive documentation

---

## 📊 Performance Considerations

- **TTS Synthesis**: Models are loaded once and cached for performance
- **Memory Engine**: Efficient pattern detection with configurable time windows
- **Avatar System**: Smooth animations with configurable update intervals
- **Integrated Features**: Parallel processing for optimal performance

---

## 🔒 Security & Privacy

- All audio synthesis is performed locally
- Memory data is stored locally with no external transmission
- Avatar state is maintained in memory only
- No personal data is collected or transmitted

---

## 🎯 Next Steps

1. **Frontend UI Development**: Create comprehensive UI components for all advanced features
2. **Mobile Integration**: Optimize for mobile devices with touch gestures and haptic feedback
3. **Real-time Updates**: Implement WebSocket connections for real-time avatar and memory updates
4. **Advanced Customization**: Add more avatar customization options and voice parameters
5. **Analytics Dashboard**: Create relationship analytics and insights visualization

---

## 📞 Support

For questions or issues with advanced features:
- Check the API documentation at http://localhost:8000/docs
- Review the health check endpoint: `GET /api/advanced/health`
- Test individual features using the provided examples
- Monitor system logs for detailed error information 