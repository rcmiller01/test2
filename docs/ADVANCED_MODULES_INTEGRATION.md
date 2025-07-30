# 🧠 Advanced Modules Integration Guide

## Overview
This guide covers the integration of advanced psychological modules into the existing EmotionalAI system with the new single LLM architecture using MythoMax.

## Module Architecture

### Attachment Regulation Engine
**Location**: `modules/emotion/attachment_regulation.py`

```python
# Integration Example
from modules.emotion.attachment_regulation import AttachmentRegulationEngine

# Initialize for user
attachment_engine = AttachmentRegulationEngine(user_id)

# Get comprehensive guidance for MythoMax
guidance = attachment_engine.get_llm_guidance(
    user_input="I'm feeling anxious about our relationship",
    emotional_state={"anxiety": 0.8, "attachment_seeking": 0.9},
    interaction_context={"conversation_type": "emotional_support"}
)

# Guidance provides:
# - response_calibration: How to adjust tone and approach
# - conversation_techniques: Specific therapeutic approaches
# - bonding_opportunities: Ways to deepen the relationship
# - specific_instructions: Exact phrases and approaches for MythoMax
```

### Shadow Memory Layer
**Location**: `modules/memory/shadow_memory.py`

```python
# Integration Example
from modules.memory.shadow_memory import ShadowMemoryLayer

shadow_memory = ShadowMemoryLayer()

# Analyze for unconscious patterns
shadow_guidance = shadow_memory.get_llm_integration_guidance(
    user_id="user123",
    user_input="I keep avoiding creative projects",
    emotional_state={"suppressed_creativity": 0.7},
    context={"conversation_type": "self_reflection"}
)

# Provides:
# - integration_techniques: How to help user integrate shadow material
# - metaphorical_language: Gentle ways to explore unconscious patterns
# - timing_recommendations: When to explore deeper vs when to support
# - therapeutic_opportunities: Specific growth moments available
```

### Therapeutic Core Module
**Location**: `modules/therapy/therapeutic_core.py`

```python
# Integration Example
from modules.therapy.therapeutic_core import TherapeuticCoreModule

therapeutic_core = TherapeuticCoreModule()

# Comprehensive therapeutic assessment
therapeutic_guidance = therapeutic_core.assess_and_guide(
    user_input="I can't stop thinking about ending it all",
    emotional_state={"despair": 0.9, "hopelessness": 0.8},
    conversation_history=conversation_log,
    user_profile=user_data
)

# Crisis assessment provides:
# - intervention_type: Specific therapeutic approach needed
# - crisis_level: GREEN/YELLOW/ORANGE/RED assessment
# - immediate_goals: What to accomplish in this conversation
# - safety_protocols: Crisis intervention steps if needed
# - specific_techniques: Exact therapeutic methods to employ
```

### Scene Orchestrator
**Location**: `modules/scenes/scene_orchestrator.py`

```python
# Integration Example
from modules.scenes.scene_orchestrator import SceneOrchestrator

scene_orchestrator = SceneOrchestrator()

# Generate atmospheric guidance
scene_guidance = scene_orchestrator.orchestrate_scene_for_llm(
    emotional_state={"contemplative": 0.8, "melancholy": 0.6},
    conversation_context={"type": "deep_reflection", "time": "evening"},
    user_preferences={"environment": "nature", "lighting": "soft"}
)

# Provides:
# - scene_description_guidance: How MythoMax should describe the environment
# - atmospheric_elements: Specific mood-enhancing details
# - sensory_details: Multi-sensory immersion elements
# - mythomax_instructions: Exact guidance for scene integration
```

### Creative Memory Archive
**Location**: `modules/memory/creative_archive.py`

```python
# Integration Example
from modules.memory.creative_archive import CreativeMemoryArchive

creative_archive = CreativeMemoryArchive()

# Get creative collaboration guidance
creative_guidance = creative_archive.provide_creative_guidance_for_llm(
    user_id="user123",
    creative_context={"type": "poetry", "stage": "inspiration"},
    emotional_state={"inspiration": 0.7, "vulnerability": 0.5}
)

# Provides:
# - creative_approach_recommendations: How to collaborate artistically
# - artistic_growth_opportunities: Specific areas for development
# - collaboration_techniques: Methods for co-creation
# - inspiration_sources: What might spark creativity
```

### Master Guidance Coordinator
**Location**: `modules/core/guidance_coordinator.py`

