# Ambient Presence Sensing System

The Ambient Presence Sensing system provides intelligent, multi-modal presence detection to enable natural contextual interactions with the AI persona. This system combines session tracking, idle detection, and background sensing to create a unified understanding of user presence and availability.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Presence Orchestrator                       │
│              (Unified Intelligence Layer)                   │
└─────────────────┬───────────────┬───────────────┬───────────┘
                  │               │               │
    ┌─────────────▼─────────────┐ │ ┌─────────────▼─────────────┐
    │    Session Presence      │ │ │   Background Sensing      │
    │   (Direct Interaction)   │ │ │   (Ambient Signals)       │
    │                          │ │ │                           │
    │ • Real-time tracking     │ │ │ • System metrics          │
    │ • Engagement levels      │ │ │ • Browser activity        │
    │ • Interaction patterns   │ │ │ • Passive indicators      │
    │ • Focus detection        │ │ │ • Hardware sensors        │
    └──────────────────────────┘ │ └───────────────────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │           Idle Detection            │
              │        (Activity Patterns)         │
              │                                    │
              │ • Smart idle detection             │
              │ • Activity type classification     │
              │ • Break prediction                 │
              │ • Return time estimation           │
              └────────────────────────────────────┘
```

## Core Components

### 1. Session Presence (`session_presence.py`)
**Purpose**: Real-time session monitoring and engagement detection

**Key Features**:
- **Engagement Levels**: High, Moderate, Low, Minimal
- **Presence States**: Active, Focused, Idle, Away, Background
- **Interaction Tracking**: Messages, voice, typing, UI events
- **Focus Detection**: Tab focus, window activity, interaction patterns
- **Metrics**: Interaction rate, focus percentage, engagement scoring

**Usage**:
```python
from backend.modules.presence import session_presence

# Start tracking
await session_presence.start_session_tracking(user_id, session_id)

# Record interactions
await session_presence.record_interaction(session_id, InteractionType.MESSAGE)

# Get status
status = await session_presence.get_presence_status(session_id)
```

### 2. Idle Detection (`idle_detection.py`)
**Purpose**: Smart idle detection with activity pattern analysis

**Key Features**:
- **Idle States**: Active, Short Idle, Medium Idle, Long Idle, Deep Idle
- **Activity Types**: Keyboard, Voice, UI Interaction, Navigation
- **Smart Detection**: Learns user patterns for personalized thresholds
- **Break Prediction**: Predicts break duration and return times
- **Pattern Learning**: Adapts to individual user behavior

**Usage**:
```python
from backend.modules.presence import idle_detector

# Start monitoring
await idle_detector.start_monitoring(user_id)

# Record activity
await idle_detector.record_activity(user_id, ActivityType.KEYBOARD)

# Get predictions
prediction = await idle_detector.predict_break_time(user_id)
```

### 3. Background Sensing (`background_sensing.py`)
**Purpose**: Ambient presence detection through system metrics

**Key Features**:
- **System Metrics**: CPU usage, memory, network activity
- **Browser Signals**: Tab activity, focus events, page interactions
- **Hardware Sensors**: Webcam status, microphone activity
- **Passive Indicators**: Mouse movement, keyboard activity patterns
- **Privacy-Conscious**: Configurable data collection levels

**Usage**:
```python
from backend.modules.presence import background_sensor

# Start sensing
await background_sensor.start_background_sensing(user_id)

# Record browser signals
await background_sensor.record_browser_signal(user_id, "focus", 0.9)

# Get presence signal
signal = await background_sensor.get_presence_signal(user_id)
```

### 4. Presence Orchestrator (`presence_orchestrator.py`)
**Purpose**: Unified intelligence layer combining all detection methods

**Key Features**:
- **Unified States**: Highly Engaged, Actively Present, Passively Present, Briefly Away, Away, Deeply Away
- **Context Detection**: Focused Session, Casual Browsing, Multitasking, Background Mode, Break Time
- **Intelligent Fusion**: Weighted combination of all presence sources
- **Availability Scoring**: Real-time availability and interruption receptivity
- **Prediction**: Return time estimation when user is away

**Unified Presence Data**:
```python
{
    "unified_state": "actively_present",
    "context": "focused_session", 
    "confidence": 0.85,
    "availability_score": 0.78,
    "attention_level": 0.82,
    "interruption_receptivity": 0.65,
    "predicted_return_minutes": None,
    "session_duration": 15.3
}
```

## API Endpoints

### Core Operations
- `POST /api/presence/start-monitoring` - Start comprehensive monitoring
- `POST /api/presence/stop-monitoring` - Stop monitoring  
- `GET /api/presence/status/<user_id>` - Get current presence status
- `POST /api/presence/interaction` - Record user interaction
- `POST /api/presence/heartbeat` - Update presence heartbeat

### Analytics & Management
- `GET /api/presence/availability/<user_id>` - Check availability for interaction
- `GET /api/presence/analytics/<user_id>` - Get presence analytics and patterns
- `GET /api/presence/active-users` - List all users with active monitoring
- `GET /api/presence/health` - System health check

### Configuration
- `GET/POST /api/presence/config/<user_id>` - Get/update presence configuration

## Integration Layer

The integration layer (`integration.py`) provides seamless connection with other system modules:

### Persona System Integration
```python
# Get presence for persona decision-making
persona_presence = await presence_integration.get_presence_for_persona(user_id)

