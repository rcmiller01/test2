"""
True Recall - Comprehensive Test Suite

Tests for all components of the True Recall memory system to ensure
proper functionality, integration, and error handling.
"""

import unittest
import tempfile
import shutil
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import sys
import os

# Add the house_of_minds directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import True Recall components
try:
    from memory.recall_engine import RecallEngine, create_recall_engine
    from memory.emotion_tagger import EmotionTagger
    from memory.salience_scoring import SalienceScorer
    from memory.memory_graph import MemoryGraph
    from memory.reflection_agent import ReflectionAgent
    from storage.memory_store import MemoryStore
except ImportError as e:
    print(f"Import error: {e}")
    print("Note: Some dependencies may be missing. Install with: pip install textblob scikit-learn tinydb")

class TestEmotionTagger(unittest.TestCase):
    """Test the emotion analysis system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tagger = EmotionTagger()
    
    def test_basic_emotion_detection(self):
        """Test basic emotion detection."""
        # Test positive emotion
        result = self.tagger.analyze_text("I am so happy and excited about this!")
        self.assertIn('joy', result['detected_emotions'])
        self.assertEqual(result['primary_emotion'], 'joy')
        self.assertGreater(result['sentiment_polarity'], 0)
        
        # Test negative emotion
        result = self.tagger.analyze_text("I feel really sad and disappointed")
        self.assertIn('sadness', result['detected_emotions'])
        self.assertEqual(result['primary_emotion'], 'sadness')
        self.assertLess(result['sentiment_polarity'], 0)
    
    def test_neutral_text(self):
        """Test neutral or empty text handling."""
        result = self.tagger.analyze_text("")
        self.assertEqual(result['primary_emotion'], None)
        self.assertEqual(result['emotional_fingerprint'], 'neutral')
        
        result = self.tagger.analyze_text("The weather is 72 degrees.")
        self.assertLess(result['emotional_intensity'], 0.3)
    
    def test_complex_emotions(self):
        """Test complex emotional expressions."""
        text = "I'm really excited about the opportunity but also nervous about the challenges"
        result = self.tagger.analyze_text(text)
        
        # Should detect multiple emotions
        emotions = result['detected_emotions']
        self.assertGreater(len(emotions), 1)
        self.assertIn('anticipation', emotions)
        self.assertIn('fear', emotions)
    
    def test_emotion_intensity(self):
        """Test emotional intensity calculation."""
        # High intensity
        result = self.tagger.analyze_text("I am EXTREMELY thrilled and absolutely ecstatic!!!")
        self.assertGreater(result['emotional_intensity'], 1.0)
        
        # Low intensity
        result = self.tagger.analyze_text("I'm somewhat pleased with the result")
        self.assertLess(result['emotional_intensity'], 0.8)
    
    def test_context_awareness(self):
        """Test context-aware emotion analysis."""
        context = {'speaker': 'user', 'hour': 23}
        result = self.tagger.analyze_text("I'm feeling tired", context)
        
        self.assertIsInstance(result, dict)
        self.assertIn('analyzed_at', result)


class TestSalienceScorer(unittest.TestCase):
    """Test the salience scoring system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scorer = SalienceScorer()
        
        # Create sample events
        self.sample_events = [
            {
                'id': 'event1',
                'content': 'Had a great conversation about machine learning',
                'actor': 'user',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'emotion_analysis': {
                    'emotional_intensity': 0.6,
                    'primary_emotion': 'joy',
                    'valence': 0.5
                }
            },
            {
                'id': 'event2',
                'content': 'Remember to call mom tomorrow',
                'actor': 'user',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'emotion_analysis': {
                    'emotional_intensity': 0.3,
                    'primary_emotion': 'anticipation',
                    'valence': 0.2
                }
            }
        ]
    
    def test_recency_scoring(self):
        """Test recency-based scoring."""
        # Recent event should score higher
        recent_event = {
            'id': 'recent',
            'timestamp': datetime.now().isoformat(),
            'content': 'Recent event'
        }
        
        old_event = {
            'id': 'old',
            'timestamp': (datetime.now() - timedelta(days=10)).isoformat(),
            'content': 'Old event'
        }
        
        recent_score = self.scorer.calculate_salience(recent_event)
        old_score = self.scorer.calculate_salience(old_event)
        
        self.assertGreater(recent_score['component_scores']['recency'], 
                          old_score['component_scores']['recency'])
    
    def test_emotional_scoring(self):
        """Test emotion-based scoring."""
        high_emotion_event = {
            'id': 'emotional',
            'content': 'Very emotional event',
            'emotion_analysis': {
                'emotional_intensity': 1.5,
                'primary_emotion': 'anger',
                'valence': -0.8,
                'arousal': 0.9
            }
        }
        
        low_emotion_event = {
            'id': 'neutral',
            'content': 'Neutral event',
            'emotion_analysis': {
                'emotional_intensity': 0.1,
                'primary_emotion': None,
                'valence': 0.0,
                'arousal': 0.0
            }
        }
        
        high_score = self.scorer.calculate_salience(high_emotion_event)
        low_score = self.scorer.calculate_salience(low_emotion_event)
        
        self.assertGreater(high_score['component_scores']['emotional'],
                          low_score['component_scores']['emotional'])
    
    def test_salience_levels(self):
        """Test salience level categorization."""
        high_salience_event = {
            'id': 'important',
            'content': 'This is extremely important and urgent! Remember this forever!',
            'actor': 'user',
            'timestamp': datetime.now().isoformat(),
            'emotion_analysis': {
                'emotional_intensity': 1.8,
                'primary_emotion': 'fear',
                'valence': -0.7,
                'arousal': 1.0
            }
        }
        
        result = self.scorer.calculate_salience(high_salience_event, self.sample_events)
        self.assertIn(result['salience_level'], ['high', 'critical'])
        self.assertGreater(result['salience_score'], 0.5)
    
    def test_frequency_analysis(self):
        """Test frequency-based scoring."""
        # Create events with repeated content
        frequent_events = [
            {'id': 'f1', 'content': 'machine learning discussion', 'actor': 'user', 
             'timestamp': (datetime.now() - timedelta(hours=i)).isoformat()}
            for i in range(1, 4)
        ]
        
        new_ml_event = {
            'id': 'new_ml',
            'content': 'Another machine learning conversation',
            'actor': 'user',
            'timestamp': datetime.now().isoformat()
        }
        
        result = self.scorer.calculate_salience(new_ml_event, frequent_events)
        self.assertIsInstance(result['component_scores']['frequency'], float)


