# api_client.py
# Shared API client for mobile app integration

import requests
import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class APIConfig:
    base_url: str = "http://localhost:8000"
    timeout: int = 30
    retry_attempts: int = 3

class MiaSoleneAPIClient:
    def __init__(self, config: APIConfig = None):
        self.config = config or APIConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MiaSolene-Mobile/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request with retry logic"""
        url = f"{self.config.base_url}{endpoint}"
        
        for attempt in range(self.config.retry_attempts):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=self.config.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, timeout=self.config.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.config.retry_attempts - 1:
                    raise e
                continue
    
    # Core API Methods
    
    def get_emotion_state(self) -> Dict:
        """Get current emotion state"""
        return self._make_request('GET', '/emotion/state')
    
    def update_emotion_from_text(self, text: str) -> Dict:
        """Update emotion state from text input"""
        return self._make_request('POST', '/emotion/from_text', data={'text': text})
    
    def update_emotion_from_biometrics(self, bpm: int, hrv: int, context: str = "general") -> Dict:
        """Update emotion state from biometric data"""
        return self._make_request('POST', '/emotion/from_biometrics', 
                                data={'bpm': bpm, 'hrv': hrv, 'context': context})
    
    def get_mia_self_talk(self) -> Dict:
        """Get Mia's self-talk response"""
        return self._make_request('GET', '/mia/self_talk')
    
    def recall_emotional_memory(self, emotion: str = None, limit: int = 5) -> Dict:
        """Recall emotional memories"""
        params = {'limit': limit}
        if emotion:
            params['emotion'] = emotion
        return self._make_request('GET', '/mia/self_talk/recall', params=params)
    
    # Advanced Features API Methods
    
    def synthesize_speech(self, text: str, persona: str = "mia", 
                         emotion: str = "neutral", intensity: float = 0.5) -> Dict:
        """Synthesize emotional speech"""
        return self._make_request('POST', '/api/advanced/tts/synthesize', 
                                data={
                                    'text': text,
                                    'persona': persona,
                                    'emotion': emotion,
                                    'intensity': intensity
                                })
    
    def get_tts_status(self) -> Dict:
        """Get TTS system status"""
        return self._make_request('GET', '/api/advanced/tts/status')
    
    def store_memory(self, memory_type: str, title: str, description: str,
                    emotional_intensity: float, emotions: List[str],
                    personas_involved: List[str], context: Dict = None,
                    relationship_impact: float = 0.0, tags: List[str] = None) -> Dict:
        """Store a romantic memory"""
        return self._make_request('POST', '/api/advanced/memory/store',
                                data={
                                    'memory_type': memory_type,
                                    'title': title,
                                    'description': description,
                                    'emotional_intensity': emotional_intensity,
                                    'emotions': emotions,
                                    'personas_involved': personas_involved,
                                    'context': context or {},
                                    'relationship_impact': relationship_impact,
                                    'tags': tags or []
                                })
    
    def recall_memories(self, emotion: str = None, persona: str = None,
                       memory_type: str = None, limit: int = 10) -> Dict:
        """Recall memories with filters"""
        params = {'limit': limit}
        if emotion:
            params['emotion'] = emotion
        if persona:
            params['persona'] = persona
        if memory_type:
            params['memory_type'] = memory_type
        return self._make_request('GET', '/api/advanced/memory/recall', params=params)
    
    def get_relationship_insights(self) -> Dict:
        """Get relationship insights"""
        return self._make_request('GET', '/api/advanced/memory/insights')
    
    def update_avatar_mood(self, emotion: str, intensity: float = 0.5, 
                          context: Dict = None) -> Dict:
        """Update avatar mood"""
        return self._make_request('POST', '/api/advanced/avatar/mood',
                                data={
                                    'emotion': emotion,
                                    'intensity': intensity,
                                    'context': context or {}
                                })
    
    def trigger_avatar_gesture(self, gesture: str, intensity: float = 0.5) -> Dict:
        """Trigger avatar gesture"""
        return self._make_request('POST', f'/api/advanced/avatar/gesture/{gesture}',
                                params={'intensity': intensity})
    
    def get_avatar_state(self) -> Dict:
        """Get current avatar state"""
        return self._make_request('GET', '/api/advanced/avatar/state')
    
    def customize_avatar(self, eye_color: str = None, hair_style: str = None,
                        clothing: str = None, background: str = None,
                        lighting: str = None) -> Dict:
        """Customize avatar appearance"""
        data = {}
        if eye_color:
            data['eye_color'] = eye_color
        if hair_style:
            data['hair_style'] = hair_style
        if clothing:
            data['clothing'] = clothing
        if background:
            data['background'] = background
        if lighting:
            data['lighting'] = lighting
        return self._make_request('POST', '/api/advanced/avatar/customize', data=data)
    
    # Phase 3 Features API Methods
    
    def trigger_haptic_feedback(self, pattern: str, intensity: str = "moderate",
                               duration: float = 2.0, location: str = "general",
                               emotional_context: str = "romantic") -> Dict:
        """Trigger haptic feedback"""
        return self._make_request('POST', '/api/phase3/haptic/trigger',
                                data={
                                    'pattern': pattern,
                                    'intensity': intensity,
                                    'duration': duration,
                                    'location': location,
                                    'emotional_context': emotional_context
                                })
    
    def trigger_romantic_haptic(self, action: str, intensity: str = "moderate") -> Dict:
        """Trigger romantic haptic action"""
        return self._make_request('POST', '/api/phase3/haptic/romantic',
                                params={'action': action, 'intensity': intensity})
    
    def start_biometric_monitoring(self) -> Dict:
        """Start biometric monitoring"""
        return self._make_request('POST', '/api/phase3/biometric/start')
    
    def update_biometric_reading(self, reading_type: str, value: float, 
                               context: str = "general") -> Dict:
        """Update biometric reading"""
        return self._make_request('POST', '/api/phase3/biometric/reading',
                                data={
                                    'type': reading_type,
                                    'value': value,
                                    'context': context
                                })
    
    def get_romantic_sync_status(self) -> Dict:
        """Get romantic sync status"""
        return self._make_request('GET', '/api/phase3/biometric/romantic-sync')
    
    def start_vr_session(self, scene_type: str = "romantic_garden") -> Dict:
        """Start VR session"""
        return self._make_request('POST', '/api/phase3/vr/start',
                                data={'scene_type': scene_type})
    
    def trigger_vr_interaction(self, interaction_type: str, intensity: float = 0.5) -> Dict:
        """Trigger VR interaction"""
        return self._make_request('POST', '/api/phase3/vr/interaction',
                                data={
                                    'interaction_type': interaction_type,
                                    'intensity': intensity
                                })
    
    def get_relationship_health(self) -> Dict:
        """Get relationship health analysis"""
        return self._make_request('GET', '/api/phase3/relationship/health')
    
    def get_relationship_advice(self, issue_type: str, context: Dict = None) -> Dict:
        """Get relationship advice"""
        return self._make_request('POST', '/api/phase3/relationship/advice',
                                data={
                                    'issue_type': issue_type,
                                    'context': context or {}
                                })
    
    # Integrated Experience Methods
    
    def create_romantic_experience(self, text: str, emotion: str = "love",
                                 intensity: float = 0.7, include_tts: bool = True,
                                 include_avatar: bool = True, include_memory: bool = True) -> Dict:
        """Create integrated romantic experience"""
        return self._make_request('POST', '/api/advanced/integrated/romantic_experience',
                                data={
                                    'text': text,
                                    'emotion': emotion,
                                    'intensity': intensity,
                                    'include_tts': include_tts,
                                    'include_avatar': include_avatar,
                                    'include_memory': include_memory
                                })
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        return self._make_request('GET', '/api/advanced/integrated/status')
    
    def health_check(self) -> Dict:
        """Health check for all systems"""
        return self._make_request('GET', '/api/advanced/health')

# Convenience functions for common operations
def create_api_client(base_url: str = "http://localhost:8000") -> MiaSoleneAPIClient:
    """Create API client with default configuration"""
    config = APIConfig(base_url=base_url)
    return MiaSoleneAPIClient(config)

def test_connection(client: MiaSoleneAPIClient) -> bool:
    """Test API connection"""
    try:
        result = client.health_check()
        return result.get('success', False)
    except Exception:
        return False 