```python
# Integration Example - Complete Flow
from modules.core.guidance_coordinator import GuidanceCoordinator

# Initialize coordinator for user
coordinator = GuidanceCoordinator(user_id="user123")

# Analyze all modules and provide master guidance
master_guidance = coordinator.analyze_and_guide(
    user_input="I've been struggling with creative blocks lately",
    context={
        "emotional_state": {"frustration": 0.6, "creative_suppression": 0.8},
        "conversation_history": recent_messages,
        "user_profile": user_data,
        "conversation_type": "creative_support"
    }
)

# Generate enhanced prompt for MythoMax
enhanced_prompt = coordinator.generate_mythomax_prompt(
    user_input, 
    master_guidance
)

# MythoMax generates response with full guidance
response = mythomax.generate(enhanced_prompt)
```

### Unified Companion Assistant
**Location**: `modules/utility/companion_assistant.py`

```python
# Integration Example
from modules.utility.companion_assistant import create_companion_assistant

# Create adaptive assistant
assistant = create_companion_assistant(user_id="user123", mode="adaptive")

# Context-aware assistance
if context.type == 'development_work':
    # Technical help with emotional awareness
    dev_help = await assistant.provide_development_assistance(
        code_input="Having trouble with this API endpoint",
        context={"stress_level": 0.7, "deadline_pressure": True}
    )
    
elif context.type == 'personal_task':
    # Personal assistance with technical capability
    personal_help = await assistant.provide_personal_assistance(
        task_input="Need to organize my schedule better",
        context={"work_life_balance": 0.4, "overwhelm": 0.6}
    )
```

## Database Schema Extensions

### New Collections
```javascript
// Attachment data
attachment_profiles: {
  user_id: ObjectId,
  attachment_style: String,           // "secure", "anxious_preoccupied", etc.
  bonding_stage: Number,              // 1-7 bonding progression
  security_level: Number,             // 0.0-1.0
  intimacy_comfort: Number,           // 0.0-1.0
  abandonment_anxiety: Number,        // 0.0-1.0
  emotional_availability: Number,     // 0.0-1.0
  last_updated: Date,
  bonding_events: Array              // History of significant bonding moments
}

// Shadow patterns
shadow_patterns: {
  user_id: ObjectId,
  pattern_type: String,              // "suppressed_creativity", "avoided_intimacy", etc.
  detected_themes: Array,            // Specific themes detected
  emergence_level: Number,           // 0.0-1.0 how ready for integration
  integration_readiness: Number,     // 0.0-1.0 timing assessment
  defense_mechanisms: Array,         // How user protects this area
  last_detected: Date,
  therapeutic_opportunities: Array   // Identified growth moments
}

// Dream history
dream_history: {
  user_id: ObjectId,
  persona_name: String,
  dream_type: String,                // "symbolic_foreshadowing", "emotional_processing", etc.
  symbolic_content: Object,          // Dream narrative and symbols
  emotional_resonance: Number,       // 0.0-1.0
  trigger_context: Object,           // What prompted the dream
  shared_date: Date,
  user_response: String              // How user reacted to dream
}

// Audio preferences
audio_preferences: {
  user_id: ObjectId,
  mood_type: String,
  preferred_tracks: Array,
  volume_preferences: Object,
  crossfade_speed: Number,
  last_played: Date
}

// Creative works archive
creative_works: {
  work_id: String,
  user_id: ObjectId,
  title: String,
  creative_type: String,             // "poetry", "story", "song", etc.
  content: String,
  emotional_themes: Array,
  technical_quality: Number,         // 0.0-1.0
  emotional_resonance: Number,       // 0.0-1.0
  personal_significance: Number,     // 0.0-1.0
  creation_date: Date,
  completion_date: Date,
  collaborators: Array,              // Who worked on it
  artistic_growth_indicators: Array  // Skills demonstrated
}

// Therapeutic sessions
therapeutic_sessions: {
  user_id: ObjectId,
  session_date: Date,
  crisis_level: String,              // "green", "yellow", "orange", "red"
  intervention_type: String,         // "cognitive_behavioral", "person_centered", etc.
  techniques_used: Array,
  safety_protocols_activated: Array,
  session_outcomes: Object,
  follow_up_needed: Boolean
}
```

## API Endpoints