class TestMemoryGraph(unittest.TestCase):
    """Test the memory graph relationship system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = MemoryGraph()
        
        # Add sample events
        self.events = [
            {
                'id': 'event1',
                'content': 'What is machine learning?',
                'actor': 'user',
                'timestamp': datetime.now().isoformat(),
                'emotion_analysis': {'primary_emotion': 'curiosity'}
            },
            {
                'id': 'event2',
                'content': 'Machine learning is a type of artificial intelligence',
                'actor': 'dolphin',
                'timestamp': (datetime.now() + timedelta(minutes=1)).isoformat(),
                'emotion_analysis': {'primary_emotion': 'joy'}
            },
            {
                'id': 'event3',
                'content': 'That makes sense! Can you tell me more about neural networks?',
                'actor': 'user',
                'timestamp': (datetime.now() + timedelta(minutes=2)).isoformat(),
                'emotion_analysis': {'primary_emotion': 'curiosity'}
            }
        ]
        
        for event in self.events:
            self.graph.add_event(event)
    
    def test_event_addition(self):
        """Test adding events to the graph."""
        self.assertEqual(len(self.graph.nodes), 3)
        self.assertIn('event1', self.graph.nodes)
        self.assertIn('event2', self.graph.nodes)
        self.assertIn('event3', self.graph.nodes)
    
    def test_relationship_discovery(self):
        """Test relationship discovery between events."""
        # Get related events for the first event
        related = self.graph.get_related_events('event1', max_depth=2, max_results=5)
        
        self.assertIsInstance(related, list)
        # Should find some relationships
        self.assertGreater(len(related), 0)
        
        # Check that related events have relationship metadata
        if related:
            first_related = related[0]
            self.assertIn('relationship_weight', first_related)
            self.assertIn('relationship_depth', first_related)
    
    def test_conversation_threads(self):
        """Test conversation thread detection."""
        threads = self.graph.find_conversation_threads(max_gap_minutes=5)
        
        self.assertIsInstance(threads, list)
        # Should detect the conversation thread
        self.assertGreater(len(threads), 0)
        
        if threads:
            # The thread should contain our events
            first_thread = threads[0]
            self.assertGreater(len(first_thread), 1)
    
    def test_central_events(self):
        """Test central event identification."""
        central = self.graph.get_central_events(limit=3)
        
        self.assertIsInstance(central, list)
        self.assertLessEqual(len(central), 3)
        
        # Central events should have centrality scores
        for event in central:
            self.assertIn('centrality_score', event)
            self.assertIn('connection_count', event)
    
    def test_graph_statistics(self):
        """Test graph statistics calculation."""
        stats = self.graph.get_graph_statistics()
        
        required_fields = ['total_nodes', 'total_edges', 'graph_density', 
                          'average_connections', 'connection_types']
        
        for field in required_fields:
            self.assertIn(field, stats)
        
        self.assertEqual(stats['total_nodes'], 3)
        self.assertIsInstance(stats['graph_density'], float)


class TestReflectionAgent(unittest.TestCase):
    """Test the reflection and analysis system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = ReflectionAgent()
        
        # Create sample events for a day
        self.daily_events = [
            {
                'id': 'day1_event1',
                'content': 'Started learning about Python programming',
                'actor': 'user',
                'timestamp': datetime.now().replace(hour=9).isoformat(),
                'emotion_analysis': {
                    'primary_emotion': 'curiosity',
                    'emotional_intensity': 0.7,
                    'valence': 0.5
                },
                'salience_analysis': {'salience_score': 0.8}
            },
            {
                'id': 'day1_event2',
                'content': 'Had a great conversation about AI ethics',
                'actor': 'user',
                'timestamp': datetime.now().replace(hour=14).isoformat(),
                'emotion_analysis': {
                    'primary_emotion': 'joy',
                    'emotional_intensity': 0.6,
                    'valence': 0.7
                },
                'salience_analysis': {'salience_score': 0.6}
            },
            {
                'id': 'day1_event3',
                'content': 'Feeling a bit overwhelmed with all the new concepts',
                'actor': 'user',
                'timestamp': datetime.now().replace(hour=18).isoformat(),
                'emotion_analysis': {
                    'primary_emotion': 'fear',
                    'emotional_intensity': 0.5,
                    'valence': -0.3
                },
                'salience_analysis': {'salience_score': 0.4}
            }
        ]
    
    def test_daily_reflection_generation(self):
        """Test daily reflection generation."""
        reflection = self.agent.generate_daily_reflection(
            self.daily_events, 
            date.today()
        )
        
        # Check required fields
        required_fields = ['id', 'type', 'date', 'event_count', 'emotional_tone',
                          'key_events', 'interaction_patterns', 'learning_moments']
        
        for field in required_fields:
            self.assertIn(field, reflection)
        
        self.assertEqual(reflection['type'], 'daily')
        self.assertEqual(reflection['event_count'], len(self.daily_events))
        self.assertIsInstance(reflection['emotional_tone'], dict)
        self.assertIsInstance(reflection['key_events'], list)
    
    def test_emotional_tone_analysis(self):
        """Test emotional tone analysis."""
        reflection = self.agent.generate_daily_reflection(
            self.daily_events, 
            date.today()
        )
        
        emotional_tone = reflection['emotional_tone']
        required_tone_fields = ['tone', 'description', 'average_intensity', 
                               'average_valence', 'dominant_emotions']
        
        for field in required_tone_fields:
            self.assertIn(field, emotional_tone)
        
        self.assertIsInstance(emotional_tone['dominant_emotions'], list)
        self.assertIsInstance(emotional_tone['average_intensity'], float)
    
    def test_key_events_identification(self):
        """Test key event identification."""
        reflection = self.agent.generate_daily_reflection(
            self.daily_events, 
            date.today()
        )
        
        key_events = reflection['key_events']
        self.assertIsInstance(key_events, list)
        
        # Should identify events with high salience
        if key_events:
            first_key_event = key_events[0]
            self.assertIn('significance_score', first_key_event)
            self.assertIn('reasons', first_key_event)
            self.assertIn('content', first_key_event)
    
    def test_learning_moments_extraction(self):
        """Test learning moment extraction."""
        reflection = self.agent.generate_daily_reflection(
            self.daily_events, 
            date.today()
        )
        
        learning_moments = reflection['learning_moments']
        self.assertIsInstance(learning_moments, list)
        
        # Should find the learning event
        self.assertGreater(len(learning_moments), 0)
        
        if learning_moments:
            learning_moment = learning_moments[0]
            self.assertIn('content', learning_moment)
            self.assertIn('indicators', learning_moment)
    
    def test_pattern_identification(self):
        """Test pattern identification across events."""
        patterns = self.agent.identify_patterns(self.daily_events, 1)
        
        required_pattern_fields = ['temporal_patterns', 'emotional_patterns',
                                  'interaction_patterns', 'content_patterns']
        
        for field in required_pattern_fields:
            self.assertIn(field, patterns)
        
        self.assertIn('identified_at', patterns)
        self.assertEqual(patterns['total_events_analyzed'], len(self.daily_events))
    
    def test_empty_events_handling(self):
        """Test handling of empty event lists."""
        reflection = self.agent.generate_daily_reflection([], date.today())
        
        self.assertEqual(reflection['event_count'], 0)
        self.assertIn('note', reflection)
        self.assertEqual(reflection['type'], 'daily')


