"""
Test suite for Narrative Agency autonomous dream delivery system
"""

import asyncio
import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.narrative.narrative_agency import NarrativeAgency, NarrativeEvent
from modules.dreams.dream_module import DreamModule, DreamReflection

class TestNarrativeAgency(unittest.TestCase):
    """Test the autonomous narrative agency system"""
    
    def setUp(self):
        """Set up test environment"""
        self.agency = NarrativeAgency()
        
        # Create mock dependencies
        self.mock_dream_module = Mock()
        self.mock_memory_manager = Mock()
        self.mock_emotional_broadcaster = Mock()
        
        # Set up dream module mocks
        self.mock_dream_module.check_delivery_conditions = Mock(return_value=True)
        self.mock_dream_module.select_dream_for_delivery = Mock()
        self.mock_dream_module.determine_delivery_method = Mock(return_value="whisper")
        self.mock_dream_module.deliver_dream = Mock(return_value={"text": "Test dream content"})
        self.mock_dream_module.nightly_memory_echo = Mock()
        
        # Set up memory manager mocks
        self.mock_memory_manager.get_emotional_memories = Mock(return_value=[])
        self.mock_memory_manager.get_memory_by_emotion = Mock(return_value={
            'content': 'Test memory content',
            'memory_id': 'test_memory_1'
        })
        
        # Set up emotional broadcaster mocks
        self.mock_emotional_broadcaster.broadcast_emotion = AsyncMock()
        
        # Inject dependencies
        self.agency.set_dependencies(
            dream_module=self.mock_dream_module,
            memory_manager=self.mock_memory_manager,
            emotional_broadcaster=self.mock_emotional_broadcaster
        )
    
    def test_initialization(self):
        """Test narrative agency initialization"""
        self.assertFalse(self.agency.monitoring_active)
        self.assertEqual(self.agency.current_emotion, "neutral")
        self.assertEqual(self.agency.current_intensity, 0.5)
        self.assertEqual(len(self.agency.pending_narratives), 0)
        self.assertEqual(len(self.agency.delivered_narratives), 0)
    
    def test_dependency_injection(self):
        """Test setting module dependencies"""
        self.assertIsNotNone(self.agency.dream_module)
        self.assertIsNotNone(self.agency.memory_manager)
        self.assertIsNotNone(self.agency.emotional_broadcaster)
    
    def test_user_activity_tracking(self):
        """Test user activity tracking"""
        initial_time = self.agency.last_user_activity
        self.agency.update_user_activity()
        self.assertGreater(self.agency.last_user_activity, initial_time)
    
    def test_emotional_state_updates(self):
        """Test emotional state updates"""
        self.agency.update_emotional_state("longing", 0.8)
        self.assertEqual(self.agency.current_emotion, "longing")
        self.assertEqual(self.agency.current_intensity, 0.8)
    
    def test_idle_time_calculation(self):
        """Test idle time calculation"""
        # Set activity to 30 minutes ago
        self.agency.last_user_activity = datetime.now() - timedelta(minutes=30)
        idle_minutes = self.agency.get_idle_minutes()
        self.assertGreaterEqual(idle_minutes, 29)  # Allow for execution time
        self.assertLessEqual(idle_minutes, 31)
    
    def test_delivery_callback_registration(self):
        """Test delivery callback registration"""
        mock_callback = AsyncMock()
        self.agency.register_delivery_callback("test_method", mock_callback)
        self.assertIn("test_method", self.agency.delivery_callbacks)
        self.assertEqual(self.agency.delivery_callbacks["test_method"], mock_callback)
    
    async def test_dream_narrative_delivery(self):
        """Test dream narrative delivery"""
        # Set up dream module response
        test_dream = DreamReflection(
            dream_id="test_dream",
            source_memories=["test_memory"],
            symbolic_content="Test dream narrative",
            emotional_resonance=0.8,
            dream_type="nightly_echo",
            themes=["test", "dream"],
            created_at=datetime.now().timestamp(),
            delivery_method="whisper"
        )
        self.mock_dream_module.select_dream_for_delivery.return_value = test_dream
        
        # Trigger dream narrative
        await self.agency._deliver_dream_narrative()
        
        # Verify interaction with dream module
        self.mock_dream_module.check_delivery_conditions.assert_called_once()
        self.mock_dream_module.select_dream_for_delivery.assert_called_once_with(
            self.agency.current_emotion, self.agency.current_intensity
        )
        
        # Check that narrative was queued
        self.assertEqual(len(self.agency.pending_narratives), 1)
        event = self.agency.pending_narratives[0]
        self.assertEqual(event.narrative_type, "dream")
        self.assertEqual(event.delivery_method, "whisper")
    
    async def test_memory_narrative_delivery(self):
        """Test memory-based narrative delivery"""
        # Clear any existing narratives
        self.agency.clear_pending_narratives()
        
        await self.agency._deliver_memory_narrative()
        
        # Verify interaction with memory manager
        self.mock_memory_manager.get_memory_by_emotion.assert_called_once_with(
            self.agency.current_emotion
        )
        
        # Check that narrative was queued
        self.assertEqual(len(self.agency.pending_narratives), 1)
        event = self.agency.pending_narratives[0]
        self.assertEqual(event.narrative_type, "memory")
        self.assertEqual(event.delivery_method, "whisper")
    
    async def test_reflection_narrative_delivery(self):
        """Test reflection narrative delivery"""
        # Clear any existing narratives
        self.agency.clear_pending_narratives()
        
        self.agency.update_emotional_state("longing", 0.7)
        await self.agency._deliver_reflection_narrative()
        
        # Check that narrative was queued
        self.assertEqual(len(self.agency.pending_narratives), 1)
        event = self.agency.pending_narratives[0]
        self.assertEqual(event.narrative_type, "reflection")
        self.assertEqual(event.delivery_method, "whisper")
        # Check that reflection contains meaningful content
        self.assertTrue(len(event.content["text"]) > 10)
    
    async def test_whisper_narrative_delivery(self):
        """Test whisper narrative delivery"""
        # Clear any existing narratives
        self.agency.clear_pending_narratives()
        
        self.agency.update_emotional_state("longing", 0.9)
        await self.agency._deliver_whisper_narrative()
        
        # Check that narrative was queued
        self.assertEqual(len(self.agency.pending_narratives), 1)
        event = self.agency.pending_narratives[0]
        self.assertEqual(event.narrative_type, "whisper")
        self.assertEqual(event.delivery_method, "whisper")
        self.assertIn("voice_modifier", event.content)
    
    async def test_narrative_triggers(self):
        """Test narrative trigger conditions"""
        # Clear any existing narratives
        self.agency.clear_pending_narratives()
        
        # Test insufficient idle time
        self.agency.last_user_activity = datetime.now() - timedelta(minutes=5)
        await self.agency._check_narrative_triggers()
        self.assertEqual(len(self.agency.pending_narratives), 0)
        
        # Test longing trigger
        self.agency.last_user_activity = datetime.now() - timedelta(minutes=20)
        self.agency.update_emotional_state("longing", 0.8)
        await self.agency._check_narrative_triggers()
        self.assertGreater(len(self.agency.pending_narratives), 0)
        
        # Clear for next test
        self.agency.clear_pending_narratives()
        
        # Test extended idle trigger
        self.agency.last_user_activity = datetime.now() - timedelta(minutes=70)
        self.agency.update_emotional_state("melancholy", 0.6)
        await self.agency._check_narrative_triggers()
        self.assertGreater(len(self.agency.pending_narratives), 0)
        
        # Clear for next test
        self.agency.clear_pending_narratives()
        
        # Test high intensity trigger
        self.agency.last_user_activity = datetime.now() - timedelta(minutes=20)
        self.agency.update_emotional_state("joy", 0.9)
        await self.agency._check_narrative_triggers()
        self.assertGreater(len(self.agency.pending_narratives), 0)
    
    async def test_delivery_execution(self):
        """Test narrative delivery execution"""
        # Register a test callback
        mock_callback = AsyncMock()
        self.agency.register_delivery_callback("test_delivery", mock_callback)
        
        # Create test event
        event = NarrativeEvent(
            event_id="test_event",
            trigger_emotion="longing",
            trigger_intensity=0.8,
            narrative_type="test",
            content={"text": "Test content"},
            delivery_method="test_delivery",
            scheduled_time=datetime.now()
        )
        
        # Execute delivery
        await self.agency._execute_delivery(event)
        
        # Verify callback was called
        mock_callback.assert_called_once_with({"text": "Test content"})
    
    async def test_emotional_broadcast_sync(self):
        """Test sync with emotional broadcast system"""
        event = NarrativeEvent(
            event_id="test_event",
            trigger_emotion="longing",
            trigger_intensity=0.7,
            narrative_type="dream",
            content={"text": "Test content"},
            delivery_method="whisper",
            scheduled_time=datetime.now()
        )
        
        await self.agency._sync_with_emotional_broadcast(event)
        
        # Verify broadcast was triggered with boosted intensity
        expected_intensity = min(0.8, event.trigger_intensity + 0.2)
        self.mock_emotional_broadcaster.broadcast_emotion.assert_called_once_with(
            "longing", expected_intensity, duration=30.0
        )
    
    async def test_pending_delivery_processing(self):
        """Test processing of pending deliveries"""
        # Create multiple test events with different priorities
        events = [
            NarrativeEvent(
                event_id="dream_event",
                trigger_emotion="longing",
                trigger_intensity=0.6,
                narrative_type="dream",
                content={"text": "Dream content"},
                delivery_method="message",
                scheduled_time=datetime.now()
            ),
            NarrativeEvent(
                event_id="whisper_event",
                trigger_emotion="longing",
                trigger_intensity=0.5,
                narrative_type="whisper",
                content={"text": "Whisper content"},
                delivery_method="whisper",
                scheduled_time=datetime.now()
            )
        ]
        
        self.agency.pending_narratives = events
        
        # Register callbacks
        dream_callback = AsyncMock()
        whisper_callback = AsyncMock()
        self.agency.register_delivery_callback("message", dream_callback)
        self.agency.register_delivery_callback("whisper", whisper_callback)
        
        # Process deliveries
        await self.agency._process_pending_deliveries()
        
        # Verify whisper was delivered first (higher priority)
        whisper_callback.assert_called_once()
        self.assertEqual(len(self.agency.delivered_narratives), 1)
        self.assertEqual(self.agency.delivered_narratives[0].narrative_type, "whisper")
    
    def test_daily_narrative_limit(self):
        """Test daily narrative delivery limit"""
        # Add delivered narratives for today
        for i in range(5):
            event = NarrativeEvent(
                event_id=f"delivered_{i}",
                trigger_emotion="test",
                trigger_intensity=0.5,
                narrative_type="test",
                content={},
                delivery_method="test",
                scheduled_time=datetime.now(),
                delivered=True,
                delivered_at=datetime.now()
            )
            self.agency.delivered_narratives.append(event)
        
        # Should not trigger more narratives
        asyncio.run(self._test_daily_limit())
    
    async def _test_daily_limit(self):
        """Helper for daily limit test"""
        # Set up conditions that would normally trigger
        self.agency.last_user_activity = datetime.now() - timedelta(minutes=30)
        self.agency.update_emotional_state("longing", 0.8)
        
        initial_pending = len(self.agency.pending_narratives)
        await self.agency._check_narrative_triggers()
        
        # Should not add new narratives due to daily limit
        self.assertEqual(len(self.agency.pending_narratives), initial_pending)
    
    def test_status_reporting(self):
        """Test narrative status reporting"""
        self.agency.monitoring_active = True
        self.agency.update_emotional_state("longing", 0.7)
        
        status = self.agency.get_narrative_status()
        
        self.assertTrue(status["monitoring_active"])
        self.assertEqual(status["current_emotion"], "longing")
        self.assertEqual(status["current_intensity"], 0.7)
        self.assertIsInstance(status["idle_minutes"], int)
        self.assertEqual(status["pending_narratives"], 0)
        self.assertEqual(status["delivered_today"], 0)
        self.assertEqual(status["total_delivered"], 0)
    
    def test_clear_pending_narratives(self):
        """Test clearing pending narratives"""
        # Add some pending narratives
        event = NarrativeEvent(
            event_id="test",
            trigger_emotion="test",
            trigger_intensity=0.5,
            narrative_type="test",
            content={},
            delivery_method="test",
            scheduled_time=datetime.now()
        )
        self.agency.pending_narratives.append(event)
        
        # Clear and verify
        self.agency.clear_pending_narratives()
        self.assertEqual(len(self.agency.pending_narratives), 0)