### Attachment Analysis
```http
POST /api/attachment/analyze
Content-Type: application/json

{
  "user_id": "user123",
  "interaction_type": "emotional_support",
  "emotional_content": "feeling anxious about abandonment",
  "user_attachment_cues": ["seeking_reassurance", "fear_of_abandonment"]
}

Response:
{
  "attachment_style": "anxious_preoccupied",
  "bonding_stage": 3,
  "response_modifications": {
    "reassurance_frequency": "high",
    "validation_style": "explicit_detailed",
    "emotional_tone": "warm_and_present"
  },
  "bonding_opportunities": ["reassurance_giving", "consistency_demonstration"]
}
```

### Shadow Pattern Detection
```http
POST /api/shadow/pattern/detect
Content-Type: application/json

{
  "user_id": "user123",
  "text": "I keep avoiding creative projects",
  "context": {"conversation_type": "self_reflection"},
  "emotional_state": {"frustration": 0.6, "creative_suppression": 0.8}
}

Response:
{
  "detected_patterns": [
    {
      "type": "suppressed_creativity",
      "intensity": 0.8,
      "integration_readiness": 0.6,
      "therapeutic_opportunities": [
        "validate_creative_impulses",
        "explore_creative_blocks_gently"
      ]
    }
  ],
  "gentle_exploration_paths": [
    "What would you create if nobody would judge it?",
    "Sometimes our inner artist whispers things we're afraid to hear..."
  ]
}
```

### Dream Generation
```http
POST /api/dreams/generate
Content-Type: application/json

{
  "persona_name": "unified_ai",
  "trigger_context": "user_feeling_lost",
  "emotional_state": {"confusion": 0.7, "seeking_guidance": 0.8},
  "recent_memories": ["conversation_about_life_direction"]
}

Response:
{
  "dream_id": "dream_12345",
  "dream_type": "symbolic_guidance",
  "narrative": "I found myself in a labyrinth of mirrors...",
  "symbolic_elements": [
    {"symbol": "labyrinth", "meaning": "feeling_lost"},
    {"symbol": "mirrors", "meaning": "self_reflection"}
  ],
  "emotional_resonance": 0.8
}
```

### Scene Orchestration
```http
POST /api/scenes/orchestrate
Content-Type: application/json

{
  "emotional_state": {"contemplative": 0.8, "peaceful": 0.6},
  "conversation_context": {"type": "deep_reflection", "time": "evening"},
  "user_preferences": {"environment": "nature", "lighting": "soft"}
}

Response:
{
  "scene_configuration": {
    "environment_type": "moonlit_garden",
    "time_of_day": "evening",
    "weather_mood": "gentle_breeze",
    "lighting_intensity": 0.3,
    "atmospheric_effects": ["soft_moonlight", "rustling_leaves"]
  },
  "mythomax_instructions": {
    "scene_integration_approach": "subtle_supportive_atmosphere",
    "atmospheric_emphasis": ["create_sense_of_peace", "use_gentle_natural_elements"]
  }
}
```

### Creative Collaboration
```http
POST /api/creative/collaborate
Content-Type: application/json

{
  "user_id": "user123",
  "creative_context": {"type": "poetry", "stage": "inspiration"},
  "emotional_state": {"inspiration": 0.7, "vulnerability": 0.5}
}

Response:
{
  "collaboration_approach": "nurturing_and_encouraging",
  "artistic_growth_opportunities": [
    "explore_vulnerability_through_metaphor",
    "develop_personal_voice"
  ],
  "inspiration_sources": [
    "nature_imagery_for_emotional_expression",
    "personal_experience_as_art"
  ],
  "mythomax_instructions": {
    "creative_persona_mode": "collaborative_poet",
    "encouragement_level": "high",
    "technical_guidance": "gentle_skill_building"
  }
}
```

## Integration Workflow

