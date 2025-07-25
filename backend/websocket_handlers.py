# websocket_handlers.py
# Backend WebSocket handlers for Phase 3 real-time features

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

# Import Phase 3 modules
from modules.input.haptic_system import get_haptic_system, trigger_haptic_feedback
from modules.input.biometric_sync import get_biometric_sync, start_biometric_monitoring
from modules.visual.vr_integration import get_vr_integration, start_vr_session
from modules.relationship.relationship_ai import get_relationship_ai, analyze_relationship_health
from modules.voice.emotional_tts import synthesize_emotional_speech
from modules.memory.romantic_memory_engine import get_romantic_memory_engine
from modules.visual.mood_driven_avatar import get_mood_driven_avatar, update_avatar_mood

# Import socket.io from OpenWebUI
from frontend.backend.open_webui.socket.main import sio, SESSION_POOL, USER_POOL

# Import MongoDB client
from database.mongodb_client import mongodb_client

logger = logging.getLogger(__name__)

# Store active persona rooms
PERSONA_ROOMS = {}

# Store active sessions and their states
SESSION_STATES = {}

class Phase3WebSocketHandlers:
    """WebSocket handlers for Phase 3 real-time features"""
    
    def __init__(self):
        self.haptic_system = get_haptic_system()
        self.biometric_sync = get_biometric_sync()
        self.vr_integration = get_vr_integration()
        self.relationship_ai = get_relationship_ai()
        self.memory_engine = get_romantic_memory_engine()
        self.avatar_system = get_mood_driven_avatar()
        
    async def setup_handlers(self):
        """Setup all WebSocket event handlers"""
        
        # Persona room management
        sio.on('join-persona-room', self.handle_join_persona_room)
        sio.on('leave-persona-room', self.handle_leave_persona_room)
        
        # Avatar events
        sio.on('avatar:update:mood', self.handle_avatar_update_mood)
        sio.on('avatar:trigger:gesture', self.handle_avatar_trigger_gesture)
        sio.on('avatar:update:expression', self.handle_avatar_update_expression)
        
        # Haptic events
        sio.on('haptic:trigger', self.handle_haptic_trigger)
        sio.on('haptic:stop', self.handle_haptic_stop)
        
        # VR events
        sio.on('vr:scene:start', self.handle_vr_scene_start)
        sio.on('vr:scene:stop', self.handle_vr_scene_stop)
        
        # Voice events
        sio.on('voice:speak', self.handle_voice_speak)
        sio.on('voice:stop', self.handle_voice_stop)
        sio.on('voice:listen:start', self.handle_voice_listen_start)
        sio.on('voice:listen:stop', self.handle_voice_listen_stop)
        
        # Memory events
        sio.on('memory:create', self.handle_memory_create)
        sio.on('memory:update', self.handle_memory_update)
        
        # Relationship events
        sio.on('relationship:analyze', self.handle_relationship_analyze)
        
        logger.info("Phase 3 WebSocket handlers setup complete")
    
    async def handle_join_persona_room(self, sid, data):
        """Handle user joining a persona-specific room"""
        try:
            persona = data.get('persona', 'unified_ai')
            user = SESSION_POOL.get(sid)
            
            if not user:
                logger.warning(f"User not found for session {sid}")
                return
            
            # Join persona room
            room_name = f"persona:{persona}"
            await sio.enter_room(sid, room_name)
            
            # Store session state
            SESSION_STATES[sid] = {
                'persona': persona,
                'user_id': user.get('id'),
                'joined_at': datetime.now().isoformat()
            }
            
            # Add to persona rooms tracking
            if room_name not in PERSONA_ROOMS:
                PERSONA_ROOMS[room_name] = []
            PERSONA_ROOMS[room_name].append(sid)
            
            # Send confirmation
            await sio.emit('persona:room:joined', {
                'persona': persona,
                'room': room_name,
                'timestamp': datetime.now().isoformat()
            }, room=sid)
            
            logger.info(f"User {user.get('id')} joined persona room {room_name}")
            
        except Exception as e:
            logger.error(f"Error joining persona room: {e}")
    
    async def handle_leave_persona_room(self, sid, data):
        """Handle user leaving a persona-specific room"""
        try:
            persona = data.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            # Leave room
            await sio.leave_room(sid, room_name)
            
            # Remove from tracking
            if room_name in PERSONA_ROOMS and sid in PERSONA_ROOMS[room_name]:
                PERSONA_ROOMS[room_name].remove(sid)
            
            # Clean up session state
            if sid in SESSION_STATES:
                del SESSION_STATES[sid]
            
            logger.info(f"User left persona room {room_name}")
            
        except Exception as e:
            logger.error(f"Error leaving persona room: {e}")
    
    async def handle_avatar_update_mood(self, sid, data):
        """Handle avatar mood updates"""
        try:
            mood = data.get('mood', 'neutral')
            user = SESSION_POOL.get(sid)
            
            if not user:
                return
            
            # Update avatar mood
            success = update_avatar_mood(mood)
            
            # Broadcast to persona room
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('avatar:update', {
                'mood': mood,
                'success': success,
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Avatar mood updated to {mood} for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error updating avatar mood: {e}")
    
    async def handle_avatar_trigger_gesture(self, sid, data):
        """Handle avatar gesture triggers"""
        try:
            gesture = data.get('gesture', 'wave')
            user = SESSION_POOL.get(sid)
            
            if not user:
                return
            
            # Trigger avatar gesture
            success = self.avatar_system.trigger_gesture(gesture)
            
            # Broadcast to persona room
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('avatar:animation:start', {
                'gesture': gesture,
                'success': success,
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            # Simulate animation progress
            await self._simulate_animation_progress(sid, gesture, room_name)
            
            logger.info(f"Avatar gesture {gesture} triggered for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error triggering avatar gesture: {e}")
    
    async def handle_avatar_update_expression(self, sid, data):
        """Handle avatar expression updates"""
        try:
            expression = data.get('expression', 'neutral')
            user = SESSION_POOL.get(sid)
            
            if not user:
                return
            
            # Update avatar expression
            success = self.avatar_system.update_expression(expression)
            
            # Broadcast to persona room
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('avatar:update', {
                'expression': expression,
                'success': success,
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Avatar expression updated to {expression} for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error updating avatar expression: {e}")
    
    async def handle_haptic_trigger(self, sid, data):
        """Handle haptic feedback triggers"""
        try:
            pattern = data.get('pattern', 'heartbeat')
            intensity = data.get('intensity', 50)
            duration = data.get('duration', 2000)
            
            user = SESSION_POOL.get(sid)
            if not user:
                return
            
            # Trigger haptic feedback
            success = trigger_haptic_feedback(pattern, intensity, duration)
            
            # Broadcast to persona room
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('haptic:trigger', {
                'pattern': pattern,
                'intensity': intensity,
                'duration': duration,
                'success': success,
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Haptic pattern {pattern} triggered for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error triggering haptic feedback: {e}")
    
    async def handle_haptic_stop(self, sid, data):
        """Handle haptic feedback stop"""
        try:
            user = SESSION_POOL.get(sid)
            if not user:
                return
            
            # Stop haptic feedback
            success = self.haptic_system.stop_haptic()
            
            # Broadcast to persona room
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('haptic:stop', {
                'success': success,
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Haptic feedback stopped for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error stopping haptic feedback: {e}")
    
    async def handle_vr_scene_start(self, sid, data):
        """Handle VR scene start"""
        try:
            scene_id = data.get('sceneId')
            scene_type = data.get('sceneType', 'pre_created')
            
            user = SESSION_POOL.get(sid)
            if not user:
                return
            
            # Start VR session
            success = start_vr_session(scene_id)
            
            # Broadcast to persona room
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('vr:scene:start', {
                'scene': scene_id,
                'sceneType': scene_type,
                'success': success,
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            # Simulate VR progress
            await self._simulate_vr_progress(sid, scene_id, room_name)
            
            logger.info(f"VR scene {scene_id} started for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error starting VR scene: {e}")
    
    async def handle_vr_scene_stop(self, sid, data):
        """Handle VR scene stop"""
        try:
            user = SESSION_POOL.get(sid)
            if not user:
                return
            
            # Stop VR session
            success = self.vr_integration.stop_session()
            
            # Broadcast to persona room
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('vr:scene:end', {
                'success': success,
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"VR scene stopped for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error stopping VR scene: {e}")
    
    async def handle_voice_speak(self, sid, data):
        """Handle voice synthesis"""
        try:
            text = data.get('text', '')
            emotion = data.get('emotion', 'neutral')
            pitch = data.get('pitch', 1.0)
            rate = data.get('rate', 1.0)
            volume = data.get('volume', 1.0)
            
            user = SESSION_POOL.get(sid)
            if not user:
                return
            
            # Start voice synthesis
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('voice:speak:start', {
                'text': text,
                'emotion': emotion,
                'pitch': pitch,
                'rate': rate,
                'volume': volume,
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            # Simulate voice synthesis
            await asyncio.sleep(len(text) * 0.1)  # Rough timing
            
            await sio.emit('voice:speak:end', {
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Voice synthesis completed for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error in voice synthesis: {e}")
    
    async def handle_voice_stop(self, sid, data):
        """Handle voice stop"""
        try:
            user = SESSION_POOL.get(sid)
            if not user:
                return
            
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('voice:speak:end', {
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Voice stopped for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error stopping voice: {e}")
    
    async def handle_voice_listen_start(self, sid, data):
        """Handle voice listening start"""
        try:
            user = SESSION_POOL.get(sid)
            if not user:
                return
            
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('voice:listen:start', {
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Voice listening started for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error starting voice listening: {e}")
    
    async def handle_voice_listen_stop(self, sid, data):
        """Handle voice listening stop"""
        try:
            user = SESSION_POOL.get(sid)
            if not user:
                return
            
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('voice:listen:end', {
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Voice listening stopped for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error stopping voice listening: {e}")
    
    async def handle_memory_create(self, sid, data):
        """Handle memory creation"""
        try:
            memory_data = data.get('memory', {})
            user = SESSION_POOL.get(sid)
            
            if not user:
                return
            
            # Store memory in MongoDB
            memory_id = await mongodb_client.store_memory({
                **memory_data,
                'user_id': user.get('id'),
                'session_id': sid
            })
            
            # Broadcast memory notification
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('memory:notification', {
                'type': 'memory_created',
                'title': 'New Memory Created',
                'message': f"Memory '{memory_data.get('title', 'Untitled')}' has been stored",
                'memoryId': memory_id,
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Memory created for user {user.get('id')} with ID {memory_id}")
            
        except Exception as e:
            logger.error(f"Error creating memory: {e}")
    
    async def handle_memory_update(self, sid, data):
        """Handle memory updates"""
        try:
            memory_data = data.get('memory', {})
            memory_id = data.get('memory_id')
            user = SESSION_POOL.get(sid)
            
            if not user or not memory_id:
                return
            
            # Update memory in MongoDB
            success = await mongodb_client.update_memory(memory_id, memory_data)
            
            # Broadcast memory notification
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('memory:notification', {
                'type': 'memory_updated',
                'title': 'Memory Updated',
                'message': f"Memory '{memory_data.get('title', 'Untitled')}' has been updated",
                'memoryId': memory_id,
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Memory updated for user {user.get('id')} with ID {memory_id}")
            
        except Exception as e:
            logger.error(f"Error updating memory: {e}")
    
    async def handle_relationship_analyze(self, sid, data):
        """Handle relationship analysis"""
        try:
            analysis_data = data.get('analysis', {})
            user = SESSION_POOL.get(sid)
            
            if not user:
                return
            
            # Analyze relationship
            analysis_result = analyze_relationship_health(analysis_data)
            
            # Broadcast relationship insight
            session_state = SESSION_STATES.get(sid, {})
            persona = session_state.get('persona', 'unified_ai')
            room_name = f"persona:{persona}"
            
            await sio.emit('relationship:insight', {
                'type': 'health_analysis',
                'message': f"Relationship health score: {analysis_result.get('health_score', 0)}",
                'user_id': user.get('id'),
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
            logger.info(f"Relationship analyzed for user {user.get('id')}")
            
        except Exception as e:
            logger.error(f"Error analyzing relationship: {e}")
    
    async def _simulate_animation_progress(self, sid, gesture, room_name):
        """Simulate avatar animation progress"""
        try:
            for progress in range(0, 101, 10):
                await sio.emit('avatar:animation:progress', {
                    'progress': progress,
                    'gesture': gesture,
                    'timestamp': datetime.now().isoformat()
                }, room=room_name)
                await asyncio.sleep(0.2)
            
            await sio.emit('avatar:animation:complete', {
                'gesture': gesture,
                'timestamp': datetime.now().isoformat()
            }, room=room_name)
            
        except Exception as e:
            logger.error(f"Error simulating animation progress: {e}")
    
    async def _simulate_vr_progress(self, sid, scene_id, room_name):
        """Simulate VR scene progress"""
        try:
            for progress in range(0, 101, 5):
                await sio.emit('vr:scene:progress', {
                    'progress': progress,
                    'scene': scene_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_name)
                await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error simulating VR progress: {e}")

# Global instance
phase3_handlers = Phase3WebSocketHandlers()

# Setup function to be called during app startup
async def setup_phase3_websocket_handlers():
    """Setup Phase 3 WebSocket handlers"""
    await phase3_handlers.setup_handlers() 
