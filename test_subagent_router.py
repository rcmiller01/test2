"""
Unit Tests for SubAgent Router System
Tests intent classification, routing logic, agent dispatching, and personality formatting
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Import our modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.subagent_router import (
    SubAgentRouter, IntentClassifier, IntentType, 
    AgentResponse, RoutingDecision
)
from backend.ai_reformulator import (
    PersonalityFormatter, ReformulationRequest, ReformulatedResponse,
    format_agent_response
)
from backend.agents.code_agent import CodeAgent
from backend.agents.creative_agent import CreativeAgent
from backend.agents.memory_agent import MemoryAgent

class TestIntentClassifier:
    """Test intent classification functionality"""
    
    def setup_method(self):
        self.classifier = IntentClassifier()
    
    def test_code_intent_detection(self):
        """Test detection of code-related intents"""
        test_cases = [
            ("Help me debug this Python function", IntentType.CODE),
            ("Write a function to calculate fibonacci", IntentType.CODE), 
            ("How do I implement a REST API?", IntentType.CODE),
            ("Fix this error: NameError", IntentType.CODE),
            ("Create a class for user management", IntentType.CODE),
            ("Optimize this database query", IntentType.CODE)
        ]
        
        for input_text, expected_intent in test_cases:
            intent, confidence = self.classifier.classify_intent(input_text)
            assert intent == expected_intent, f"Failed for: {input_text}"
            assert confidence > 0.3, f"Low confidence for: {input_text}"
    
    def test_creative_intent_detection(self):
        """Test detection of creative intents"""
        test_cases = [
            ("Write me a story about loss", IntentType.CREATIVE),
            ("What does the ocean symbolize?", IntentType.CREATIVE),
            ("Create a metaphor for growth", IntentType.CREATIVE),
            ("Paint me a picture with words", IntentType.CREATIVE),
            ("Tell me something beautiful", IntentType.CREATIVE),
            ("Imagine a world where...", IntentType.CREATIVE)
        ]
        
        for input_text, expected_intent in test_cases:
            intent, confidence = self.classifier.classify_intent(input_text)
            assert intent == expected_intent, f"Failed for: {input_text}"
            assert confidence > 0.3, f"Low confidence for: {input_text}"
    
    def test_memory_intent_detection(self):
        """Test detection of memory-related intents"""
        test_cases = [
            ("Do you remember our conversation yesterday?", IntentType.MEMORY),
            ("What did we talk about last time?", IntentType.MEMORY),
            ("Recall our previous discussion", IntentType.MEMORY),
            ("What's our story so far?", IntentType.MEMORY),
            ("Continue from where we left off", IntentType.MEMORY),
            ("What happened in our past interactions?", IntentType.MEMORY)
        ]
        
        for input_text, expected_intent in test_cases:
            intent, confidence = self.classifier.classify_intent(input_text)
            assert intent == expected_intent, f"Failed for: {input_text}"
            assert confidence > 0.3, f"Low confidence for: {input_text}"
    
    def test_ritual_intent_detection(self):
        """Test detection of ritual/symbolic intents"""
        test_cases = [
            ("Create a ritual for new beginnings", IntentType.RITUAL),
            ("Help me design a sacred ceremony", IntentType.RITUAL),
            ("What would be a meaningful practice?", IntentType.RITUAL),
            ("Create a blessing for this transition", IntentType.RITUAL),
            ("Design a meditation practice", IntentType.RITUAL)
        ]
        
        for input_text, expected_intent in test_cases:
            intent, confidence = self.classifier.classify_intent(input_text)
            assert intent == expected_intent, f"Failed for: {input_text}"
            assert confidence > 0.3, f"Low confidence for: {input_text}"
    
    def test_emotional_intent_detection(self):
        """Test detection of emotional intents"""
        test_cases = [
            ("I'm feeling overwhelmed and need support", IntentType.EMOTIONAL),
            ("My heart is heavy today", IntentType.EMOTIONAL),
            ("I need comfort and understanding", IntentType.EMOTIONAL),
            ("Help me process these feelings", IntentType.EMOTIONAL),
            ("I'm struggling emotionally", IntentType.EMOTIONAL)
        ]
        
        for input_text, expected_intent in test_cases:
            intent, confidence = self.classifier.classify_intent(input_text)
            assert intent == expected_intent, f"Failed for: {input_text}"
            assert confidence > 0.3, f"Low confidence for: {input_text}"
    
    def test_context_influence_on_classification(self):
        """Test how context influences intent classification"""
        
        # Test mood influence
        context_anxious = {"mood": "anxious"}
        intent, confidence = self.classifier.classify_intent("I need help", context_anxious)
        assert intent == IntentType.EMOTIONAL
        
        # Test conversation depth influence
        context_deep = {"conversation_depth": 0.9}
        intent, confidence = self.classifier.classify_intent("Tell me about connection", context_deep)
        assert intent in [IntentType.RITUAL, IntentType.SYMBOLIC, IntentType.CREATIVE]
    
    def test_fallback_to_conversational(self):
        """Test fallback to conversational for unclear intents"""
        unclear_inputs = [
            "Hello",
            "Hmm",
            "Not sure what to ask",
            "Random thoughts"
        ]
        
        for input_text in unclear_inputs:
            intent, confidence = self.classifier.classify_intent(input_text)
            assert intent == IntentType.CONVERSATIONAL

class TestSubAgentRouter:
    """Test the main routing system"""
    
    def setup_method(self):
        self.router = SubAgentRouter()
    
    @pytest.mark.asyncio
    async def test_code_agent_routing(self):
        """Test routing to code agent"""
        response = await self.router.route(
            "Help me implement a binary search algorithm",
            {"project_type": "python"}
        )
        
        assert response.agent_type == "code"
        assert response.intent_detected == IntentType.CODE
        assert "implementation" in response.content.lower() or "algorithm" in response.content.lower()
        assert response.confidence > 0.3
    
    @pytest.mark.asyncio
    async def test_creative_agent_routing(self):
        """Test routing to creative agent"""
        response = await self.router.route(
            "Create a metaphor for transformation",
            {"mood": "contemplative"}
        )
        
        assert response.agent_type == "creative"
        assert response.intent_detected == IntentType.CREATIVE
        assert len(response.content) > 50  # Should be substantial creative content
        assert response.confidence > 0.3
    
    @pytest.mark.asyncio
    async def test_memory_agent_routing(self):
        """Test routing to memory agent"""
        context = {
            "conversation_history": ["Previous exchange about growth"],
            "total_interactions": 5
        }
        
        response = await self.router.route(
            "Do you remember what we discussed about personal growth?",
            context
        )
        
        assert response.agent_type == "memory"
        assert response.intent_detected == IntentType.MEMORY
        assert "remember" in response.content.lower() or "conversation" in response.content.lower()
    
    @pytest.mark.asyncio
    async def test_conversational_fallback(self):
        """Test fallback to conversational handling"""
        response = await self.router.route(
            "I'm feeling a bit lost today",
            {"mood": "sad"}
        )
        
        assert response.agent_type == "conversational"
        assert response.intent_detected == IntentType.EMOTIONAL
        assert len(response.content) > 30  # Should provide meaningful response
    
    @pytest.mark.asyncio
    async def test_routing_with_agent_unavailable(self):
        """Test behavior when preferred agent is unavailable"""
        # Mock an unavailable agent
        original_agents = self.router.agents.copy()
        self.router.agents["code"] = None
        
        response = await self.router.route(
            "Help me debug this code",
            {"project_type": "python"}
        )
        
        # Should fallback to conversational
        assert response.agent_type == "conversational"
        
        # Restore original agents
        self.router.agents = original_agents
    
    @pytest.mark.asyncio
    async def test_performance_tracking(self):
        """Test performance metrics tracking"""
        initial_metrics = len(self.router.agent_performance)
        
        await self.router.route("Test message", {})
        
        # Should have updated performance metrics
        assert len(self.router.agent_performance) >= initial_metrics
        
        # Check metrics structure
        for agent_name, metrics in self.router.agent_performance.items():
            assert "total_requests" in metrics
            assert "successful_requests" in metrics
            assert "success_rate" in metrics
            assert "avg_response_time" in metrics
    
    def test_routing_analytics(self):
        """Test routing analytics functionality"""
        analytics = self.router.get_routing_analytics()
        
        required_keys = [
            "total_routes", "intent_distribution", "agent_performance", 
            "available_agents", "recent_decisions"
        ]
        
        for key in required_keys:
            assert key in analytics
        
        assert isinstance(analytics["available_agents"], list)
        assert isinstance(analytics["intent_distribution"], dict)

class TestAgents:
    """Test individual agent functionality"""
    
    @pytest.mark.asyncio
    async def test_code_agent_functionality(self):
        """Test CodeAgent processing"""
        agent = CodeAgent()
        
        test_cases = [
            ("Implement a function to reverse a string", "implementation_request"),
            ("Debug this error: IndexError", "debug_request"),
            ("Explain how binary search works", "explanation_request"),
            ("Optimize this sorting algorithm", "optimization_request")
        ]
        
        for prompt, expected_type in test_cases:
            response = await agent.process(prompt, {"project_type": "python"})
            
            assert isinstance(response, str)
            assert len(response) > 50  # Should provide substantial response
            
            # Check that it detected the right request type
            detected_type = agent._analyze_code_request(prompt)
            assert detected_type == expected_type
    
    @pytest.mark.asyncio 
    async def test_creative_agent_functionality(self):
        """Test CreativeAgent processing"""
        agent = CreativeAgent()
        
        test_cases = [
            ("Write a story about courage", "storytelling"),
            ("What does the mountain symbolize?", "symbolic_interpretation"),
            ("Create a ritual for healing", "ritual_creation"),
            ("Describe the feeling of dawn", "aesthetic_description")
        ]
        
        for prompt, expected_type in test_cases:
            response = await agent.process(prompt, {"mood": "contemplative"})
            
            assert isinstance(response, str)
            assert len(response) > 100  # Creative responses should be substantial
            
            # Check that it detected the right creative type
            detected_type = agent._analyze_creative_request(prompt)
            assert detected_type == expected_type
    
    @pytest.mark.asyncio
    async def test_memory_agent_functionality(self):
        """Test MemoryAgent processing"""
        agent = MemoryAgent()
        
        context = {
            "conversation_history": ["We talked about growth", "Discussed challenges"],
            "total_interactions": 10,
            "significant_moments": ["Deep conversation about purpose"]
        }
        
        test_cases = [
            ("What did we discuss last time?", "direct_recall"),
            ("Tell me our story so far", "narrative_continuity"),
            ("How has our relationship evolved?", "relationship_history"),
            ("What patterns do you notice?", "pattern_recognition")
        ]
        
        for prompt, expected_type in test_cases:
            response = await agent.process(prompt, context)
            
            assert isinstance(response, str)
            assert len(response) > 80  # Memory responses should be thoughtful
            
            # Check that it detected the right memory type
            detected_type = agent._analyze_memory_request(prompt)
            assert detected_type == expected_type

class TestPersonalityFormatter:
    """Test personality formatting functionality"""
    
    def setup_method(self):
        self.formatter = PersonalityFormatter()
    
    @pytest.mark.asyncio
    async def test_code_response_formatting(self):
        """Test formatting of code agent responses"""
        original_response = """Here's a Python function:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