class TestMemoryStore(unittest.TestCase):
    """Test the persistent storage system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary storage
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, 'test_memories.json')
        self.store = MemoryStore(self.storage_path)
        
        # Sample event
        self.sample_event = {
            'id': 'test_event_1',
            'content': 'This is a test memory',
            'actor': 'user',
            'event_type': 'test',
            'timestamp': datetime.now().isoformat(),
            'emotion_analysis': {
                'primary_emotion': 'joy',
                'emotional_intensity': 0.6
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.store.close()
        shutil.rmtree(self.temp_dir)
    
    def test_event_storage(self):
        """Test storing events."""
        success = self.store.store_event(self.sample_event)
        self.assertTrue(success)
        
        # Retrieve the event
        retrieved = self.store.get_event_by_id(self.sample_event['id'])
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['content'], self.sample_event['content'])
        self.assertEqual(retrieved['actor'], self.sample_event['actor'])
    
    def test_event_querying(self):
        """Test querying events."""
        # Store multiple events
        events = []
        for i in range(5):
            event = self.sample_event.copy()
            event['id'] = f'test_event_{i}'
            event['content'] = f'Test memory {i}'
            event['timestamp'] = (datetime.now() - timedelta(hours=i)).isoformat()
            events.append(event)
            self.store.store_event(event)
        
        # Query by actor
        user_events = self.store.get_events(actor='user')
        self.assertEqual(len(user_events), 5)
        
        # Query with limit
        limited_events = self.store.get_events(limit=3)
        self.assertLessEqual(len(limited_events), 3)
        
        # Query by date range
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=2)
        range_events = self.store.get_events(
            date_range=(start_date.isoformat(), end_date.isoformat())
        )
        self.assertGreater(len(range_events), 0)
    
    def test_content_search(self):
        """Test content-based search."""
        # Store event with specific content
        specific_event = self.sample_event.copy()
        specific_event['id'] = 'specific_test'
        specific_event['content'] = 'Machine learning is fascinating'
        self.store.store_event(specific_event)
        
        # Search for content
        results = self.store.search_events_by_content('machine learning')
        self.assertGreater(len(results), 0)
        
        found_event = next((e for e in results if e['id'] == 'specific_test'), None)
        self.assertIsNotNone(found_event)
    
    def test_reflection_storage(self):
        """Test storing and retrieving reflections."""
        reflection = {
            'id': 'test_reflection',
            'type': 'daily',
            'date': date.today().isoformat(),
            'summary': 'Test daily reflection',
            'event_count': 3
        }
        
        success = self.store.store_reflection(reflection)
        self.assertTrue(success)
        
        # Retrieve reflection
        retrieved = self.store.get_reflection(date.today().isoformat(), 'daily')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['summary'], reflection['summary'])
    
    def test_storage_statistics(self):
        """Test storage statistics."""
        # Store some events
        for i in range(3):
            event = self.sample_event.copy()
            event['id'] = f'stats_test_{i}'
            self.store.store_event(event)
        
        stats = self.store.get_storage_stats()
        
        required_fields = ['total_events', 'storage_path', 'file_size_mb']
        for field in required_fields:
            self.assertIn(field, stats)
        
        self.assertEqual(stats['total_events'], 3)
        self.assertIsInstance(stats['file_size_mb'], float)
    
    def test_backup_and_restore(self):
        """Test backup and restore functionality."""
        # Store some data
        self.store.store_event(self.sample_event)
        
        # Create backup
        backup_path = os.path.join(self.temp_dir, 'backup.json')
        success = self.store.backup_to_file(backup_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(backup_path))
        
        # Clear data and restore
        self.store.events_table.truncate()
        self.assertEqual(len(self.store.events_table), 0)
        
        success = self.store.restore_from_backup(backup_path)
        self.assertTrue(success)
        self.assertGreater(len(self.store.events_table), 0)


class TestRecallEngine(unittest.TestCase):
    """Test the main recall engine integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary storage
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, 'test_recall.json')
        self.engine = RecallEngine(self.storage_path, auto_reflect=False)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.engine.close()
        shutil.rmtree(self.temp_dir)
    
    def test_memory_storage_integration(self):
        """Test integrated memory storage."""
        result = self.engine.store_memory(
            content="I learned something interesting about quantum computing today",
            actor="user",
            event_type="learning"
        )
        
        # Check that all analysis was performed
        self.assertIn('emotion_analysis', result)
        self.assertIn('salience_analysis', result)
        self.assertIn('id', result)
        self.assertIn('timestamp', result)
        
        # Verify emotion analysis
        emotion_data = result['emotion_analysis']
        self.assertIn('primary_emotion', emotion_data)
        self.assertIn('emotional_intensity', emotion_data)
        
        # Verify salience analysis
        salience_data = result['salience_analysis']
        self.assertIn('salience_score', salience_data)
        self.assertIn('salience_level', salience_data)
    
    def test_memory_recall_integration(self):
        """Test integrated memory recall."""
        # Store several memories
        memories_to_store = [
            "I love learning about artificial intelligence",
            "Had a difficult conversation with a colleague",
            "Discovered a new coffee shop downtown",
            "Feeling excited about the weekend plans"
        ]
        
        stored_ids = []
        for content in memories_to_store:
            result = self.engine.store_memory(content, "user")
            stored_ids.append(result['id'])
        
        # Recall memories
        recalled = self.engine.recall_memories(query="artificial intelligence", limit=5)
        
        self.assertIsInstance(recalled, list)
        self.assertGreater(len(recalled), 0)
        
        # Check that relevant memory was found
        ai_memory = next((m for m in recalled if 'artificial intelligence' in m['content']), None)
        self.assertIsNotNone(ai_memory)
        
        # Test filtering by actor
        user_memories = self.engine.recall_memories(actor="user", limit=10)
        self.assertEqual(len(user_memories), len(memories_to_store))
    
    def test_daily_reflection_integration(self):
        """Test daily reflection generation."""
        # Store memories for today
        today_memories = [
            "Started reading a book about machine learning",
            "Had lunch with a friend and discussed career goals",
            "Feeling motivated to learn new programming skills"
        ]
        
        for content in today_memories:
            self.engine.store_memory(content, "user")
        
        # Generate reflection
        reflection = self.engine.get_daily_reflection(date.today())
        
        self.assertIsInstance(reflection, dict)
        self.assertEqual(reflection['type'], 'daily')
        self.assertIn('emotional_tone', reflection)
        self.assertIn('key_events', reflection)
        self.assertIn('reflection_summary', reflection)
        
        # Check that it found our events
        self.assertEqual(reflection['event_count'], len(today_memories))
    
    def test_pattern_analysis_integration(self):
        """Test pattern analysis across memories."""
        # Store memories with patterns
        pattern_memories = [
            "Learning about neural networks in deep learning",
            "Practicing machine learning algorithms",
            "Reading research papers on artificial intelligence",
            "Attending a workshop on data science",
            "Discussing AI ethics with colleagues"
        ]
        
        for content in pattern_memories:
            self.engine.store_memory(content, "user")
        
        # Analyze patterns
        patterns = self.engine.analyze_patterns(days=1)
        
        self.assertIsInstance(patterns, dict)
        self.assertIn('temporal_patterns', patterns)
        self.assertIn('emotional_patterns', patterns)
        self.assertIn('content_patterns', patterns)
        
        # Should detect learning pattern
        if 'graph_insights' in patterns:
            self.assertIn('central_memories', patterns['graph_insights'])
    
    def test_system_statistics(self):
        """Test system statistics."""
        # Store some memories
        for i in range(5):
            self.engine.store_memory(f"Test memory {i}", "user")
        
        stats = self.engine.get_memory_statistics()
        
        required_sections = ['storage', 'graph', 'runtime', 'configuration']
        for section in required_sections:
            self.assertIn(section, stats)
        
        # Check storage stats
        self.assertIn('total_events', stats['storage'])
        self.assertEqual(stats['storage']['total_events'], 5)
        
        # Check runtime stats
        self.assertIn('total_memories_stored', stats['runtime'])
        self.assertIn('uptime_hours', stats['runtime'])
    
    def test_configuration_updates(self):
        """Test configuration management."""
        # Update configuration
        new_config = {
            'auto_save': False,
            'enable_graph': False
        }
        
        success = self.engine.update_configuration(new_config)
        self.assertTrue(success)
        
        # Verify updates
        self.assertFalse(self.engine.config['auto_save'])
        self.assertFalse(self.engine.config['enable_graph'])
        
        # Test invalid configuration
        invalid_config = {'invalid_key': 'invalid_value'}
        success = self.engine.update_configuration(invalid_config)
        self.assertTrue(success)  # Should succeed but ignore invalid keys
    
    def test_backup_and_restore_integration(self):
        """Test integrated backup and restore."""
        # Store some memories
        original_memories = [
            "Important memory to backup",
            "Another significant event",
            "Third memorable moment"
        ]
        
        for content in original_memories:
            self.engine.store_memory(content, "user")
        
        # Create backup
        backup_path = os.path.join(self.temp_dir, 'engine_backup.json')
        success = self.engine.backup_memories(backup_path)
        self.assertTrue(success)
        
        # Clear and restore
        self.engine.memory_store.events_table.truncate()
        
        success = self.engine.restore_memories(backup_path)
        self.assertTrue(success)
        
        # Verify restoration
        recalled = self.engine.recall_memories(limit=10)
        self.assertEqual(len(recalled), len(original_memories))
    
    def test_context_manager(self):
        """Test context manager functionality."""
        temp_storage = os.path.join(self.temp_dir, 'context_test.json')
        
        with RecallEngine(temp_storage) as engine:
            result = engine.store_memory("Context manager test", "user")
            self.assertIn('id', result)
        
        # Engine should be closed automatically
        self.assertTrue(True)  # If we get here, context manager worked


class TestQuickFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, 'quick_test.json')
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_recall_engine(self):
        """Test engine creation function."""
        engine = create_recall_engine(self.storage_path)
        self.assertIsInstance(engine, RecallEngine)
        engine.close()
    
    def test_quick_memory_store(self):
        """Test quick memory storage function."""
        from memory.recall_engine import quick_memory_store
        
        result = quick_memory_store(
            "Quick test memory", 
            "user", 
            self.storage_path
        )
        
        self.assertIn('id', result)
        self.assertIn('emotion_analysis', result)
        self.assertEqual(result['content'], "Quick test memory")
    
    def test_quick_memory_recall(self):
        """Test quick memory recall function."""
        from memory.recall_engine import quick_memory_store, quick_memory_recall
        
        # Store a memory first
        quick_memory_store(
            "Searchable quick memory about Python programming", 
            "user", 
            self.storage_path
        )
        
        # Recall it
        results = quick_memory_recall(
            "Python programming", 
            limit=5, 
            storage_path=self.storage_path
        )
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Should find our memory
        found = any('Python programming' in r['content'] for r in results)
        self.assertTrue(found)


def run_comprehensive_tests():
    """Run all tests and provide a summary."""
    print("🧪 Running True Recall Comprehensive Test Suite...")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestEmotionTagger,
        TestSalienceScorer,
        TestMemoryGraph,
        TestReflectionAgent,
        TestMemoryStore,
        TestRecallEngine,
        TestQuickFunctions
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, error in result.failures:
            print(f"  - {test}: {error.split('AssertionError: ')[-1].split(chr(10))[0]}")
    
    if result.errors:
        print(f"\n💥 ERRORS ({len(result.errors)}):")
        for test, error in result.errors:
            print(f"  - {test}: {error.split(chr(10))[-2] if chr(10) in error else error}")
    
    if not result.failures and not result.errors:
        print("\n✅ ALL TESTS PASSED! True Recall system is working correctly.")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run the comprehensive test suite
    success = run_comprehensive_tests()
    
    if success:
        print("\n🎉 True Recall is ready for integration with Dolphin!")
        print("\nNext steps:")
        print("1. Install required dependencies: pip install textblob scikit-learn tinydb")
        print("2. Update requirements.txt with memory dependencies")
        print("3. Integrate RecallEngine with Dolphin interface")
        print("4. Test the complete system with real conversations")
    else:
        print("\n⚠️  Some tests failed. Please review and fix issues before deployment.")
    
    exit(0 if success else 1)
