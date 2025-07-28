"""
True Recall + Dolphin Integration Demo

Demonstration of the complete True Recall memory system integrated
with the Dolphin AI companion interface.
"""

import asyncio
import logging
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the house_of_minds directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def demo_memory_integration():
    """Demonstrate the integrated True Recall + Dolphin system."""
    
    print("🧠🐬 True Recall + Dolphin Integration Demo")
    print("=" * 60)
    
    try:
        # Import the integrated Dolphin interface
        from house_of_minds.models.dolphin_interface import DolphinInterface
        from house_of_minds.memory.recall_engine import RecallEngine
        
        # Configuration for Dolphin with memory
        config = {
            'ollama_url': 'http://localhost:11434',
            'model_name': 'dolphin-mixtral',
            'temperature': 0.7,
            'emotional_awareness': True,
            'memory': {
                'storage_path': 'demo_data/dolphin_demo_memories.json',
                'auto_reflect': True
            }
        }
        
        # Initialize Dolphin with memory
        print("🚀 Initializing Dolphin with True Recall memory system...")
        dolphin = DolphinInterface(config)
        
        if not dolphin.memory_enabled:
            print("⚠️  Memory system not available - continuing with basic demo")
        else:
            print("✅ Memory system successfully integrated!")
        
        # Simulate conversation with memory
        print("\n📱 Simulating conversation with memory...")
        
        conversations = [
            {
                'user': "Hi Dolphin! I'm excited to learn about machine learning today.",
                'context': {'user_id': 'demo_user', 'session_id': 'demo_session_1'}
            },
            {
                'user': "Can you explain what neural networks are?",
                'context': {'user_id': 'demo_user', 'session_id': 'demo_session_1'}
            },
            {
                'user': "That's fascinating! I want to build my own neural network.",
                'context': {'user_id': 'demo_user', 'session_id': 'demo_session_1'}
            }
        ]
        
        # Process conversations (if Ollama is available)
        print("\n💬 Processing demo conversations...")
        
        for i, conv in enumerate(conversations, 1):
            print(f"\n--- Conversation {i} ---")
            print(f"User: {conv['user']}")
            
            try:
                # Check if Dolphin is available
                if await dolphin.health_check():
                    response = await dolphin.generate_response(conv['user'], conv['context'])
                    print(f"Dolphin: {response}")
                else:
                    print("Dolphin: [Ollama not available - simulating response storage]")
                    # Still store in memory for demo
                    if dolphin.memory_enabled:
                        await dolphin._store_user_memory(conv['user'], conv['context'])
                        await dolphin._store_dolphin_memory(
                            "I'd love to help you learn about that! [Demo response]",
                            conv['user'],
                            conv['context']
                        )
            
            except Exception as e:
                print(f"Response generation failed: {e}")
                # Continue with memory demo
        
        # Demonstrate memory capabilities
        if dolphin.memory_enabled:
            print("\n🧠 Demonstrating memory capabilities...")
            
            # Memory search
            print("\n🔍 Searching memories for 'neural networks'...")
            memories = await dolphin.search_memories("neural networks", limit=3)
            
            if memories:
                for i, memory in enumerate(memories, 1):
                    content = memory.get('content', '')[:100] + ('...' if len(memory.get('content', '')) > 100 else '')
                    actor = memory.get('actor', 'unknown')
                    timestamp = memory.get('timestamp', '')
                    print(f"  {i}. [{actor}] {content}")
            else:
                print("  No memories found (expected for demo)")
            
            # Memory statistics
            print("\n📊 Memory system statistics:")
            stats = dolphin.get_memory_statistics()
            
            if 'error' not in stats:
                storage_stats = stats.get('storage', {})
                runtime_stats = stats.get('runtime', {})
                
                print(f"  Total memories: {storage_stats.get('total_events', 0)}")
                print(f"  Storage size: {storage_stats.get('file_size_mb', 0)} MB")
                print(f"  Uptime: {runtime_stats.get('uptime_hours', 0):.1f} hours")
                print(f"  Processing errors: {runtime_stats.get('processing_errors', 0)}")
            else:
                print(f"  Error: {stats.get('error')}")
            
            # Daily reflection
            print("\n📔 Generating daily reflection...")
            reflection = await dolphin.get_daily_reflection()
            
            if 'error' not in reflection:
                print(f"  Date: {reflection.get('date')}")
                print(f"  Events: {reflection.get('event_count', 0)}")
                print(f"  Emotional tone: {reflection.get('emotional_tone', {}).get('tone', 'unknown')}")
                
                key_events = reflection.get('key_events', [])
                if key_events:
                    print(f"  Key events: {len(key_events)}")
                    for event in key_events[:2]:
                        content = event.get('content', '')[:80] + ('...' if len(event.get('content', '')) > 80 else '')
                        print(f"    - {content}")
            else:
                print(f"  Error: {reflection.get('error')}")
        
        # Test individual memory components
        print("\n🔧 Testing individual memory components...")
        
        # Test emotion tagger
        try:
            from house_of_minds.memory.emotion_tagger import EmotionTagger
            emotion_tagger = EmotionTagger()
            
            test_text = "I'm really excited about learning artificial intelligence!"
            emotion_result = emotion_tagger.analyze_text(test_text)
            
            print(f"\n😊 Emotion Analysis for: '{test_text}'")
            print(f"  Primary emotion: {emotion_result.get('primary_emotion')}")
            print(f"  Emotional intensity: {emotion_result.get('emotional_intensity'):.2f}")
            print(f"  Sentiment polarity: {emotion_result.get('sentiment_polarity'):.2f}")
            print(f"  Emotional fingerprint: {emotion_result.get('emotional_fingerprint')}")
            
        except Exception as e:
            print(f"  Emotion tagger test failed: {e}")
        
        # Test salience scorer
        try:
            from house_of_minds.memory.salience_scoring import SalienceScorer
            salience_scorer = SalienceScorer()
            
            test_event = {
                'id': 'test_event',
                'content': 'This is extremely important! Please remember this forever.',
                'actor': 'user',
                'timestamp': datetime.now().isoformat(),
                'emotion_analysis': emotion_result
            }
            
            salience_result = salience_scorer.calculate_salience(test_event)
            
            print(f"\n📊 Salience Analysis for important event:")
            print(f"  Salience score: {salience_result.get('salience_score'):.3f}")
            print(f"  Salience level: {salience_result.get('salience_level')}")
            print(f"  Key factors: {', '.join(salience_result.get('scoring_factors', []))}")
            
        except Exception as e:
            print(f"  Salience scorer test failed: {e}")
        
        # Test memory graph
        try:
            from house_of_minds.memory.memory_graph import MemoryGraph
            memory_graph = MemoryGraph()
            
            # Add some test events
            test_events = [
                {
                    'id': 'graph_test_1',
                    'content': 'What is machine learning?',
                    'actor': 'user',
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'id': 'graph_test_2',
                    'content': 'Machine learning is a subset of artificial intelligence',
                    'actor': 'dolphin',
                    'timestamp': (datetime.now() + timedelta(minutes=1)).isoformat()
                }
            ]
            
            for event in test_events:
                memory_graph.add_event(event)
            
            # Get graph statistics
            graph_stats = memory_graph.get_graph_statistics()
            
            print(f"\n🕸️  Memory Graph Statistics:")
            print(f"  Total nodes: {graph_stats.get('total_nodes', 0)}")
            print(f"  Total edges: {graph_stats.get('total_edges', 0)}")
            print(f"  Graph density: {graph_stats.get('graph_density', 0):.3f}")
            
            # Find related events
            related = memory_graph.get_related_events('graph_test_1', max_results=3)
            print(f"  Related events: {len(related)}")
            
        except Exception as e:
            print(f"  Memory graph test failed: {e}")
        
        # Test reflection agent
        try:
            from house_of_minds.memory.reflection_agent import ReflectionAgent
            reflection_agent = ReflectionAgent()
            
            # Create sample events
            sample_events = [
                {
                    'id': 'reflection_test_1',
                    'content': 'Started learning about neural networks today',
                    'actor': 'user',
                    'timestamp': datetime.now().isoformat(),
                    'emotion_analysis': {'primary_emotion': 'curiosity', 'emotional_intensity': 0.7},
                    'salience_analysis': {'salience_score': 0.8}
                },
                {
                    'id': 'reflection_test_2',
                    'content': 'Had a great conversation about AI ethics',
                    'actor': 'user',
                    'timestamp': (datetime.now() + timedelta(hours=1)).isoformat(),
                    'emotion_analysis': {'primary_emotion': 'joy', 'emotional_intensity': 0.6},
                    'salience_analysis': {'salience_score': 0.7}
                }
            ]
            
            # Generate reflection
            daily_reflection = reflection_agent.generate_daily_reflection(sample_events, date.today())
            
            print(f"\n📔 Reflection Agent Test:")
            print(f"  Events analyzed: {daily_reflection.get('event_count')}")
            print(f"  Emotional tone: {daily_reflection.get('emotional_tone', {}).get('tone')}")
            print(f"  Key events found: {len(daily_reflection.get('key_events', []))}")
            print(f"  Learning moments: {len(daily_reflection.get('learning_moments', []))}")
            
        except Exception as e:
            print(f"  Reflection agent test failed: {e}")
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        dolphin.close()
        
        print("\n✅ Demo completed successfully!")
        print("\nNext steps for integration:")
        print("1. Install dependencies: pip install textblob scikit-learn tinydb")
        print("2. Configure Ollama with Dolphin model")
        print("3. Update Dolphin interface configuration")
        print("4. Test with real conversations")
        print("5. Monitor memory growth and performance")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("pip install textblob scikit-learn tinydb")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.exception("Demo error details:")

