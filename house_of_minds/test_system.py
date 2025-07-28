"""
House of Minds System Test Suite

Comprehensive testing for all components of the House of Minds system.
"""

import asyncio
import logging
import sys
import os
import json
from typing import Dict, Any, List
from datetime import datetime

# Add the house_of_minds directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all components
from config_manager import ConfigManager
from intent_classifier import IntentClassifier
from model_router import ModelRouter
from models.dolphin_interface import DolphinInterface
from models.kimi_interface import KimiInterface
from models.memory_handler import MemoryHandler
from core.openrouter_gateway import OpenRouterGateway
from core.n8n_client import N8NClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HouseOfMindsTestSuite:
    """Comprehensive test suite for the House of Minds system."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.config_manager = None
        self.intent_classifier = None
        self.model_router = None
        self.components = {}
        self.test_results = {}
        
        logger.info("🧪 House of Minds Test Suite initialized")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        logger.info("🚀 Starting comprehensive House of Minds tests...")
        
        test_suite = {
            'config_tests': await self._test_configuration(),
            'component_tests': await self._test_components(),
            'integration_tests': await self._test_integrations(),
            'routing_tests': await self._test_routing(),
            'memory_tests': await self._test_memory(),
            'end_to_end_tests': await self._test_end_to_end()
        }
        
        # Calculate overall results
        total_tests = sum(len(results) for results in test_suite.values())
        passed_tests = sum(
            sum(1 for result in results.values() if result.get('passed', False))
            for results in test_suite.values()
        )
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
            'test_details': test_suite
        }
        
        logger.info(f"✅ Test suite completed: {passed_tests}/{total_tests} tests passed ({summary['success_rate']}%)")
        return summary
    
    async def _test_configuration(self) -> Dict[str, Any]:
        """Test configuration management."""
        logger.info("🔧 Testing configuration management...")
        
        tests = {}
        
        # Test 1: Configuration loading
        try:
            self.config_manager = ConfigManager()
            tests['config_loading'] = {
                'passed': True,
                'message': 'Configuration loaded successfully',
                'details': {
                    'config_path': self.config_manager.config_path,
                    'models_count': len(self.config_manager.models),
                    'services_count': len(self.config_manager.services)
                }
            }
        except Exception as e:
            tests['config_loading'] = {
                'passed': False,
                'message': f'Configuration loading failed: {e}',
                'details': {'error': str(e)}
            }
        
        # Test 2: Configuration validation
        if self.config_manager:
            try:
                issues = self.config_manager.validate_configuration()
                tests['config_validation'] = {
                    'passed': len(issues) == 0,
                    'message': f'Configuration validation: {len(issues)} issues found',
                    'details': {'issues': issues}
                }
            except Exception as e:
                tests['config_validation'] = {
                    'passed': False,
                    'message': f'Configuration validation error: {e}',
                    'details': {'error': str(e)}
                }
        
        # Test 3: Model configurations
        if self.config_manager:
            try:
                enabled_models = self.config_manager.get_enabled_models()
                tests['model_configs'] = {
                    'passed': len(enabled_models) > 0,
                    'message': f'Found {len(enabled_models)} enabled models',
                    'details': {
                        'enabled_models': list(enabled_models.keys()),
                        'total_models': len(self.config_manager.models)
                    }
                }
            except Exception as e:
                tests['model_configs'] = {
                    'passed': False,
                    'message': f'Model configuration error: {e}',
                    'details': {'error': str(e)}
                }
        
        return tests
    
    async def _test_components(self) -> Dict[str, Any]:
        """Test individual components."""
        logger.info("🧩 Testing individual components...")
        
        tests = {}
        
        # Test 1: Intent Classifier
        try:
            self.intent_classifier = IntentClassifier()
            
            test_queries = [
                ("How are you today?", "conversation"),
                ("Create a plan for my vacation", "planning"),
                ("Write a Python function", "code"),
                ("What's the weather like?", "utility"),
                ("Analyze this data set", "analysis")
            ]
            
            correct_classifications = 0
            for query, expected_intent in test_queries:
                result = self.intent_classifier.classify_intent(query)
                if result['intent'] == expected_intent:
                    correct_classifications += 1
            
            accuracy = (correct_classifications / len(test_queries)) * 100
            
            tests['intent_classifier'] = {
                'passed': accuracy >= 60,  # 60% accuracy threshold
                'message': f'Intent classification accuracy: {accuracy:.1f}%',
                'details': {
                    'correct': correct_classifications,
                    'total': len(test_queries),
                    'accuracy': accuracy
                }
            }
            
        except Exception as e:
            tests['intent_classifier'] = {
                'passed': False,
                'message': f'Intent classifier test failed: {e}',
                'details': {'error': str(e)}
            }
        
        # Test 2: Memory Handler
        try:
            memory_config = self.config_manager.system_settings if self.config_manager else {}
            memory_handler = MemoryHandler(memory_config)
            
            # Test memory storage and retrieval
            memory_id = await memory_handler.store_memory(
                "Test memory content for House of Minds",
                metadata={'test': True},
                tags=['test'],
                importance=0.8
            )
            
            retrieved_memory = await memory_handler.get_memory(memory_id)
            
            tests['memory_handler'] = {
                'passed': retrieved_memory is not None,
                'message': 'Memory storage and retrieval successful',
                'details': {
                    'memory_id': memory_id,
                    'retrieved': retrieved_memory is not None
                }
            }
            
            self.components['memory_handler'] = memory_handler
            
        except Exception as e:
            tests['memory_handler'] = {
                'passed': False,
                'message': f'Memory handler test failed: {e}',
                'details': {'error': str(e)}
            }
        
        # Test 3: Dolphin Interface (if available)
        if self.config_manager:
            dolphin_config = self.config_manager.get_model_config('dolphin')
            if dolphin_config and dolphin_config.enabled:
                try:
                    dolphin = DolphinInterface(dolphin_config.__dict__)
                    health_ok = await dolphin.health_check()
                    
                    tests['dolphin_interface'] = {
                        'passed': health_ok,
                        'message': f'Dolphin interface health check: {"passed" if health_ok else "failed"}',
                        'details': {
                            'health_check': health_ok,
                            'endpoint': dolphin_config.endpoint
                        }
                    }
                    
                    if health_ok:
                        self.components['dolphin'] = dolphin
                        
                except Exception as e:
                    tests['dolphin_interface'] = {
                        'passed': False,
                        'message': f'Dolphin interface test failed: {e}',
                        'details': {'error': str(e)}
                    }
            else:
                tests['dolphin_interface'] = {
                    'passed': False,
                    'message': 'Dolphin not configured or disabled',
                    'details': {'configured': dolphin_config is not None}
                }
        
        # Test 4: Kimi Interface (if available)
        if self.config_manager:
            kimi_config = self.config_manager.get_model_config('kimi')
            if kimi_config and kimi_config.enabled:
                try:
                    kimi = KimiInterface(kimi_config.__dict__)
                    health_ok = await kimi.health_check()
                    
                    tests['kimi_interface'] = {
                        'passed': health_ok,
                        'message': f'Kimi interface health check: {"passed" if health_ok else "failed"}',
                        'details': {
                            'health_check': health_ok,
                            'endpoint': kimi_config.endpoint
                        }
                    }
                    
                    if health_ok:
                        self.components['kimi'] = kimi
                        
                except Exception as e:
                    tests['kimi_interface'] = {
                        'passed': False,
                        'message': f'Kimi interface test failed: {e}',
                        'details': {'error': str(e)}
                    }
            else:
                tests['kimi_interface'] = {
                    'passed': False,
                    'message': 'Kimi not configured or disabled',
                    'details': {'configured': kimi_config is not None}
                }
        
        return tests
    
    async def _test_integrations(self) -> Dict[str, Any]:
        """Test external service integrations."""
        logger.info("🔗 Testing external integrations...")
        
        tests = {}
        
        # Test 1: N8N Integration (if configured)
        if self.config_manager:
            n8n_config = self.config_manager.get_service_config('n8n')
            if n8n_config and n8n_config.enabled:
                try:
                    n8n_client = N8NClient(n8n_config.__dict__)
                    health_ok = await n8n_client.health_check()
                    
                    tests['n8n_integration'] = {
                        'passed': health_ok,
                        'message': f'N8N integration health check: {"passed" if health_ok else "failed"}',
                        'details': {
                            'health_check': health_ok,
                            'endpoint': n8n_config.endpoint
                        }
                    }
                    
                    if health_ok:
                        self.components['n8n'] = n8n_client
                        
                except Exception as e:
                    tests['n8n_integration'] = {
                        'passed': False,
                        'message': f'N8N integration test failed: {e}',
                        'details': {'error': str(e)}
                    }
            else:
                tests['n8n_integration'] = {
                    'passed': False,
                    'message': 'N8N not configured or disabled',
                    'details': {'configured': n8n_config is not None}
                }
        
        # Test 2: OpenRouter Gateway (if configured)
        if self.config_manager:
            openrouter_config = self.config_manager.get_service_config('openrouter')
            if openrouter_config and openrouter_config.enabled:
                try:
                    gateway = OpenRouterGateway(openrouter_config.__dict__)
                    health_ok = await gateway.health_check()
                    
                    tests['openrouter_integration'] = {
                        'passed': health_ok,
                        'message': f'OpenRouter integration health check: {"passed" if health_ok else "failed"}',
                        'details': {
                            'health_check': health_ok,
                            'endpoint': openrouter_config.endpoint
                        }
                    }
                    
                    if health_ok:
                        self.components['openrouter'] = gateway
                        
                except Exception as e:
                    tests['openrouter_integration'] = {
                        'passed': False,
                        'message': f'OpenRouter integration test failed: {e}',
                        'details': {'error': str(e)}
                    }
            else:
                tests['openrouter_integration'] = {
                    'passed': False,
                    'message': 'OpenRouter not configured or disabled',
                    'details': {'configured': openrouter_config is not None}
                }
        
        return tests
    
    async def _test_routing(self) -> Dict[str, Any]:
        """Test the model routing system."""
        logger.info("🚏 Testing model routing...")
        
        tests = {}
        
        # Test 1: Router initialization
        try:
            if self.config_manager and self.intent_classifier:
                router_config = {
                    'config_manager': self.config_manager,
                    'intent_classifier': self.intent_classifier,
                    'components': self.components
                }
                
                self.model_router = ModelRouter(router_config)
                
                tests['router_initialization'] = {
                    'passed': True,
                    'message': 'Model router initialized successfully',
                    'details': {
                        'handlers_count': len(self.model_router.handlers),
                        'available_handlers': list(self.model_router.handlers.keys())
                    }
                }
            else:
                tests['router_initialization'] = {
                    'passed': False,
                    'message': 'Cannot initialize router - missing dependencies',
                    'details': {
                        'config_manager': self.config_manager is not None,
                        'intent_classifier': self.intent_classifier is not None
                    }
                }
        except Exception as e:
            tests['router_initialization'] = {
                'passed': False,
                'message': f'Router initialization failed: {e}',
                'details': {'error': str(e)}
            }
        
        # Test 2: Route resolution
        if self.model_router:
            try:
                test_queries = [
                    "Hello, how are you?",
                    "Create a plan for my project",
                    "What's the weather like?",
                    "Analyze this data"
                ]
                
                successful_routes = 0
                for query in test_queries:
                    try:
                        result = await self.model_router.route_request(query)
                        if result and 'response' in result:
                            successful_routes += 1
                    except Exception as e:
                        logger.warning(f"Route test failed for '{query}': {e}")
                
                success_rate = (successful_routes / len(test_queries)) * 100
                
                tests['route_resolution'] = {
                    'passed': success_rate >= 25,  # At least 25% should work
                    'message': f'Route resolution success rate: {success_rate:.1f}%',
                    'details': {
                        'successful': successful_routes,
                        'total': len(test_queries),
                        'success_rate': success_rate
                    }
                }
                
            except Exception as e:
                tests['route_resolution'] = {
                    'passed': False,
                    'message': f'Route resolution test failed: {e}',
                    'details': {'error': str(e)}
                }
        
        return tests
    
    async def _test_memory(self) -> Dict[str, Any]:
        """Test memory operations."""
        logger.info("🧠 Testing memory operations...")
        
        tests = {}
        
        if 'memory_handler' in self.components:
            memory_handler = self.components['memory_handler']
            
            # Test 1: Memory storage and search
            try:
                # Store test memories
                memories = [
                    ("Python programming is fun", ["programming", "python"], 0.8),
                    ("Machine learning algorithms", ["ai", "ml"], 0.9),
                    ("House of Minds is an AI system", ["system", "ai"], 0.7)
                ]
                
                stored_ids = []
                for content, tags, importance in memories:
                    memory_id = await memory_handler.store_memory(
                        content, tags=tags, importance=importance
                    )
                    stored_ids.append(memory_id)
                
                # Test search
                search_results = await memory_handler.search_memories("programming")
                
                tests['memory_operations'] = {
                    'passed': len(search_results) > 0,
                    'message': f'Memory operations successful: {len(search_results)} search results',
                    'details': {
                        'stored_memories': len(stored_ids),
                        'search_results': len(search_results),
                        'memory_ids': stored_ids
                    }
                }
                
            except Exception as e:
                tests['memory_operations'] = {
                    'passed': False,
                    'message': f'Memory operations failed: {e}',
                    'details': {'error': str(e)}
                }
            
            # Test 2: Memory statistics
            try:
                stats = memory_handler.get_memory_statistics()
                
                tests['memory_statistics'] = {
                    'passed': stats['total_memories'] > 0,
                    'message': f'Memory statistics: {stats["total_memories"]} total memories',
                    'details': stats
                }
                
            except Exception as e:
                tests['memory_statistics'] = {
                    'passed': False,
                    'message': f'Memory statistics failed: {e}',
                    'details': {'error': str(e)}
                }
        else:
            tests['memory_not_available'] = {
                'passed': False,
                'message': 'Memory handler not available for testing',
                'details': {'reason': 'Component not initialized'}
            }
        
        return tests
    
    async def _test_end_to_end(self) -> Dict[str, Any]:
        """Test end-to-end scenarios."""
        logger.info("🎯 Testing end-to-end scenarios...")
        
        tests = {}
        
        if self.model_router:
            # Test 1: Complete conversation flow
            try:
                test_conversation = [
                    "Hi, I'm testing the House of Minds system",
                    "Can you help me create a simple plan?",
                    "What's the current time?"
                ]
                
                successful_responses = 0
                for i, message in enumerate(test_conversation):
                    try:
                        result = await self.model_router.route_request(message)
                        if result and result.get('response'):
                            successful_responses += 1
                            logger.info(f"E2E Test {i+1}: ✅ Got response")
                        else:
                            logger.warning(f"E2E Test {i+1}: ❌ No response")
                    except Exception as e:
                        logger.warning(f"E2E Test {i+1}: ❌ Error: {e}")
                
                success_rate = (successful_responses / len(test_conversation)) * 100
                
                tests['conversation_flow'] = {
                    'passed': success_rate >= 33,  # At least 1/3 should work
                    'message': f'Conversation flow success rate: {success_rate:.1f}%',
                    'details': {
                        'successful_responses': successful_responses,
                        'total_messages': len(test_conversation),
                        'success_rate': success_rate
                    }
                }
                
            except Exception as e:
                tests['conversation_flow'] = {
                    'passed': False,
                    'message': f'Conversation flow test failed: {e}',
                    'details': {'error': str(e)}
                }
            
            # Test 2: Intent routing coverage
            try:
                intent_tests = {
                    'conversation': "Hello, how are you doing today?",
                    'planning': "Help me plan a vacation to Japan",
                    'code': "Write a Python function to sort a list",
                    'analysis': "Analyze the pros and cons of remote work"
                }
                
                intent_results = {}
                for intent, query in intent_tests.items():
                    try:
                        result = await self.model_router.route_request(query)
                        intent_results[intent] = {
                            'success': result is not None and 'response' in result,
                            'handler': result.get('handler') if result else None
                        }
                    except Exception as e:
                        intent_results[intent] = {
                            'success': False,
                            'error': str(e)
                        }
                
                successful_intents = sum(1 for r in intent_results.values() if r['success'])
                coverage = (successful_intents / len(intent_tests)) * 100
                
                tests['intent_coverage'] = {
                    'passed': coverage >= 25,  # At least 25% coverage
                    'message': f'Intent routing coverage: {coverage:.1f}%',
                    'details': {
                        'intent_results': intent_results,
                        'successful_intents': successful_intents,
                        'total_intents': len(intent_tests),
                        'coverage': coverage
                    }
                }
                
            except Exception as e:
                tests['intent_coverage'] = {
                    'passed': False,
                    'message': f'Intent coverage test failed: {e}',
                    'details': {'error': str(e)}
                }
        else:
            tests['router_not_available'] = {
                'passed': False,
                'message': 'Model router not available for end-to-end testing',
                'details': {'reason': 'Router not initialized'}
            }
        
        return tests
    
    def save_test_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to a file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"house_of_minds_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Test results saved to {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save test results: {e}")

async def main():
    """Main test runner."""
    print("=" * 60)
    print("🏠 HOUSE OF MINDS - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    test_suite = HouseOfMindsTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Success Rate: {results['success_rate']}%")
        
        # Print detailed results
        print("\n" + "=" * 60)
        print("📋 DETAILED RESULTS")
        print("=" * 60)
        
        for test_category, tests in results['test_details'].items():
            print(f"\n🔍 {test_category.upper().replace('_', ' ')}:")
            for test_name, test_result in tests.items():
                status = "✅ PASS" if test_result['passed'] else "❌ FAIL"
                print(f"  {status} {test_name}: {test_result['message']}")
        
        # Save results
        test_suite.save_test_results(results)
        
        print("\n" + "=" * 60)
        print("🎉 Test suite completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