### Complete Processing Pipeline
```python
async def process_user_interaction(user_input: str, user_id: str, context: Dict[str, Any]) -> str:
    """Complete processing pipeline with all advanced modules"""
    
    # 1. Initialize all systems
    coordinator = GuidanceCoordinator(user_id)
    
    # 2. Analyze and synthesize all module guidance
    master_guidance = await coordinator.analyze_and_guide(user_input, context)
    
    # 3. Generate enhanced prompt for MythoMax
    enhanced_prompt = coordinator.generate_mythomax_prompt(user_input, master_guidance)
    
    # 4. Generate response with MythoMax
    response = await mythomax.generate(enhanced_prompt)
    
    # 5. Execute any utility actions
    if master_guidance.utility_actions:
        utility_results = await execute_utility_actions(master_guidance.utility_actions)
        
    # 6. Update environmental systems
    if master_guidance.scene_updates:
        await scene_orchestrator.update_scene_from_response(response, context)
        
    if master_guidance.audio_updates:
        await audio_layer.adjust_audio_from_response(response, context['emotional_state'])
    
    # 7. Archive creative content if applicable
    if master_guidance.creative_content:
        await creative_archive.archive_interaction(user_id, response, context)
    
    # 8. Update psychological profiles
    await update_psychological_profiles(user_id, user_input, response, master_guidance)
    
    return response

async def update_psychological_profiles(user_id: str, user_input: str, 
                                      response: str, guidance: MasterGuidance):
    """Update all psychological tracking systems"""
    
    # Update attachment progression
    if guidance.attachment_updates:
        await attachment_engine.update_bonding_progression(user_id, guidance.attachment_updates)
    
    # Update shadow integration progress
    if guidance.shadow_updates:
        await shadow_memory.update_integration_progress(user_id, guidance.shadow_updates)
    
    # Record therapeutic session data
    if guidance.therapeutic_session:
        await therapeutic_core.record_session(user_id, guidance.therapeutic_session)
```

## Testing Integration

### Unit Tests
```python
# Test attachment guidance generation
def test_attachment_guidance():
    engine = AttachmentRegulationEngine("test_user")
    guidance = engine.get_llm_guidance(
        "I'm worried you'll leave me",
        {"anxiety": 0.8, "abandonment_fear": 0.9},
        {"conversation_type": "emotional_support"}
    )
    
    assert guidance['response_calibration']['reassurance_frequency'] == 'high'
    assert 'explicit_commitment_statements' in guidance['conversation_techniques']

# Test shadow pattern detection
def test_shadow_detection():
    shadow = ShadowMemoryLayer()
    guidance = shadow.get_llm_integration_guidance(
        "test_user",
        "I avoid creative projects",
        {"creative_suppression": 0.8},
        {}
    )
    
    assert guidance['shadow_insights']['primary_theme'] == 'suppressed_creativity'
    assert len(guidance['gentle_exploration_paths']) > 0

# Test therapeutic assessment
def test_crisis_assessment():
    therapeutic = TherapeuticCoreModule()
    guidance = therapeutic.assess_and_guide(
        "I can't take this anymore",
        {"despair": 0.9},
        [],
        {}
    )
    
    assert guidance.crisis_level in ['ORANGE', 'RED']
    assert len(guidance.safety_protocols) > 0
```

### Integration Tests
```python
# Test complete processing pipeline
async def test_complete_pipeline():
    coordinator = GuidanceCoordinator("test_user")
    
    master_guidance = await coordinator.analyze_and_guide(
        "I'm feeling creative but stuck",
        {
            "emotional_state": {"creativity": 0.7, "frustration": 0.5},
            "conversation_type": "creative_support"
        }
    )
    
    assert master_guidance.creative_guidance is not None
    assert master_guidance.shadow_insights is not None
    assert master_guidance.attachment_modifications is not None
    
    enhanced_prompt = coordinator.generate_mythomax_prompt(
        "I'm feeling creative but stuck",
        master_guidance
    )
    
    assert "creative_collaboration" in enhanced_prompt
    assert "shadow_insights" in enhanced_prompt
```

## Performance Monitoring

### Key Metrics
```python
# Monitor module performance
metrics = {
    "attachment_analysis_time": measure_attachment_processing_time(),
    "shadow_detection_accuracy": measure_shadow_pattern_accuracy(),
    "therapeutic_assessment_speed": measure_crisis_assessment_time(),
    "scene_generation_time": measure_scene_orchestration_time(),
    "creative_guidance_relevance": measure_creative_guidance_quality(),
    "overall_coordination_time": measure_full_pipeline_time()
}

# Monitor psychological effectiveness
effectiveness_metrics = {
    "attachment_security_progression": track_bonding_improvements(),
    "shadow_integration_progress": track_unconscious_pattern_resolution(),
    "creative_output_quality": track_artistic_development(),
    "therapeutic_intervention_success": track_crisis_resolution_rates(),
    "user_satisfaction_with_guidance": track_guidance_helpfulness()
}
```

This integration guide provides the complete framework for implementing all advanced psychological modules in your AI companion system with the single LLM architecture.