This uses recursion to calculate Fibonacci numbers."""
        
        request = ReformulationRequest(
            original_response=original_response,
            agent_type="code",
            intent_detected="implementation_request",
            user_context={"mood": "neutral", "conversation_depth": 0.4},
            personality_context={}
        )
        
        result = await self.formatter.format(request)
        
        assert isinstance(result, ReformulatedResponse)
        assert len(result.content) > len(original_response)  # Should add personality
        assert result.emotional_tone in ["grounded_wisdom", "patient_guidance"]
        assert result.reformulation_confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_creative_response_formatting(self):
        """Test formatting of creative agent responses"""
        original_response = "The ocean represents the unconscious mind, vast and mysterious."
        
        request = ReformulationRequest(
            original_response=original_response,
            agent_type="creative",
            intent_detected="symbolic_interpretation",
            user_context={"mood": "contemplative", "conversation_depth": 0.8},
            personality_context={}
        )
        
        result = await self.formatter.format(request)
        
        assert isinstance(result, ReformulatedResponse)
        assert "ocean" in result.content.lower()
        assert result.emotional_tone in ["intimate_guidance", "soulful_artistry"]
        assert "✨" in result.content or result.content.endswith("...")  # Should add creative touches
    
    @pytest.mark.asyncio
    async def test_emotional_filtering(self):
        """Test emotional state filtering"""
        original_response = "Here's how to solve this problem."
        
        # Test anxious mood filtering
        request = ReformulationRequest(
            original_response=original_response,
            agent_type="code",
            intent_detected="implementation_request",
            user_context={"mood": "anxious", "conversation_depth": 0.3},
            personality_context={}
        )
        
        result = await self.formatter.format(request)
        
        # Should add gentle, supportive language
        assert "time" in result.content.lower() or "gentle" in result.content.lower()
        assert result.emotional_tone == "gentle_presence"
    
    @pytest.mark.asyncio
    async def test_personality_evolution_integration(self):
        """Test integration with personality evolution"""
        # Mock personality evolution with specific traits
        mock_personality = Mock()
        mock_personality.get_personality_modifier.return_value = 0.8
        
        formatter = PersonalityFormatter(mock_personality)
        
        request = ReformulationRequest(
            original_response="Basic response",
            agent_type="conversational",
            intent_detected="emotional",
            user_context={"mood": "contemplative"},
            personality_context={}
        )
        
        result = await formatter.format(request)
        
        # Should call personality evolution for modifiers
        assert mock_personality.get_personality_modifier.called
        assert len(result.personality_adjustments) > 0
    
    @pytest.mark.asyncio
    async def test_convenience_function(self):
        """Test the standalone formatting function"""
        result = await format_agent_response(
            original_response="Test response",
            agent_type="creative",
            intent_detected="storytelling",
            user_context={"mood": "inspired", "conversation_depth": 0.6}
        )
        
        assert isinstance(result, str)
        assert len(result) > len("Test response")

class TestIntegration:
    """Test full system integration"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test complete request -> route -> format pipeline"""
        router = SubAgentRouter()
        formatter = PersonalityFormatter()
        
        # Test code request pipeline
        user_input = "Help me implement a sorting algorithm in Python"
        context = {"mood": "focused", "project_type": "python"}
        
        # Step 1: Route to agent
        agent_response = await router.route(user_input, context)
        
        # Step 2: Format response
        format_request = ReformulationRequest(
            original_response=agent_response.content,
            agent_type=agent_response.agent_type,
            intent_detected=agent_response.intent_detected.value,
            user_context=context,
            personality_context={}
        )
        
        final_response = await formatter.format(format_request)
        
        # Verify pipeline worked
        assert agent_response.agent_type == "code"
        assert agent_response.intent_detected == IntentType.CODE
        assert final_response.reformulation_confidence > 0.5
        assert len(final_response.content) > len(agent_response.content)
    
    @pytest.mark.asyncio
    async def test_error_handling_and_fallbacks(self):
        """Test system behavior under error conditions"""
        router = SubAgentRouter()
        
        # Test with malformed input
        try:
            response = await router.route("", {})
            assert response.agent_type == "conversational"  # Should fallback gracefully
        except Exception as e:
            pytest.fail(f"Router should handle empty input gracefully: {e}")
        
        # Test with very long input
        long_input = "A" * 10000
        response = await router.route(long_input, {})
        assert isinstance(response, AgentResponse)
    
    def test_system_capabilities_reporting(self):
        """Test that all components report their capabilities correctly"""
        router = SubAgentRouter()
        formatter = PersonalityFormatter()
        
        # Test router analytics
        analytics = router.get_routing_analytics()
        assert "available_agents" in analytics
        
        # Test individual agent capabilities
        for agent_name, agent in router.agents.items():
            if agent is not None:
                capabilities = agent.get_capabilities()
                assert "agent_type" in capabilities
                assert "specialties" in capabilities
        
        # Test formatter capabilities
        profile = formatter.get_current_personality_profile()
        assert isinstance(profile, dict)
        assert "tenderness" in profile
        assert "emotional_openness" in profile

# Pytest configuration
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v", "--tb=short"])