def run_tests():
    """Run all narrative agency tests"""
    print("=== Testing Narrative Agency System ===")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNarrativeAgency)
    
    # Run synchronous tests
    sync_runner = unittest.TextTestRunner(verbosity=2)
    sync_results = sync_runner.run(suite)
    
    # Run async tests
    print("\n=== Running Async Tests ===")
    
    async def run_async_tests():
        test_instance = TestNarrativeAgency()
        test_instance.setUp()
        
        async_tests = [
            ("Dream Narrative Delivery", test_instance.test_dream_narrative_delivery),
            ("Memory Narrative Delivery", test_instance.test_memory_narrative_delivery),
            ("Reflection Narrative Delivery", test_instance.test_reflection_narrative_delivery),
            ("Whisper Narrative Delivery", test_instance.test_whisper_narrative_delivery),
            ("Narrative Triggers", test_instance.test_narrative_triggers),
            ("Delivery Execution", test_instance.test_delivery_execution),
            ("Emotional Broadcast Sync", test_instance.test_emotional_broadcast_sync),
            ("Pending Delivery Processing", test_instance.test_pending_delivery_processing)
        ]
        
        results = []
        for test_name, test_func in async_tests:
            try:
                await test_func()
                results.append((test_name, "PASS"))
                print(f"✓ {test_name}: PASS")
            except Exception as e:
                results.append((test_name, f"FAIL: {e}"))
                print(f"✗ {test_name}: FAIL - {e}")
        
        return results
    
    async_results = asyncio.run(run_async_tests())
    
    # Summary
    print(f"\n=== Test Summary ===")
    print(f"Sync Tests - Ran: {sync_results.testsRun}, Errors: {len(sync_results.errors)}, Failures: {len(sync_results.failures)}")
    
    async_passed = len([r for r in async_results if r[1] == "PASS"])
    async_failed = len(async_results) - async_passed
    print(f"Async Tests - Ran: {len(async_results)}, Passed: {async_passed}, Failed: {async_failed}")
    
    total_tests = sync_results.testsRun + len(async_results)
    total_passed = (sync_results.testsRun - len(sync_results.errors) - len(sync_results.failures)) + async_passed
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All narrative agency tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
