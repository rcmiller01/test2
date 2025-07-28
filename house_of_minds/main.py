#!/usr/bin/env python3
"""
House of Minds - Main System Entry Point

This module serves as the primary testing interface for the House of Minds
multi-agent AI system. It demonstrates task routing between local models
(Dolphin, Kimi) and cloud services (OpenRouter, n8n).

Usage:
    python main.py
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from model_router import ModelRouter
from intent_classifier import IntentClassifier
from config.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('house_of_minds.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class HouseOfMinds:
    """
    Main orchestrator for the House of Minds AI system.
    
    Coordinates between different AI agents and services to handle
    various types of user requests through intelligent routing.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the House of Minds system."""
        self.config = ConfigManager(config_path)
        self.intent_classifier = IntentClassifier()
        self.model_router = ModelRouter(self.config)
        self.session_id = f"session_{int(datetime.now().timestamp())}"
        
        logger.info("🧠 House of Minds system initialized")
        
    async def process_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user request through the complete House of Minds pipeline.
        
        Args:
            user_input: The user's request or query
            context: Optional context from previous interactions
            
        Returns:
            Dict containing the response and metadata
        """
        try:
            # Step 1: Classify the intent
            logger.info(f"📥 Processing request: '{user_input[:50]}...'")
            intent_result = await self.intent_classifier.classify_intent(user_input, context)
            
            task_type = intent_result.get('task_type', 'conversation')
            confidence = intent_result.get('confidence', 0.0)
            
            logger.info(f"🎯 Intent classified: {task_type} (confidence: {confidence:.2f})")
            
            # Step 2: Route to appropriate model/service
            response = await self.model_router.route_request(
                user_input=user_input,
                task_type=task_type,
                context=context,
                intent_metadata=intent_result
            )
            
            # Step 3: Package the complete response
            result = {
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'user_input': user_input,
                'intent': intent_result,
                'response': response,
                'status': 'success'
            }
            
            logger.info(f"✅ Request processed successfully via {response.get('handler', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing request: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'user_input': user_input,
                'error': str(e),
                'status': 'error'
            }
    
    async def interactive_session(self):
        """Run an interactive session for testing the system."""
        print("\n🧠 Welcome to House of Minds Interactive Session")
        print("=" * 50)
        print("Type 'exit' to quit, 'status' for system status")
        print()
        
        context = {}
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'exit':
                    print("👋 Goodbye!")
                    break
                    
                if user_input.lower() == 'status':
                    status = await self.model_router.get_system_status()
                    print(f"System Status: {json.dumps(status, indent=2)}")
                    continue
                
                if not user_input:
                    continue
                
                # Process the request
                result = await self.process_request(user_input, context)
                
                if result['status'] == 'success':
                    response = result['response']
                    print(f"\n🤖 {response.get('handler', 'AI')}: {response.get('content', 'No response')}")
                    
                    # Update context for next interaction
                    context.update({
                        'last_intent': result['intent']['task_type'],
                        'last_handler': response.get('handler'),
                        'conversation_history': context.get('conversation_history', []) + [
                            {'user': user_input, 'ai': response.get('content', '')}
                        ]
                    })
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Session error: {e}")
                print(f"❌ Session error: {e}")

async def main():
    """Main function to demonstrate the House of Minds system."""
    
    # Test scenarios
    test_scenarios = [
        {
            "input": "Hello, how are you doing today?",
            "expected_type": "conversation"
        },
        {
            "input": "Can you help me plan a vacation to Japan?",
            "expected_type": "planning"
        },
        {
            "input": "Write a Python function to calculate fibonacci numbers",
            "expected_type": "code"
        },
        {
            "input": "Send an email to john@example.com about the meeting",
            "expected_type": "utility"
        },
        {
            "input": "What did we discuss about AI safety last week?",
            "expected_type": "memory"
        }
    ]
    
    print("🧠 House of Minds - System Initialization Test")
    print("=" * 60)
    
    # Initialize the system
    house = HouseOfMinds()
    
    print("\n📋 Running test scenarios...")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 Test {i}: {scenario['input']}")
        print("-" * 40)
        
        result = await house.process_request(scenario['input'])
        
        if result['status'] == 'success':
            intent = result['intent']
            response = result['response']
            
            print(f"Intent: {intent['task_type']} (confidence: {intent['confidence']:.2f})")
            print(f"Handler: {response.get('handler', 'Unknown')}")
            print(f"Response: {response.get('content', 'No content')[:100]}...")
            
            # Check if intent matches expectation
            if intent['task_type'] == scenario['expected_type']:
                print("✅ Intent classification correct")
            else:
                print(f"⚠️ Intent mismatch - expected: {scenario['expected_type']}, got: {intent['task_type']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print("\n🎮 Starting interactive session...")
    print("(You can test the system interactively)")
    
    # Start interactive session
    await house.interactive_session()

if __name__ == "__main__":
    asyncio.run(main())
