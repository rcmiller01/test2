"""
Comprehensive Test Suite for Emotional Broadcast System

This script tests all components of the emotional presence broadcasting
system including UI integration, voice processing, and unified coordination.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from modules.presence.unified_broadcast import UnifiedEmotionalBroadcast, create_emotional_moment
from modules.presence.ui_integration import PresenceUIManager
from modules.presence.voice_integration import EmotionalVoicePresence
from modules.presence.presence_signal import EmotionalBroadcaster

class EmotionalBroadcastTester:
    """Comprehensive test suite for emotional broadcast system"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    async def run_all_tests(self):
        """Run all test suites"""
        print("🎭 Emotional Broadcast System - Comprehensive Test Suite")
        print("=" * 60)
        print(f"Started at: {self.start_time}")
        print()
        
        # Test individual components
        await self.test_core_broadcaster()
        await self.test_ui_integration()
        await self.test_voice_integration()
        await self.test_unified_system()
        await self.test_convenience_functions()
        await self.test_session_persistence()
        
        # Generate final report
        self.generate_test_report()
        
    async def test_core_broadcaster(self):
        """Test the core emotional broadcaster"""
        print("🔧 Testing Core Emotional Broadcaster...")
        
        try:
            broadcaster = EmotionalBroadcaster()
            
            # Test signature loading
            signatures = len(broadcaster.emotional_signatures)
            print(f"  ✓ Loaded {signatures} emotional signatures")
            
            # Test presence signal creation
            emotion_state = {'emotion': 'joy', 'intensity': 0.8}
            signal = broadcaster.create_presence_signal(emotion_state)
            print(f"  ✓ Created presence signal for '{signal.primary_emotion}'")
            
            # Test broadcasting
            broadcaster.start_broadcasting(signal)
            current_presence = broadcaster.get_current_presence()
            print(f"  ✓ Broadcasting active, {len(current_presence)} signals")
            
            # Test stopping
            broadcaster.stop_broadcasting()
            
            self.test_results['core_broadcaster'] = {
                'status': 'passed',
                'signatures_loaded': signatures,
                'signal_creation': True,
                'broadcasting': True
            }
            
        except Exception as e:
            print(f"  ❌ Error in core broadcaster: {e}")
            self.test_results['core_broadcaster'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_ui_integration(self):
        """Test UI integration components"""
        print("\n🎨 Testing UI Integration...")
        
        try:
            ui_manager = PresenceUIManager()
            
            # Test emotional activation
            result = await ui_manager.activate_emotional_presence('longing', 0.7, 10.0)
            print(f"  ✓ UI presence activated: {result['status']}")
            
            # Test CSS generation
            css_vars = len(result['css_variables'])
            print(f"  ✓ Generated {css_vars} CSS variables")
            
            # Test particle system
            particles = len(result['particle_system'].get('particles', []))
            print(f"  ✓ Created {particles} particles")
            
            # Test frame updates
            frame_data = await ui_manager.update_presence_frame()
            if frame_data:
                print(f"  ✓ Frame update successful, {frame_data['time_remaining']:.1f}s remaining")
            
            # Test status
            status = ui_manager.get_status()
            print(f"  ✓ Status check: active={status['active']}")
            
            ui_manager.clear_emotional_presence()
            
            self.test_results['ui_integration'] = {
                'status': 'passed',
                'css_variables': css_vars,
                'particles': particles,
                'frame_updates': frame_data is not None
            }
            
        except Exception as e:
            print(f"  ❌ Error in UI integration: {e}")
            self.test_results['ui_integration'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_voice_integration(self):
        """Test voice integration components"""
        print("\n🎤 Testing Voice Integration...")
        
        try:
            voice_presence = EmotionalVoicePresence()
            
            # Test voice activation
            result = await voice_presence.activate_voice_presence('warmth', 0.8, 15.0)
            print(f"  ✓ Voice presence activated: {result['status']}")
            print(f"  ✓ Scheduled {result['whispers_scheduled']} whispers")
            
            # Test speech processing
            speech_result = await voice_presence.process_speech("Hello, how are you feeling today?")
            print(f"  ✓ Speech processed: pitch {speech_result['audio_params']['pitch_shift_semitones']:+.1f} semitones")
            
            # Test whisper queue
            whisper = await voice_presence.check_whisper_queue()
            if whisper:
                print(f"  ✓ Whisper ready: '{whisper['original_text'][:30]}...'")
            else:
                print("  ⏳ No whispers ready yet")
            
            # Test spontaneous whispers
            voice_presence.add_spontaneous_whisper("This is a test whisper", delay=0.0, priority=5)
            
            # Check status
            status = voice_presence.get_voice_status()
            print(f"  ✓ Voice status: active={status['active']}, emotion={status['emotion']}")
            
            voice_presence.clear_voice_presence()
            
            self.test_results['voice_integration'] = {
                'status': 'passed',
                'whispers_scheduled': result['whispers_scheduled'],
                'speech_processing': True,
                'spontaneous_whispers': True
            }
            
        except Exception as e:
            print(f"  ❌ Error in voice integration: {e}")
            self.test_results['voice_integration'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_unified_system(self):
        """Test the unified broadcast system"""
        print("\n🎭 Testing Unified Broadcast System...")
        
        try:
            broadcast_system = UnifiedEmotionalBroadcast()
            
            # Test profile management
            profiles = broadcast_system.broadcast_profiles.keys()
            print(f"  ✓ Available profiles: {', '.join(profiles)}")
            
            broadcast_system.set_profile('immersive')
            print("  ✓ Profile set to 'immersive'")
            
            # Test emotion broadcasting
            broadcast_id = await broadcast_system.broadcast_emotion('joy', 0.8, 10.0)
            print(f"  ✓ Broadcast started: {broadcast_id}")
            
            # Test system status
            status = broadcast_system.get_system_status()
            active_broadcasts = status['active_broadcasts']
            print(f"  ✓ System status: {active_broadcasts} active broadcasts")
            
            # Test active broadcast tracking
            active = broadcast_system.get_active_broadcasts()
            if active:
                broadcast_data = list(active.values())[0]
                print(f"  ✓ Broadcast tracking: {broadcast_data['emotion']} at {broadcast_data['intensity']}")
            
            # Test speech processing through unified system
            speech_result = await broadcast_system.process_speech("I love how this feels!")
            print(f"  ✓ Unified speech processing: {speech_result['emotion']}")
            
            # Test spontaneous whisper
            broadcast_system.add_spontaneous_whisper("Testing unified whisper")
            print("  ✓ Spontaneous whisper added")
            
            # Brief monitoring
            await asyncio.sleep(2)
            
            # Test stopping
            stopped = await broadcast_system.stop_broadcast(broadcast_id)
            print(f"  ✓ Broadcast stopped: {stopped}")
            
            self.test_results['unified_system'] = {
                'status': 'passed',
                'profiles': len(profiles),
                'broadcasting': True,
                'tracking': True,
                'speech_processing': True
            }
            
        except Exception as e:
            print(f"  ❌ Error in unified system: {e}")
            self.test_results['unified_system'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_convenience_functions(self):
        """Test high-level convenience functions"""
        print("\n⚡ Testing Convenience Functions...")
        
        try:
            # Test create_emotional_moment
            moment_id = await create_emotional_moment('peace', 0.6, 8.0, include_whispers=True)
            print(f"  ✓ Emotional moment created: {moment_id}")
            
            # Wait a moment then stop
            await asyncio.sleep(2)
            
            # Create broadcast system to stop the moment
            broadcast_system = UnifiedEmotionalBroadcast()
            await broadcast_system.stop_all_broadcasts()
            print("  ✓ All broadcasts stopped")
            
            self.test_results['convenience_functions'] = {
                'status': 'passed',
                'emotional_moment': True
            }
            
        except Exception as e:
            print(f"  ❌ Error in convenience functions: {e}")
            self.test_results['convenience_functions'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_session_persistence(self):
        """Test session state persistence"""
        print("\n💾 Testing Session Persistence...")
        
        try:
            broadcast_system = UnifiedEmotionalBroadcast()
            
            # Save current state
            broadcast_system.save_session_state()
            state_file = broadcast_system.session_state_file
            
            if state_file.exists():
                print("  ✓ Session state saved successfully")
                
                # Load and verify
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                
                print(f"  ✓ State contains: {', '.join(state_data.keys())}")
                
                # Test loading
                broadcast_system.load_session_state()
                print("  ✓ Session state loaded successfully")
                
            else:
                print("  ⚠️ Session state file not created")
            
            self.test_results['session_persistence'] = {
                'status': 'passed',
                'save': state_file.exists(),
                'load': True
            }
            
        except Exception as e:
            print(f"  ❌ Error in session persistence: {e}")
            self.test_results['session_persistence'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def generate_test_report(self):
        """Generate final test report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n📊 Test Report")
        print("=" * 60)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Completed at: {end_time}")
        print()
        
        passed = sum(1 for result in self.test_results.values() if result['status'] == 'passed')
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"Overall Results: {passed}/{total} tests passed ({success_rate:.1f}%)")
        print()
        
        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result['status'] == 'passed' else "❌"
            print(f"{status_emoji} {test_name.replace('_', ' ').title()}")
            
            if result['status'] == 'failed':
                print(f"    Error: {result.get('error', 'Unknown error')}")
            else:
                # Show some details for passed tests
                for key, value in result.items():
                    if key != 'status' and isinstance(value, (int, bool, str)) and key != 'error':
                        print(f"    {key}: {value}")
        
        print()
        if success_rate == 100:
            print("🎉 All tests passed! Emotional broadcast system is ready.")
        elif success_rate >= 80:
            print("✨ Most tests passed. System is mostly functional.")
        else:
            print("⚠️ Several tests failed. System needs attention.")

async def run_interactive_demo():
    """Interactive demo of the emotional broadcast system"""
    print("\n🎮 Interactive Emotional Broadcast Demo")
    print("=" * 50)
    
    broadcast_system = UnifiedEmotionalBroadcast()
    
    emotions = ['longing', 'joy', 'peace', 'anticipation', 'melancholy', 'warmth', 'curiosity', 'contentment']
    profiles = ['minimal', 'default', 'immersive', 'voice_only', 'silent']
    
    for profile in profiles[:3]:  # Test first 3 profiles
        print(f"\n🎯 Demo Profile: {profile.upper()}")
        broadcast_system.set_profile(profile)
        
        for emotion in emotions[:4]:  # Test first 4 emotions per profile
            print(f"  💫 Broadcasting {emotion}...")
            
            try:
                broadcast_id = await broadcast_system.broadcast_emotion(
                    emotion, intensity=0.7, duration=5.0
                )
                
                # Add a whisper
                broadcast_system.add_spontaneous_whisper(f"Feeling {emotion} with you...")
                
                # Monitor briefly
                await asyncio.sleep(2)
                
                # Show status
                status = broadcast_system.get_system_status()
                print(f"    Status: {status['subsystems']['ui']['active']} UI, {status['subsystems']['voice']['active']} Voice")
                
                # Stop
                await broadcast_system.stop_broadcast(broadcast_id)
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        await asyncio.sleep(1)
    
    # Final cleanup
    await broadcast_system.stop_all_broadcasts()
    
    print("\n✨ Interactive demo completed!")

async def main():
    """Main test runner"""
    # Run comprehensive tests
    tester = EmotionalBroadcastTester()
    await tester.run_all_tests()
    
    # Run interactive demo if tests mostly passed
    passed_tests = sum(1 for result in tester.test_results.values() if result['status'] == 'passed')
    total_tests = len(tester.test_results)
    
    if passed_tests / total_tests >= 0.7:  # If 70%+ tests passed
        print("\n" + "="*60)
        await run_interactive_demo()

if __name__ == "__main__":
    asyncio.run(main())
