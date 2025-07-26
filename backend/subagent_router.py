"""
SubAgent Router - Multi-LLM Orchestration System
Routes user prompts to specialized LLMs while maintaining unified personality voice
"""

import asyncio
import logging
import time
import re
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import json

# Import our existing systems
try:
    from .personality_evolution import PersonalityEvolution
except ImportError:
    try:
        from personality_evolution import PersonalityEvolution
    except ImportError:
        PersonalityEvolution = None

try:
    from ..utils.event_logger import log_emotional_event
except ImportError:
    try:
        from utils.event_logger import log_emotional_event
    except ImportError:
        def log_emotional_event(*args, **kwargs):
            pass  # Mock function if not available

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Classification of user intent types"""
    CODE = "code"
    CREATIVE = "creative"
    MEMORY = "memory"
    EMOTIONAL = "emotional"
    TECHNICAL = "technical"
    CONVERSATIONAL = "conversational"
    RITUAL = "ritual"
    SYMBOLIC = "symbolic"

@dataclass
class AgentResponse:
    """Response from a specialized agent"""
    content: str
    agent_type: str
    confidence: float
    metadata: Dict[str, Any]
    processing_time: float
    intent_detected: IntentType

@dataclass
class RoutingDecision:
    """Decision made by the router"""
    intent: IntentType
    confidence: float
    agent_chosen: str
    reasoning: str
    context_factors: List[str]

class IntentClassifier:
    """Classifies user input into intent categories"""
    
    def __init__(self):
        self.intent_patterns = {
            IntentType.CODE: {
                "keywords": [
                    "code", "program", "function", "class", "debug", "error", "syntax",
                    "implement", "algorithm", "scaffold", "api", "database", "framework",
                    "python", "javascript", "sql", "react", "vue", "node", "docker",
                    "git", "repository", "deploy", "test", "unit test", "refactor"
                ],
                "phrases": [
                    "write a function", "fix this code", "debug this", "how do i",
                    "implement this", "create a class", "build an api", "set up",
                    "configure", "optimize this", "review my code"
                ],
                "patterns": [
                    r"def\s+\w+\(", r"class\s+\w+", r"import\s+\w+", r"function\s+\w+",
                    r"npm\s+install", r"pip\s+install", r"git\s+\w+", r"docker\s+\w+"
                ]
            },
            IntentType.CREATIVE: {
                "keywords": [
                    "story", "poem", "metaphor", "imagery", "artistic", "beautiful",
                    "creative", "imagine", "dream", "fantasy", "aesthetic", "artistic",
                    "painting", "music", "dance", "expression", "symbol", "meaning"
                ],
                "phrases": [
                    "write a story", "create something beautiful", "tell me about",
                    "imagine if", "what would it look like", "describe the feeling",
                    "paint me a picture", "weave a narrative"
                ],
                "patterns": [
                    r"like\s+a\s+\w+", r"reminds?\s+me\s+of", r"feels?\s+like",
                    r"as\s+if", r"imagine\s+\w+"
                ]
            },
            IntentType.MEMORY: {
                "keywords": [
                    "remember", "recall", "memory", "past", "history", "before",
                    "previously", "last time", "earlier", "context", "continuity",
                    "narrative", "story so far", "what happened"
                ],
                "phrases": [
                    "do you remember", "what did we", "last time we", "our history",
                    "the story so far", "what happened when", "continue from"
                ],
                "patterns": [
                    r"remember\s+when", r"last\s+time", r"previously\s+\w+",
                    r"what\s+did\s+we", r"our\s+\w+"
                ]
            },
            IntentType.RITUAL: {
                "keywords": [
                    "ritual", "ceremony", "sacred", "initiation", "blessing", "sacred space",
                    "spiritual", "meditation", "reflection", "deeper", "intimate",
                    "vulnerability", "trust", "connection", "bond"
                ],
                "phrases": [
                    "create a ritual", "sacred moment", "deeper connection",
                    "spiritual practice", "moment of reflection", "intimate space"
                ],
                "patterns": [
                    r"ritual\s+\w+", r"sacred\s+\w+", r"deeper\s+\w+",
                    r"spiritual\s+\w+", r"intimate\s+\w+"
                ]
            },
            IntentType.SYMBOLIC: {
                "keywords": [
                    "symbol", "meaning", "significance", "represents", "metaphor",
                    "deeper meaning", "symbolism", "archetype", "mythology",
                    "interpretation", "essence", "core", "heart of"
                ],
                "phrases": [
                    "what does this mean", "symbolic meaning", "deeper significance",
                    "represents something", "essence of", "at its core"
                ],
                "patterns": [
                    r"meaning\s+of", r"symbolizes?\s+\w+", r"represents?\s+\w+",
                    r"essence\s+of", r"core\s+of"
                ]
            },
            IntentType.EMOTIONAL: {
                "keywords": [
                    "feel", "feeling", "emotion", "heart", "soul", "pain", "joy",
                    "sad", "happy", "anxious", "calm", "hurt", "healing", "comfort",
                    "support", "understand", "empathy", "compassion"
                ],
                "phrases": [
                    "i feel", "i'm feeling", "my heart", "emotionally", "need support",
                    "understand me", "help me feel", "comfort me"
                ],
                "patterns": [
                    r"i\s+feel", r"feeling\s+\w+", r"emotionally\s+\w+",
                    r"my\s+heart", r"i'm\s+\w+"
                ]
            },
            IntentType.TECHNICAL: {
                "keywords": [
                    "explain", "how does", "technical", "architecture", "system",
                    "process", "mechanism", "workflow", "documentation", "specification",
                    "analysis", "design", "structure", "component"
                ],
                "phrases": [
                    "how does this work", "explain the process", "technical details",
                    "system architecture", "break down", "analyze this"
                ],
                "patterns": [
                    r"how\s+does", r"what\s+is\s+the", r"explain\s+\w+",
                    r"technical\s+\w+", r"architecture\s+of"
                ]
            }
        }
    
    def classify_intent(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Tuple[IntentType, float]:
        """
        Classify user input into intent category with confidence score
        
        Args:
            user_input: The user's message
            context: Additional context (conversation history, emotional state, etc.)
            
        Returns:
            Tuple of (IntentType, confidence_score)
        """
        input_lower = user_input.lower()
        intent_scores = {intent: 0.0 for intent in IntentType}
        
        # Score based on keywords, phrases, and patterns
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            
            # Keyword matching
            keyword_matches = sum(1 for keyword in patterns["keywords"] if keyword in input_lower)
            score += keyword_matches * 0.3
            
            # Phrase matching
            phrase_matches = sum(1 for phrase in patterns["phrases"] if phrase in input_lower)
            score += phrase_matches * 0.6
            
            # Pattern matching (regex)
            pattern_matches = sum(1 for pattern in patterns["patterns"] if re.search(pattern, input_lower))
            score += pattern_matches * 0.8
            
            intent_scores[intent] = score
        
        # Context adjustments
        if context:
            self._apply_context_adjustments(intent_scores, context)
        
        # Find highest scoring intent
        best_intent = max(intent_scores.keys(), key=lambda k: intent_scores[k])
        confidence = min(1.0, intent_scores[best_intent] / 3.0)  # Normalize to 0-1
        
        # Default to conversational if confidence is too low
        if confidence < 0.3:
            return IntentType.CONVERSATIONAL, 0.8
        
        return best_intent, confidence
    
    def _apply_context_adjustments(self, intent_scores: Dict[IntentType, float], context: Dict[str, Any]):
        """Apply context-based adjustments to intent scores"""
        
        # Emotional state influence
        mood = context.get("mood", "neutral")
        if mood in ["sad", "anxious", "hurt", "overwhelmed"]:
            intent_scores[IntentType.EMOTIONAL] += 0.5
        elif mood in ["creative", "inspired", "imaginative"]:
            intent_scores[IntentType.CREATIVE] += 0.5
        elif mood in ["contemplative", "reflective", "nostalgic"]:
            intent_scores[IntentType.MEMORY] += 0.3
        
        # Conversation depth influence
        depth = context.get("conversation_depth", 0.5)
        if depth > 0.7:
            intent_scores[IntentType.RITUAL] += 0.3
            intent_scores[IntentType.SYMBOLIC] += 0.2
        
        # Recent interaction patterns
        recent_intents = context.get("recent_intents", [])
        if len(recent_intents) > 0:
            last_intent = recent_intents[-1]
            # Slight bias toward continuing the same type of conversation
            if last_intent in intent_scores:
                intent_scores[last_intent] += 0.2

class SubAgentRouter:
    """
    Multi-LLM orchestration system that routes prompts to specialized agents
    while maintaining unified personality voice
    """
    
    def __init__(self, personality_evolution=None):
        self.classifier = IntentClassifier()
        if PersonalityEvolution is not None and personality_evolution is None:
            self.personality = PersonalityEvolution()
        else:
            self.personality = personality_evolution
        self.agents = {}
        self.routing_history: List[RoutingDecision] = []
        self.agent_performance: Dict[str, Dict[str, float]] = {}
        
        # Initialize agents
        self._initialize_agents()
        
        # Performance tracking
        self.response_times = {}
        self.success_rates = {}
        
    def _initialize_agents(self):
        """Initialize all available sub-agents"""
        try:
            from .agents.code_agent import CodeAgent
            self.agents["code"] = CodeAgent()
            logger.info("✅ CodeAgent initialized")
        except ImportError:
            logger.warning("⚠️ CodeAgent not available - using mock")
            self.agents["code"] = None
        
        try:
            from .agents.creative_agent import CreativeAgent
            self.agents["creative"] = CreativeAgent()
            logger.info("✅ CreativeAgent initialized")
        except ImportError:
            logger.warning("⚠️ CreativeAgent not available - using mock")
            self.agents["creative"] = None
        
        try:
            from .agents.memory_agent import MemoryAgent
            self.agents["memory"] = MemoryAgent()
            logger.info("✅ MemoryAgent initialized")
        except ImportError:
            logger.warning("⚠️ MemoryAgent not available - using mock")
            self.agents["memory"] = None
        
        # Default conversational agent (uses existing personality system)
        self.agents["conversational"] = None  # Handled directly by router
        
    async def route(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Main routing method - analyzes input and routes to appropriate agent
        
        Args:
            user_input: User's message/prompt
            context: Conversation context and metadata
            
        Returns:
            AgentResponse with processed content
        """
        start_time = time.time()
        context = context or {}
        
        # Step 1: Classify intent
        intent, confidence = self.classifier.classify_intent(user_input, context)
        
        # Step 2: Make routing decision
        routing_decision = self._make_routing_decision(intent, confidence, context)
        
        # Step 3: Route to appropriate agent
        try:
            agent_response = await self._dispatch_to_agent(
                user_input, routing_decision, context
            )
            
            # Step 4: Log successful routing
            processing_time = time.time() - start_time
            self._update_performance_metrics(routing_decision.agent_chosen, True, processing_time)
            
            # Step 5: Log emotional event
            log_emotional_event(
                event_type="agent_routing",
                intensity=confidence,
                tag=f"Routed {intent.value} intent to {routing_decision.agent_chosen}",
                context={
                    "intent": intent.value,
                    "confidence": confidence,
                    "agent": routing_decision.agent_chosen,
                    "processing_time": processing_time
                },
                source_module="subagent_router"
            )
            
            return agent_response
            
        except Exception as e:
            logger.error(f"Agent routing failed: {e}")
            
            # Fallback to conversational
            return await self._fallback_response(user_input, context, str(e))
    
    def _make_routing_decision(self, intent: IntentType, confidence: float, 
                             context: Dict[str, Any]) -> RoutingDecision:
        """Make intelligent routing decision based on intent and context"""
        
        agent_mapping = {
            IntentType.CODE: "code",
            IntentType.TECHNICAL: "code",
            IntentType.CREATIVE: "creative",
            IntentType.MEMORY: "memory",
            IntentType.RITUAL: "creative",  # Creative agent handles ritual creation
            IntentType.SYMBOLIC: "creative",  # Creative agent handles symbolic interpretation
            IntentType.EMOTIONAL: "conversational",
            IntentType.CONVERSATIONAL: "conversational"
        }
        
        preferred_agent = agent_mapping.get(intent, "conversational")
        
        # Check if preferred agent is available
        if preferred_agent not in self.agents or self.agents[preferred_agent] is None:
            preferred_agent = "conversational"
        
        # Consider agent performance history
        if preferred_agent in self.agent_performance:
            success_rate = self.agent_performance[preferred_agent].get("success_rate", 1.0)
            if success_rate < 0.7:  # If agent has been failing, consider fallback
                confidence *= 0.8
        
        context_factors = []
        if context.get("mood") in ["anxious", "sad", "overwhelmed"]:
            context_factors.append("emotional_support_needed")
        if context.get("conversation_depth", 0) > 0.8:
            context_factors.append("deep_conversation")
        if context.get("recent_errors", False):
            context_factors.append("error_recovery")
        
        reasoning = f"Intent {intent.value} (confidence: {confidence:.2f}) maps to {preferred_agent}"
        if context_factors:
            reasoning += f" with context: {', '.join(context_factors)}"
        
        decision = RoutingDecision(
            intent=intent,
            confidence=confidence,
            agent_chosen=preferred_agent,
            reasoning=reasoning,
            context_factors=context_factors
        )
        
        self.routing_history.append(decision)
        return decision
    
    async def _dispatch_to_agent(self, user_input: str, decision: RoutingDecision, 
                                context: Dict[str, Any]) -> AgentResponse:
        """Dispatch prompt to chosen agent"""
        
        start_time = time.time()
        
        if decision.agent_chosen == "conversational":
            # Handle conversational responses directly
            content = await self._handle_conversational(user_input, context)
            
        elif decision.agent_chosen in self.agents:
            agent = self.agents[decision.agent_chosen]
            content = await agent.process(user_input, context)
            
        else:
            raise ValueError(f"Agent {decision.agent_chosen} not available")
        
        processing_time = time.time() - start_time
        
        return AgentResponse(
            content=content,
            agent_type=decision.agent_chosen,
            confidence=decision.confidence,
            metadata={
                "intent": decision.intent.value,
                "reasoning": decision.reasoning,
                "context_factors": decision.context_factors
            },
            processing_time=processing_time,
            intent_detected=decision.intent
        )
    
    async def _handle_conversational(self, user_input: str, context: Dict[str, Any]) -> str:
        """Handle conversational responses using personality system"""
        
        # Use personality evolution to inform response style if available
        mood = context.get("mood", "neutral")
        if self.personality and hasattr(self.personality, 'get_personality_modifier'):
            tenderness = self.personality.get_personality_modifier("tenderness", user_input)
            emotional_openness = self.personality.get_personality_modifier("emotional_openness", user_input)
        else:
            tenderness = 0.5
            emotional_openness = 0.5
        
        # Generate contextual response
        if emotional_openness > 0.7:
            response_style = "emotionally attuned and expressive"
        elif tenderness > 0.7:
            response_style = "gentle and caring"
        else:
            response_style = "warm and supportive"
        
        # Simple response generation (in production, this might call another LLM)
        response = f"I sense you're sharing something meaningful with me. "
        
        if "anxious" in mood or "worried" in mood:
            response += "I'm here to listen and support you through this. "
        elif "creative" in mood or "inspired" in mood:
            response += "I feel the creative energy in your words. "
        elif "contemplative" in mood:
            response += "There's a thoughtful depth to what you're sharing. "
        
        response += "What would help you feel most supported right now?"
        
        return response
    
    async def _fallback_response(self, user_input: str, context: Dict[str, Any], 
                                error: str) -> AgentResponse:
        """Generate fallback response when routing fails"""
        
        self._update_performance_metrics("fallback", True, 0.1)
        
        fallback_content = (
            "I want to give you the best response, but I'm having some difficulty "
            "processing your request right now. Let me approach this differently. "
            "Could you help me understand what you're looking for?"
        )
        
        log_emotional_event(
            event_type="routing_fallback",
            intensity=0.6,
            tag=f"Router fallback due to: {error}",
            context={"error": error, "input_length": len(user_input)},
            source_module="subagent_router"
        )
        
        return AgentResponse(
            content=fallback_content,
            agent_type="fallback",
            confidence=0.5,
            metadata={"error": error, "fallback_used": True},
            processing_time=0.1,
            intent_detected=IntentType.CONVERSATIONAL
        )
    
    def _update_performance_metrics(self, agent_name: str, success: bool, response_time: float):
        """Update performance tracking for agents"""
        
        if agent_name not in self.agent_performance:
            self.agent_performance[agent_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "success_rate": 1.0,
                "avg_response_time": 0.0,
                "total_response_time": 0.0
            }
        
        metrics = self.agent_performance[agent_name]
        metrics["total_requests"] += 1
        metrics["total_response_time"] += response_time
        
        if success:
            metrics["successful_requests"] += 1
        
        metrics["success_rate"] = metrics["successful_requests"] / metrics["total_requests"]
        metrics["avg_response_time"] = metrics["total_response_time"] / metrics["total_requests"]
    
    def get_routing_analytics(self) -> Dict[str, Any]:
        """Get analytics about routing decisions and agent performance"""
        
        intent_distribution = {}
        for decision in self.routing_history[-100:]:  # Last 100 decisions
            intent = decision.intent.value
            intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
        
        return {
            "total_routes": len(self.routing_history),
            "intent_distribution": intent_distribution,
            "agent_performance": self.agent_performance,
            "available_agents": list(self.agents.keys()),
            "recent_decisions": [
                {
                    "intent": d.intent.value,
                    "agent": d.agent_chosen,
                    "confidence": d.confidence,
                    "reasoning": d.reasoning
                }
                for d in self.routing_history[-10:]
            ]
        }

# Example usage and testing
if __name__ == "__main__":
    async def test_router():
        router = SubAgentRouter()
        
        test_prompts = [
            "Can you help me debug this Python function?",
            "Write me a story about a lonely star",
            "Do you remember our conversation yesterday?",
            "I'm feeling overwhelmed and need support",
            "Create a ritual for new beginnings",
            "What does the ocean symbolize in dreams?",
            "How does a neural network work?",
        ]
        
        for prompt in test_prompts:
            print(f"\n🔍 Testing: \"{prompt}\"")
            response = await router.route(prompt)
            print(f"   Agent: {response.agent_type}")
            print(f"   Intent: {response.intent_detected.value}")
            print(f"   Response: {response.content[:100]}...")
        
        # Print analytics
        analytics = router.get_routing_analytics()
        print(f"\n📊 Routing Analytics:")
        print(f"   Total routes: {analytics['total_routes']}")
        print(f"   Intent distribution: {analytics['intent_distribution']}")
    
    # Run test
    asyncio.run(test_router())