def demo_memory_storage():
    """Demonstrate basic memory storage and retrieval."""
    print("\n💾 Testing basic memory storage...")
    
    try:
        from house_of_minds.memory.recall_engine import quick_memory_store, quick_memory_recall
        
        # Store some test memories
        test_memories = [
            "I love learning about artificial intelligence and machine learning",
            "Had a productive meeting about the new project today",
            "Discovered a fascinating research paper on neural networks",
            "Feeling excited about implementing a new algorithm"
        ]
        
        print("Storing test memories...")
        for content in test_memories:
            result = quick_memory_store(content, "demo_user", "demo_data/quick_test.json")
            print(f"  Stored: {result.get('id')} - {content[:50]}...")
        
        # Recall memories
        print("\nRecalling memories about 'artificial intelligence'...")
        recalled = quick_memory_recall("artificial intelligence", limit=3, storage_path="demo_data/quick_test.json")
        
        for i, memory in enumerate(recalled, 1):
            content = memory.get('content', '')
            salience = memory.get('salience_analysis', {}).get('salience_score', 0)
            emotion = memory.get('emotion_analysis', {}).get('primary_emotion', 'unknown')
            
            print(f"  {i}. [{emotion}] {content}")
            print(f"     Salience: {salience:.3f}")
        
        print(f"\nFound {len(recalled)} relevant memories")
        
    except Exception as e:
        print(f"❌ Memory storage test failed: {e}")

if __name__ == "__main__":
    print("🎯 Choose demo mode:")
    print("1. Full integration demo (requires all dependencies)")
    print("2. Basic memory storage demo")
    print("3. Both demos")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        asyncio.run(demo_memory_integration())
    
    if choice in ['2', '3']:
        demo_memory_storage()
    
    if choice not in ['1', '2', '3']:
        print("Invalid choice. Running full demo...")
        asyncio.run(demo_memory_integration())