# Check if persona should proactively engage
engagement = await presence_integration.should_persona_proactively_engage(user_id)
```

### Memory System Integration
```python
# Get presence context for memory storage
memory_context = await presence_integration.get_presence_context_for_memory(user_id)
```

### Safety System Integration  
```python
# Get safety context based on presence
safety_context = await presence_integration.get_presence_safety_context(user_id)
```

### Voice System Integration
```python
# Determine voice interaction appropriateness
voice_context = await presence_integration.get_voice_interaction_context(user_id)
```

## Presence States & Contexts

### Unified Presence States
1. **Highly Engaged** - Actively interacting with high engagement
2. **Actively Present** - Present and interacting normally  
3. **Passively Present** - Present but low engagement
4. **Briefly Away** - Short absence, likely returning
5. **Away** - Extended absence
6. **Deeply Away** - Long absence, unlikely to return soon

### Presence Contexts
1. **Focused Session** - Deep work or conversation
2. **Casual Browsing** - Light engagement
3. **Multitasking** - Divided attention
4. **Background Mode** - App in background
5. **Break Time** - Taking a break
6. **End of Session** - Winding down

## Key Metrics

### Availability Scoring (0.0 - 1.0)
- Combines presence state, engagement, and focus
- Used to determine if user is available for interaction
- Threshold: >0.5 for availability

### Attention Level (0.0 - 1.0)  
- Measures user's current attention and focus
- Based on interaction patterns and activity
- High attention (>0.7) indicates deep engagement

### Interruption Receptivity (0.0 - 1.0)
- How receptive user is to interruptions
- Balances availability with respect for focus
- Threshold: >0.6 for appropriate interruptions

## Privacy & Configuration

The system is designed with privacy in mind:

### Privacy Controls
- **Background Sensing**: Can be disabled
- **System Metrics**: Optional collection
- **Detailed Activity**: Configurable granularity
- **Data Retention**: Configurable history periods

### Configurable Thresholds
- **Idle Timings**: Customizable idle detection periods
- **Engagement Levels**: Adjustable engagement thresholds  
- **Notification Preferences**: Control what triggers notifications
- **Fusion Weights**: Adjust importance of different detection methods

## Database Schema

### Tables Created
1. **presence_history** - Historical presence states and transitions
2. **presence_patterns** - Learned user behavior patterns  
3. **presence_events** - Raw events from all detection sources
4. **session_metrics** - Session-specific tracking data
5. **idle_patterns** - Individual idle behavior patterns
6. **background_signals** - Ambient sensing data

## Usage Example

```python
from backend.modules.presence import presence_integration

# Start comprehensive presence monitoring
session_data = await presence_integration.start_session_with_presence(
    user_id="user123",
    session_id="session456"
)

# Record user interactions
await presence_integration.record_interaction_across_systems(
    user_id="user123", 
    interaction_type="message",
    interaction_data={"content": "Hello AI!"}
)

# Check if persona should proactively engage
engagement_check = await presence_integration.should_persona_proactively_engage("user123")

if engagement_check["should_engage"]:
    engagement_type = engagement_check["engagement_type"]
    # Trigger appropriate persona response based on engagement_type
```

## Performance Considerations

- **Update Frequency**: Presence updated every 15 seconds
- **Data Retention**: Configurable history periods to manage storage
- **Efficient Queries**: Indexed database tables for fast lookups
- **Async Operations**: Non-blocking presence monitoring
- **Resource Usage**: Minimal system impact through efficient background sensing

## Commercial Considerations

- **Privacy Compliance**: Configurable data collection for GDPR/privacy requirements
- **Scalable Architecture**: Supports multiple concurrent users
- **API-First Design**: Easy integration with commercial applications
- **Configurable Sensitivity**: Adjustable detection thresholds for different environments
- **Professional Features**: Analytics, patterns, and reporting for business use

The Ambient Presence Sensing system provides the foundation for natural, contextual AI interactions by understanding when and how users are present, enabling the persona to respond appropriately to user availability and engagement levels.
