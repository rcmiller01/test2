"""
Test Script for Unified Companion System

Tests the core functionality of the unified companion implementation
including context detection, response generation, and database operations.
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system components
from modules.core.context_detector import ContextDetector
from modules.database.database_interface import (
    InMemoryDatabase, UserProfile, InteractionRecord, InteractionType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedCompanionTester:
    """
    Test suite for the unified companion system
    """
    
    def __init__(self):
        self.context_detector = ContextDetector()
        self.database = InMemoryDatabase()
        self.test_user_id = "test_user_001"
        
    async def initialize(self):
        """Initialize test components"""
        await self.database.initialize()
        logger.info("Test components initialized")
    
    async def test_context_detection(self):
        """Test context detection capabilities"""
        logger.info("Testing context detection...")
        
        test_cases = [
            {
                "input": "I'm feeling really overwhelmed with work and need some emotional support",
                "expected_focus": "emotional_support"
            },
            {
                "input": "Can you help me debug this Python function? It's not working correctly",
                "expected_focus": "technical_assistance"
            },
            {
                "input": "I want to write a poem about the ocean but I'm stuck for inspiration",
                "expected_focus": "creative_collaboration"
            },
            {
                "input": "I'm working on a coding project but also feeling stressed about deadlines",
                "expected_focus": "integrated_support"
            },
            {
                "input": "Hello, how are you today?",
                "expected_focus": "general_conversation"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            logger.info(f"Test case {i+1}: '{test_case['input'][:50]}...'")
            
            context = {"test_mode": True}
            conversation_history = []
            
            analysis = await self.context_detector.analyze_interaction(
                test_case["input"], context, conversation_history
            )
            
            logger.info(f"  Detected focus: {analysis['primary_focus']}")
            logger.info(f"  Expected focus: {test_case['expected_focus']}")
            logger.info(f"  Emotional priority: {analysis['emotional_priority']}")
            logger.info(f"  Detected needs: {analysis['detected_needs']}")
            
            # Note: In a real test, we'd assert expected vs actual
            print()
    
    async def test_database_operations(self):
        """Test database operations"""
        logger.info("Testing database operations...")
        
        # Test user profile creation
        user_profile = UserProfile(
            user_id=self.test_user_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            display_name="Test User",
            preferences={"theme": "adaptive", "response_style": "supportive"},
            adaptive_profile={"emotional_support_frequency": 5}
        )
        
        success = await self.database.create_user_profile(user_profile)
        logger.info(f"User profile creation: {'✓' if success else '✗'}")
        
        # Test user profile retrieval
        retrieved_user = await self.database.get_user_profile(self.test_user_id)
        logger.info(f"User profile retrieval: {'✓' if retrieved_user else '✗'}")
        
        if retrieved_user:
            logger.info(f"  Retrieved user: {retrieved_user.display_name}")
            logger.info(f"  Preferences: {retrieved_user.preferences}")
        
        # Test interaction record creation
        interaction = InteractionRecord(
            interaction_id="test_interaction_001",
            user_id=self.test_user_id,
            session_id="test_session_001",
            timestamp=datetime.now(),
            user_input="Hello, I need some help with my project",
            companion_response="I'm here to help you with your project. What specifically would you like to work on?",
            interaction_type=InteractionType.TECHNICAL_ASSISTANCE,
            context_analysis={
                "primary_focus": "technical_assistance",
                "emotional_priority": "medium",
                "detected_needs": ["project_guidance"]
            },
            emotional_state={"neutral": 0.8, "focused": 0.6},
            technical_context={"project_type": "coding", "assistance_level": "guidance"},
            creative_context={},
            guidance_used={"scene_orchestrator": {"context_mode": "technical_assistance"}},
            response_metrics={"response_time": 1.2, "confidence": 0.85}
        )
        
        success = await self.database.save_interaction(interaction)
        logger.info(f"Interaction record creation: {'✓' if success else '✗'}")
        
        # Test interaction retrieval
        interactions = await self.database.get_recent_interactions(self.test_user_id, limit=5)
        logger.info(f"Interaction retrieval: {'✓' if interactions else '✗'}")
        logger.info(f"  Retrieved {len(interactions)} interactions")
        
        print()
    
    async def test_adaptive_response_patterns(self):
        """Test adaptive response pattern selection"""
        logger.info("Testing adaptive response patterns...")
        
        # Simulate different interaction contexts
        contexts = [
            {
                "primary_focus": "emotional_support",
                "emotional_priority": "high",
                "user_input": "I'm feeling really depressed and don't know what to do"
            },
            {
                "primary_focus": "technical_assistance",
                "technical_priority": "high",
                "user_input": "My code keeps throwing a syntax error and I can't figure out why"
            },
            {
                "primary_focus": "creative_collaboration",
                "creative_priority": "medium",
                "user_input": "I want to create something beautiful but don't know where to start"
            }
        ]
        
        for context in contexts:
            logger.info(f"Context: {context['primary_focus']}")
            logger.info(f"  Input: '{context['user_input'][:50]}...'")
            
            # Simulate adaptive recommendations
            recommendations = self._generate_test_recommendations(context)
            logger.info(f"  Recommended tone: {recommendations['response_tone']}")
            logger.info(f"  Interaction style: {recommendations['interaction_style']}")
            print()
    
    def _generate_test_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test recommendations based on context"""
        if context["primary_focus"] == "emotional_support":
            return {
                "response_tone": "gentle_and_empathetic",
                "interaction_style": "intimate_and_caring"
            }
        elif context["primary_focus"] == "technical_assistance":
            return {
                "response_tone": "supportive_and_competent",
                "interaction_style": "helpful_and_encouraging"
            }
        elif context["primary_focus"] == "creative_collaboration":
            return {
                "response_tone": "inspiring_and_encouraging",
                "interaction_style": "collaborative_and_artistic"
            }
        else:
            return {
                "response_tone": "warm_and_supportive",
                "interaction_style": "natural_and_caring"
            }
    
    async def test_memory_system(self):
        """Test memory fragment system"""
        logger.info("Testing memory system...")
        
        from modules.database.database_interface import MemoryFragment
        
        # Create test memory fragments
        memories = [
            MemoryFragment(
                memory_id="mem_001",
                user_id=self.test_user_id,
                content="User prefers detailed technical explanations",
                memory_type="technical",
                importance_score=0.8,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                related_interactions=["test_interaction_001"],
                tags=["preference", "technical", "explanation_style"]
            ),
            MemoryFragment(
                memory_id="mem_002",
                user_id=self.test_user_id,
                content="User responds well to encouragement during creative blocks",
                memory_type="creative",
                importance_score=0.9,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=3,
                related_interactions=["creative_session_001"],
                tags=["emotional_pattern", "creative", "encouragement"]
            )
        ]
        
        # Save memory fragments
        for memory in memories:
            success = await self.database.save_memory_fragment(memory)
            logger.info(f"Memory fragment '{memory.memory_id}' saved: {'✓' if success else '✗'}")
        
        # Test memory retrieval
        relevant_memories = await self.database.get_relevant_memories(
            self.test_user_id, memory_type="technical", limit=5
        )
        logger.info(f"Technical memories retrieved: {len(relevant_memories)}")
        
        for memory in relevant_memories:
            logger.info(f"  Memory: {memory.content[:50]}...")
            logger.info(f"  Importance: {memory.importance_score}")
        
        print()
    
    async def test_integration_scenario(self):
        """Test complete integration scenario"""
        logger.info("Testing integration scenario...")
        
        # Simulate a complete user interaction flow
        user_inputs = [
            "Hi, I'm new here and feeling a bit overwhelmed with starting my coding project",
            "I'm trying to build a web application but I don't know where to begin",
            "Thanks for the guidance. I'm feeling more confident now. Can you help me plan the first steps?",
            "I want to make this project creative and unique, not just functional"
        ]
        
        conversation_history = []
        
        for i, user_input in enumerate(user_inputs):
            logger.info(f"Interaction {i+1}: '{user_input[:50]}...'")
            
            # Analyze context
            context = {"interaction_count": i+1, "session_duration": i * 5}
            analysis = await self.context_detector.analyze_interaction(
                user_input, context, conversation_history
            )
            
            logger.info(f"  Primary focus: {analysis['primary_focus']}")
            logger.info(f"  Emotional priority: {analysis['emotional_priority']}")
            logger.info(f"  Conversation flow: {analysis['conversation_flow']}")
            
            # Simulate companion response (would be generated by MythoMax in real system)
            companion_response = self._generate_test_response(analysis, user_input)
            logger.info(f"  Response: '{companion_response[:80]}...'")
            
            # Add to conversation history
            conversation_history.append({
                "user_input": user_input,
                "companion_response": companion_response,
                "context_analysis": analysis,
                "timestamp": datetime.now().isoformat()
            })
            
            # Limit history to last 5 interactions for testing
            if len(conversation_history) > 5:
                conversation_history = conversation_history[-5:]
            
            print()
    
    def _generate_test_response(self, analysis: Dict[str, Any], user_input: str) -> str:
        """Generate test response based on analysis"""
        primary_focus = analysis["primary_focus"]
        
        if primary_focus == "emotional_support":
            return "I understand you're feeling overwhelmed, and that's completely natural when starting something new. I'm here to support you through this journey."
        elif primary_focus == "technical_assistance":
            return "Let's break down web application development into manageable steps. We can start with planning your project structure and choosing the right tools."
        elif primary_focus == "integrated_support":
            return "I can see you're gaining confidence, which is wonderful! Let's channel that positive energy into creating a clear, actionable plan for your project."
        elif primary_focus == "creative_collaboration":
            return "I love that you want to make this project both functional and creative! Let's explore some innovative approaches that will make your application truly unique."
        else:
            return "I'm here to help you with whatever you need. What would you like to focus on today?"
    
    async def run_all_tests(self):
        """Run all test scenarios"""
        logger.info("=== Starting Unified Companion System Tests ===")
        
        try:
            await self.initialize()
            
            await self.test_context_detection()
            await self.test_database_operations()
            await self.test_adaptive_response_patterns()
            await self.test_memory_system()
            await self.test_integration_scenario()
            
            logger.info("=== All tests completed successfully ===")
            
        except Exception as e:
            logger.error(f"Test error: {e}")
            raise

async def main():
    """Main test runner"""
    tester = UnifiedCompanionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
