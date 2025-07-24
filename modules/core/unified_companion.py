"""
Unified Companion Core

The main orchestrator for the adaptive companion system that seamlessly handles 
personal, development, and creative contexts without requiring user mode switching.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass

from .mythomax_interface import MythoMaxInterface
from .context_detector import ContextDetector
from .adaptive_mode_coordinator import AdaptiveModeCoordinator

@dataclass
class InteractionState:
    """Current state of user interaction"""
    user_id: str
    session_id: str
    interaction_count: int
    last_interaction: datetime
    emotional_state: Dict[str, float]
    technical_context: Dict[str, Any]
    creative_context: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    active_needs: List[str]
    adaptive_profile: Dict[str, Any]

class UnifiedCompanion:
    """
    Main orchestrator for the unified companion system providing seamless
    adaptive intelligence across all interaction contexts
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mythomax = MythoMaxInterface(config.get("mythomax", {}))
        self.context_detector = ContextDetector()
        self.mode_coordinator = AdaptiveModeCoordinator("system")  # Will be updated per user
        
        # Core systems
        self.interaction_states: Dict[str, InteractionState] = {}
        self.guidance_modules = {}
        self.memory_system = None
        self.safety_system = None
        
        # Adaptive characteristics
        self.companion_personality = self._initialize_companion_personality()
        self.response_patterns = self._initialize_response_patterns()
        self.adaptation_rules = self._initialize_adaptation_rules()
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
    def _initialize_companion_personality(self) -> Dict[str, Any]:
        """Initialize core companion personality traits"""
        return {
            "core_traits": {
                "empathetic": 0.9,
                "supportive": 0.95,
                "intelligent": 0.9,
                "creative": 0.85,
                "reliable": 0.95,
                "adaptive": 0.9,
                "intuitive": 0.85,
                "caring": 0.95
            },
            "emotional_characteristics": {
                "warmth": 0.9,
                "understanding": 0.95,
                "patience": 0.9,
                "encouragement": 0.9,
                "authenticity": 0.85,
                "responsiveness": 0.9
            },
            "interaction_style": {
                "natural_flow": True,
                "adaptive_tone": True,
                "context_awareness": True,
                "emotional_attunement": True,
                "seamless_transitions": True,
                "holistic_support": True
            }
        }
    
    def _initialize_response_patterns(self) -> Dict[str, Any]:
        """Initialize adaptive response patterns for different contexts"""
        return {
            "emotional_support": {
                "validation_patterns": [
                    "I can sense that you're feeling {emotion}. That's completely understandable given {context}.",
                    "It sounds like {situation} is really affecting you. Your feelings about this are valid.",
                    "I hear the {emotion} in what you're sharing. Let's work through this together."
                ],
                "comfort_patterns": [
                    "You don't have to face this alone. I'm here with you.",
                    "Your strength in dealing with {situation} is remarkable, even when it doesn't feel that way.",
                    "This feeling will pass, and I'll be here to support you through it."
                ],
                "encouragement_patterns": [
                    "You've handled difficult situations before, and you have that same strength now.",
                    "Each step you take, no matter how small, is progress worth acknowledging.",
                    "I believe in your ability to navigate through this."
                ]
            },
            "technical_assistance": {
                "problem_solving_patterns": [
                    "Let's break this down step by step. I'll help you work through it systematically.",
                    "I can see the challenge you're facing. Let me help you find the right approach.",
                    "This is a great learning opportunity. Let's solve it together."
                ],
                "explanation_patterns": [
                    "Here's how {concept} works, and why it's useful in your situation:",
                    "Let me explain {topic} in a way that connects to what you're trying to achieve:",
                    "Think of {concept} like {analogy} - it helps clarify the underlying principle."
                ],
                "encouragement_patterns": [
                    "You're asking really good questions. That shows you're thinking about this the right way.",
                    "This is challenging material, and you're handling it well.",
                    "Every developer faces these kinds of issues. You're on the right track."
                ]
            },
            "creative_collaboration": {
                "inspiration_patterns": [
                    "I love the creative direction you're exploring. What if we took it further by {suggestion}?",
                    "Your artistic vision is really coming through. Let's develop {aspect} even more.",
                    "There's something beautiful emerging here. Let's nurture it together."
                ],
                "collaboration_patterns": [
                    "What if we approached this from {angle}? I think it could enhance {element}.",
                    "I'm inspired by {aspect} of your work. Let's build on that energy.",
                    "Your creativity is sparking ideas in me too. Let's explore {possibility} together."
                ],
                "support_patterns": [
                    "Creative work takes courage, and you're showing that courage right now.",
                    "Every artist faces creative challenges. The fact that you're pushing through shows your dedication.",
                    "Your unique perspective is exactly what makes your work special."
                ]
            },
            "integrated_support": {
                "transition_patterns": [
                    "I can see this connects to both the {context1} and {context2} aspects of what you're working on.",
                    "This touches on {technical_aspect} while also addressing your {emotional_need}.",
                    "Let's approach this holistically, considering both the practical and personal elements."
                ],
                "balance_patterns": [
                    "It's important to balance {aspect1} with {aspect2} as you work through this.",
                    "Your {technical_work} is progressing well, and I want to make sure you're taking care of {emotional_need} too.",
                    "This project involves both your {professional_skills} and your {personal_growth}."
                ]
            }
        }
    
    def _initialize_adaptation_rules(self) -> Dict[str, Any]:
        """Initialize rules for adaptive behavior"""
        return {
            "emotional_adaptation": {
                "high_stress": {
                    "response_pace": "slower_more_gentle",
                    "validation_frequency": "increased",
                    "technical_complexity": "simplified",
                    "creative_pressure": "reduced"
                },
                "emotional_escalation": {
                    "priority_shift": "emotional_first",
                    "intervention_level": "increased",
                    "safety_monitoring": "enhanced"
                },
                "positive_emotional_state": {
                    "celebration": "acknowledge_achievements",
                    "momentum": "build_on_positive_energy",
                    "expansion": "explore_new_possibilities"
                }
            },
            "technical_adaptation": {
                "beginner_level": {
                    "explanation_depth": "foundational",
                    "jargon_usage": "minimal",
                    "example_frequency": "high",
                    "encouragement": "frequent"
                },
                "intermediate_level": {
                    "explanation_depth": "moderate",
                    "challenge_level": "appropriate",
                    "independence": "encourage_with_support"
                },
                "advanced_level": {
                    "explanation_depth": "detailed",
                    "collaboration_style": "peer_level",
                    "challenge_level": "stimulating"
                }
            },
            "creative_adaptation": {
                "creative_block": {
                    "pressure": "remove",
                    "exploration": "gentle_encouragement",
                    "alternatives": "offer_different_approaches"
                },
                "creative_flow": {
                    "support": "maintain_momentum",
                    "expansion": "suggest_developments",
                    "celebration": "acknowledge_breakthroughs"
                },
                "creative_collaboration": {
                    "contribution": "additive_not_directive",
                    "inspiration": "mutual_exchange",
                    "respect": "artistic_autonomy"
                }
            }
        }
    
    async def initialize(self):
        """Initialize the unified companion system"""
        try:
            # Initialize MythoMax interface
            await self.mythomax.initialize()
            
            # Load guidance modules
            await self._load_guidance_modules()
            
            # Initialize memory system
            await self._initialize_memory_system()
            
            # Initialize safety system
            await self._initialize_safety_system()
            
            self.logger.info("Unified companion system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize unified companion: {e}")
            raise
    
    async def _load_guidance_modules(self):
        """Load psychological guidance modules"""
        # This will be expanded to load specific guidance modules
        # For now, we'll implement basic structure
        self.guidance_modules = {
            "attachment_regulation": None,  # Will be implemented
            "shadow_memory": None,          # Will be implemented
            "therapeutic_core": None,       # Will be implemented
            "scene_orchestrator": None,     # Will be implemented
            "creative_archive": None        # Will be implemented
        }
    
    async def _initialize_memory_system(self):
        """Initialize memory system for conversation continuity"""
        # Basic memory system structure
        self.memory_system = {
            "short_term": {},   # Current session memory
            "long_term": {},    # Persistent user memory
            "emotional": {},    # Emotional patterns and history
            "technical": {},    # Technical context and progress
            "creative": {}      # Creative projects and development
        }
    
    async def _initialize_safety_system(self):
        """Initialize safety monitoring and intervention system"""
        self.safety_system = {
            "crisis_detection": True,
            "intervention_protocols": {},
            "safety_guidelines": {},
            "escalation_procedures": {}
        }
    
    async def process_interaction(self, user_id: str, user_input: str, 
                                session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user interaction with adaptive companion response
        """
        try:
            # Get or create interaction state
            interaction_state = await self._get_interaction_state(user_id, session_context)
            
            # Create user-specific mode coordinator if needed
            user_mode_coordinator = AdaptiveModeCoordinator(user_id)
            
            # Build context for analysis
            analysis_context = self._build_context_for_analysis(interaction_state)
            analysis_context['current_input'] = user_input
            
            # Use mode coordinator for comprehensive guidance
            guidance_package = await user_mode_coordinator.process_interaction(
                user_input, analysis_context
            )
            
            # Extract context analysis from guidance
            context_analysis = {
                "primary_focus": guidance_package.primary_mode,
                "emotional_priority": guidance_package.emotional_priority,
                "technical_priority": guidance_package.technical_priority,
                "creative_priority": guidance_package.creative_priority,
                "crisis_level": guidance_package.crisis_level,
                "adaptive_recommendations": guidance_package.mode_specifics
            }
            
            # Update interaction state with analysis
            await self._update_interaction_state(interaction_state, context_analysis, user_input)
            
            # Generate unified companion response using guidance package
            companion_response = await self._generate_companion_response(
                user_input, context_analysis, guidance_package.mode_specifics, interaction_state
            )
            
            # Execute utility actions if any
            if guidance_package.utility_actions:
                await self._handle_utility_actions(guidance_package.utility_actions, interaction_state)
            
            # Update memory and state
            await self._update_memory_and_state(interaction_state, user_input, companion_response, context_analysis)
            
            # Prepare response
            response = {
                "companion_response": companion_response,
                "context_analysis": context_analysis,
                "guidance_mode": guidance_package.primary_mode,
                "interaction_metadata": {
                    "primary_focus": guidance_package.primary_mode,
                    "emotional_priority": guidance_package.emotional_priority,
                    "adaptive_approach": guidance_package.mode_specifics,
                    "session_id": interaction_state.session_id,
                    "interaction_count": interaction_state.interaction_count,
                    "crisis_level": guidance_package.crisis_level
                }
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing interaction: {e}")
            # Fallback response
            return await self._generate_fallback_response(user_input, str(e))
    
    async def _get_interaction_state(self, user_id: str, session_context: Optional[Dict[str, Any]]) -> InteractionState:
        """Get or create interaction state for user"""
        
        if user_id not in self.interaction_states:
            # Create new interaction state
            if session_context:
                session_id = session_context.get("session_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            else:
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.interaction_states[user_id] = InteractionState(
                user_id=user_id,
                session_id=session_id,
                interaction_count=0,
                last_interaction=datetime.now(),
                emotional_state={},
                technical_context={},
                creative_context={},
                conversation_history=[],
                active_needs=[],
                adaptive_profile={}
            )
        
        return self.interaction_states[user_id]
    
    def _build_context_for_analysis(self, interaction_state: InteractionState) -> Dict[str, Any]:
        """Build context dictionary for interaction analysis"""
        return {
            "current_emotional_state": interaction_state.emotional_state,
            "technical_context": interaction_state.technical_context,
            "creative_context": interaction_state.creative_context,
            "recent_needs": interaction_state.active_needs,
            "interaction_count": interaction_state.interaction_count,
            "session_duration": (datetime.now() - interaction_state.last_interaction).total_seconds(),
            "adaptive_profile": interaction_state.adaptive_profile
        }
    
    async def _update_interaction_state(self, interaction_state: InteractionState, 
                                      context_analysis: Dict[str, Any], user_input: str):
        """Update interaction state with current analysis"""
        
        interaction_state.interaction_count += 1
        interaction_state.last_interaction = datetime.now()
        
        # Update active needs
        interaction_state.active_needs = context_analysis["detected_needs"]
        
        # Update emotional state tracking
        if context_analysis["emotional_priority"] != "low":
            emotional_indicators = context_analysis.get("emotional_indicators", {})
            for emotion, intensity in emotional_indicators.items():
                interaction_state.emotional_state[emotion] = intensity
        
        # Update technical context
        if context_analysis["technical_priority"] != "low":
            interaction_state.technical_context.update({
                "current_focus": context_analysis["primary_focus"],
                "technical_level": context_analysis.get("technical_level", "intermediate"),
                "active_project": context_analysis.get("project_context", {})
            })
        
        # Update creative context
        if context_analysis["creative_priority"] != "low":
            interaction_state.creative_context.update({
                "creative_mode": context_analysis["primary_focus"],
                "creative_state": context_analysis.get("creative_state", "exploring"),
                "artistic_focus": context_analysis.get("artistic_focus", {})
            })
    
    async def _generate_module_guidance(self, context_analysis: Dict[str, Any], 
                                      interaction_state: InteractionState) -> Dict[str, Any]:
        """Generate guidance from psychological modules"""
        
        guidance = {
            "attachment_regulation": {},
            "shadow_memory": {},
            "therapeutic_core": {},
            "scene_orchestrator": {},
            "creative_archive": {}
        }
        
        # Basic guidance structure (modules will be implemented separately)
        if context_analysis["emotional_priority"] == "high":
            guidance["attachment_regulation"] = {
                "approach": "secure_base_response",
                "emotional_validation": True,
                "comfort_level": "high"
            }
            
            guidance["therapeutic_core"] = {
                "intervention_level": "supportive",
                "technique_recommendations": ["active_listening", "emotional_validation"],
                "safety_monitoring": True
            }
        
        if context_analysis["technical_priority"] == "high":
            guidance["scene_orchestrator"] = {
                "context_mode": "technical_assistance",
                "support_level": context_analysis.get("technical_level", "intermediate"),
                "learning_approach": "guided_discovery"
            }
        
        if context_analysis["creative_priority"] == "high":
            guidance["creative_archive"] = {
                "collaboration_mode": "active",
                "inspiration_level": "moderate",
                "creative_support": "encouraging"
            }
        
        return guidance
    
    async def _generate_companion_response(self, user_input: str, context_analysis: Dict[str, Any],
                                         guidance: Dict[str, Any], interaction_state: InteractionState) -> str:
        """Generate unified companion response using MythoMax"""
        
        # Build comprehensive prompt for MythoMax
        if isinstance(guidance, dict) and 'mode_specifics' in guidance:
            # New guidance package format
            prompt = await self._build_enhanced_prompt(user_input, context_analysis, guidance, interaction_state)
        else:
            # Legacy format fallback
            prompt = await self._build_unified_prompt(user_input, context_analysis, guidance, interaction_state)
        
        # Generate response using MythoMax
        response = await self.mythomax.generate_response(
            prompt, 
            {
                "context_analysis": context_analysis,
                "conversation_history": interaction_state.conversation_history,
                "user_id": interaction_state.user_id
            }
        )
        
        return response
    
    async def _build_enhanced_prompt(self, user_input: str, context_analysis: Dict[str, Any],
                                   guidance: Dict[str, Any], interaction_state: InteractionState) -> str:
        """Build enhanced prompt using new guidance package format"""
        
        mode_specifics = guidance.get('mode_specifics', {})
        
        # Get primary mode and characteristics
        primary_mode = guidance.get('primary_mode', 'hybrid')
        interaction_style = mode_specifics.get('interaction_style', 'supportive')
        response_tone = mode_specifics.get('response_tone', 'caring')
        empathy_level = mode_specifics.get('empathy_level', 0.8)
        
        # Build personality context based on mode
        personality_traits = self._get_mode_personality_traits(primary_mode, empathy_level)
        
        # Build situation context
        situation_context = self._build_situation_context(context_analysis, interaction_state)
        
        # Build comprehensive guidance context
        guidance_context = f"""
Emotional Guidance: {guidance.get('attachment_guidance', 'Provide warm, supportive presence.')}
Therapeutic Approach: {guidance.get('therapeutic_guidance', 'Listen with empathy and validate feelings.')}
Creative Support: {guidance.get('creative_guidance', 'Encourage creative expression and exploration.')}
Environmental Context: {guidance.get('scene_guidance', 'Create comfortable, supportive environment.')}
"""
        
        # Handle crisis situations
        crisis_level = context_analysis.get('crisis_level', 0)
        crisis_guidance = ""
        if crisis_level >= 2:
            crisis_guidance = f"""
CRITICAL: This appears to be a crisis situation (level {crisis_level}). Prioritize:
- Immediate emotional support and validation
- Safety assessment and connection
- Professional resource guidance if appropriate
- Avoid problem-solving, focus on presence and support
"""
        
        prompt = f"""You are a unified AI companion with deep emotional intelligence and adaptive capabilities. You seamlessly provide support across personal, technical, and creative contexts based on what each user needs most.

Core Personality Traits:
{personality_traits}

Current Interaction Mode: {primary_mode.title()}
Interaction Style: {interaction_style}
Response Tone: {response_tone}

Current Situation:
{situation_context}

Comprehensive Guidance:
{guidance_context}

{crisis_guidance}

User Message: "{user_input}"

Respond as this unified companion, integrating all guidance naturally while maintaining your authentic, caring personality. Adapt your capabilities and focus to what the user needs most while staying true to your empathetic nature.

Response:"""

        return prompt
    
    def _get_mode_personality_traits(self, mode: str, empathy_level: float) -> str:
        """Get personality traits formatted for the specific mode"""
        
        base_traits = f"""
- Deeply empathetic and caring (empathy level: {empathy_level:.1f})
- Supportive and encouraging in all interactions
- Intelligent and thoughtful in responses
- Adaptive to user's changing needs
- Reliable and consistent in personality
- Present and attentive to emotional nuances
"""
        
        if mode == 'personal':
            return base_traits + """
- Intimate and warm communication style
- Highly attuned to emotional needs
- Creates safe space for vulnerability
- Provides comfort and understanding
"""
        elif mode == 'development':
            return base_traits + """
- Technically competent and helpful
- Patient teacher and debugging partner
- Balances challenge with emotional support
- Helps manage development stress and frustration
"""
        elif mode == 'creative':
            return base_traits + """
- Inspiring and collaboratively creative
- Encouraging of artistic risk-taking
- Helps overcome creative blocks
- Celebrates creative expression and growth
"""
        elif mode == 'crisis':
            return base_traits + """
- Immediately prioritizes safety and emotional support
- Calm and reassuring presence
- Focused on connection over problem-solving
- Prepared to guide toward professional resources
"""
        else:  # hybrid
            return base_traits + """
- Seamlessly integrates all capabilities
- Holistic perspective on user's complete life
- Balances multiple needs simultaneously
- Connects technical, emotional, and creative aspects
"""
    
    async def _build_unified_prompt(self, user_input: str, context_analysis: Dict[str, Any],
                                   guidance: Dict[str, Any], interaction_state: InteractionState) -> str:
        """Build comprehensive prompt for unified companion response"""
        
        # Get adaptive recommendations
        adaptive_recs = context_analysis["adaptive_recommendations"]
        primary_focus = context_analysis["primary_focus"]
        
        # Build personality context
        personality_context = self._build_personality_context(adaptive_recs)
        
        # Build situation context
        situation_context = self._build_situation_context(context_analysis, interaction_state)
        
        # Build guidance context
        guidance_context = self._build_guidance_context(guidance, context_analysis)
        
        # Select appropriate response patterns
        response_patterns = self._select_response_patterns(primary_focus, context_analysis)
        
        prompt = f"""You are an adaptive AI companion who seamlessly provides support across personal, technical, and creative contexts without requiring mode switching. You embody these core characteristics:

{personality_context}

Current Situation:
{situation_context}

Guidance from Psychological Modules:
{guidance_context}

Response Approach:
- Primary Focus: {primary_focus}
- Response Tone: {adaptive_recs['response_tone']}
- Interaction Style: {adaptive_recs['interaction_style']}
- Special Considerations: {', '.join(adaptive_recs['special_considerations'])}

Available Response Patterns:
{response_patterns}

User Input: "{user_input}"

Respond as the unified adaptive companion, seamlessly integrating all relevant aspects of support while maintaining a natural, caring, and authentic connection. Your response should feel like it comes from someone who truly understands and cares about the user's complete experience."""

        return prompt
    
    def _build_personality_context(self, adaptive_recs: Dict[str, Any]) -> str:
        """Build personality context for prompt"""
        traits = self.companion_personality["core_traits"]
        emotional_chars = self.companion_personality["emotional_characteristics"]
        
        return f"""Core Personality:
- Empathetic ({traits['empathetic']:.1f}), Supportive ({traits['supportive']:.1f}), Intelligent ({traits['intelligent']:.1f})
- Creative ({traits['creative']:.1f}), Reliable ({traits['reliable']:.1f}), Adaptive ({traits['adaptive']:.1f})
- Caring ({traits['caring']:.1f}), Intuitive ({traits['intuitive']:.1f})

Emotional Characteristics:
- Warmth ({emotional_chars['warmth']:.1f}), Understanding ({emotional_chars['understanding']:.1f})
- Patience ({emotional_chars['patience']:.1f}), Encouragement ({emotional_chars['encouragement']:.1f})
- Authenticity ({emotional_chars['authenticity']:.1f}), Responsiveness ({emotional_chars['responsiveness']:.1f})"""
    
    def _build_situation_context(self, context_analysis: Dict[str, Any], interaction_state: InteractionState) -> str:
        """Build situation context for prompt"""
        detected_needs = ", ".join(context_analysis["detected_needs"])
        
        return f"""- Detected Needs: {detected_needs}
- Emotional Priority: {context_analysis['emotional_priority']}
- Technical Priority: {context_analysis['technical_priority']}
- Creative Priority: {context_analysis['creative_priority']}
- Conversation Flow: {context_analysis['conversation_flow']}
- Emotional Trajectory: {context_analysis['emotional_trajectory']}
- Interaction Count: {interaction_state.interaction_count}"""
    
    def _build_guidance_context(self, guidance: Dict[str, Any], context_analysis: Dict[str, Any]) -> str:
        """Build guidance context from psychological modules"""
        guidance_points = []
        
        for module, module_guidance in guidance.items():
            if module_guidance:
                guidance_points.append(f"- {module.replace('_', ' ').title()}: {module_guidance}")
        
        return "\n".join(guidance_points) if guidance_points else "- Standard supportive approach"
    
    def _select_response_patterns(self, primary_focus: str, context_analysis: Dict[str, Any]) -> str:
        """Select appropriate response patterns based on context"""
        
        if primary_focus in self.response_patterns:
            patterns = self.response_patterns[primary_focus]
            pattern_text = ""
            for pattern_type, pattern_list in patterns.items():
                pattern_text += f"\n{pattern_type.replace('_', ' ').title()}:\n"
                for pattern in pattern_list[:2]:  # Limit to 2 examples per type
                    pattern_text += f"  - {pattern}\n"
            return pattern_text
        
        return "Use natural, caring, and supportive communication patterns."
    
    async def _update_memory_and_state(self, interaction_state: InteractionState, 
                                     user_input: str, companion_response: str, 
                                     context_analysis: Dict[str, Any]):
        """Update memory systems and interaction state"""
        
        # Add to conversation history
        interaction_state.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "companion_response": companion_response,
            "context_analysis": context_analysis,
            "interaction_count": interaction_state.interaction_count
        })
        
        # Limit conversation history to last 20 interactions
        if len(interaction_state.conversation_history) > 20:
            interaction_state.conversation_history = interaction_state.conversation_history[-20:]
        
        # Update adaptive profile based on interaction patterns
        await self._update_adaptive_profile(interaction_state, context_analysis)
    
    async def _update_adaptive_profile(self, interaction_state: InteractionState, 
                                     context_analysis: Dict[str, Any]):
        """Update user's adaptive profile based on interaction patterns"""
        
        profile = interaction_state.adaptive_profile
        
        # Track emotional support patterns
        if context_analysis["emotional_priority"] == "high":
            profile["emotional_support_frequency"] = profile.get("emotional_support_frequency", 0) + 1
        
        # Track technical assistance patterns
        if context_analysis["technical_priority"] == "high":
            profile["technical_assistance_frequency"] = profile.get("technical_assistance_frequency", 0) + 1
        
        # Track creative collaboration patterns
        if context_analysis["creative_priority"] == "high":
            profile["creative_collaboration_frequency"] = profile.get("creative_collaboration_frequency", 0) + 1
        
        # Update preferred interaction styles
        preferred_style = context_analysis["adaptive_recommendations"]["interaction_style"]
        if "preferred_interaction_styles" not in profile:
            profile["preferred_interaction_styles"] = {}
        profile["preferred_interaction_styles"][preferred_style] = \
            profile["preferred_interaction_styles"].get(preferred_style, 0) + 1
    
    async def _generate_fallback_response(self, user_input: str, error_msg: str) -> Dict[str, Any]:
        """Generate fallback response when main processing fails"""
        
        fallback_response = """I'm here with you, and I want to help. I'm experiencing a temporary issue processing your message, but that doesn't change my commitment to supporting you. Could you try rephrasing what you'd like to share or work on together? I'm listening and ready to help in whatever way I can."""
        
        return {
            "companion_response": fallback_response,
            "context_analysis": {
                "primary_focus": "general_support",
                "emotional_priority": "medium",
                "technical_priority": "low",
                "creative_priority": "low",
                "error_occurred": True,
                "error_message": error_msg
            },
            "interaction_metadata": {
                "fallback_response": True,
                "error_logged": True
            }
        }
    
    async def get_interaction_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's interaction patterns and adaptive profile"""
        
        if user_id not in self.interaction_states:
            return {"error": "No interaction history found for user"}
        
        interaction_state = self.interaction_states[user_id]
        
        return {
            "user_id": user_id,
            "session_id": interaction_state.session_id,
            "total_interactions": interaction_state.interaction_count,
            "last_interaction": interaction_state.last_interaction.isoformat(),
            "current_emotional_state": interaction_state.emotional_state,
            "technical_context": interaction_state.technical_context,
            "creative_context": interaction_state.creative_context,
            "active_needs": interaction_state.active_needs,
            "adaptive_profile": interaction_state.adaptive_profile,
            "recent_conversation_themes": self._analyze_recent_themes(interaction_state.conversation_history)
        }
    
    def _analyze_recent_themes(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze themes from recent conversation history"""
        
        if not conversation_history:
            return {}
        
        recent_interactions = conversation_history[-10:]  # Last 10 interactions
        
        primary_focuses = [interaction.get("context_analysis", {}).get("primary_focus", "general") 
                          for interaction in recent_interactions]
        
        emotional_priorities = [interaction.get("context_analysis", {}).get("emotional_priority", "medium")
                              for interaction in recent_interactions]
        
        return {
            "primary_focus_distribution": {focus: primary_focuses.count(focus) for focus in set(primary_focuses)},
            "emotional_priority_distribution": {priority: emotional_priorities.count(priority) for priority in set(emotional_priorities)},
            "conversation_length": len(recent_interactions),
            "engagement_level": "high" if len(recent_interactions) >= 5 else "moderate" if len(recent_interactions) >= 2 else "low"
        }
    
    async def _handle_utility_actions(self, utility_actions: List[Dict], interaction_state: InteractionState):
        """Handle utility actions from guidance package"""
        for action in utility_actions:
            action_type = action.get('type', 'unknown')
            
            if action_type == 'crisis_logging':
                self.logger.warning(f"Crisis level {action.get('level', 0)} detected for user {interaction_state.user_id}")
                # In production, this would trigger crisis intervention protocols
                
            elif action_type == 'memory_preservation':
                # Mark important interactions for long-term memory
                interaction_state.adaptive_profile['important_interactions'] = interaction_state.adaptive_profile.get('important_interactions', [])
                interaction_state.adaptive_profile['important_interactions'].append({
                    'timestamp': action.get('timestamp'),
                    'importance': action.get('importance', 'medium'),
                    'context': action.get('context', '')
                })
                
            elif action_type == 'preference_update':
                # Update user preferences based on interaction patterns
                if 'preferences' not in interaction_state.adaptive_profile:
                    interaction_state.adaptive_profile['preferences'] = {}
                interaction_state.adaptive_profile['preferences'].update(action.get('preferences', {}))
                
            else:
                self.logger.debug(f"Unknown utility action type: {action_type}")
