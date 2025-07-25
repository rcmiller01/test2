from typing import Dict, Any, Tuple
import math

def analyze_movement(acceleration: Dict[str, float], gyroscope: Dict[str, float]) -> str:
    """Analyze movement patterns from accelerometer and gyroscope data"""
    if not acceleration or not gyroscope:
        return "unknown"
    
    # Calculate movement magnitude
    accel_magnitude = math.sqrt(
        acceleration.get('x', 0)**2 + 
        acceleration.get('y', 0)**2 + 
        acceleration.get('z', 0)**2
    )
    
    gyro_magnitude = math.sqrt(
        gyroscope.get('x', 0)**2 + 
        gyroscope.get('y', 0)**2 + 
        gyroscope.get('z', 0)**2
    )
    
    # Classify movement
    if accel_magnitude < 0.1 and gyro_magnitude < 0.1:
        return "still"
    elif accel_magnitude < 0.5:
        return "gentle_movement"
    elif accel_magnitude < 2.0:
        return "active"
    else:
        return "vigorous"

def calculate_stress_level(heart_rate: float, hrv: float, baseline_hr: float = 70) -> float:
    """Calculate stress level from heart rate and HRV"""
    hr_stress = abs(heart_rate - baseline_hr) / baseline_hr
    hrv_stress = max(0, (50 - hrv) / 50)  # Lower HRV = higher stress
    return min(1.0, (hr_stress + hrv_stress) / 2)

def analyze_voice_stress(voice_indicators: Dict[str, float]) -> float:
    """Analyze voice stress indicators"""
    if not voice_indicators:
        return 0.0
        
    stress_factors = []
    
    # Pitch variation (higher = more stressed)
    if 'pitch_variance' in voice_indicators:
        stress_factors.append(min(1.0, voice_indicators['pitch_variance'] / 100))
    
    # Speaking rate (too fast or slow = stressed)
    if 'speaking_rate' in voice_indicators:
        normal_rate = 150  # words per minute
        rate_stress = abs(voice_indicators['speaking_rate'] - normal_rate) / normal_rate
        stress_factors.append(min(1.0, rate_stress))
    
    # Voice tremor
    if 'tremor_level' in voice_indicators:
        stress_factors.append(voice_indicators['tremor_level'])
    
    return sum(stress_factors) / len(stress_factors) if stress_factors else 0.0

async def process_biometrics_for_emotion(biometric_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process biometric data and return emotional state"""
    emotional_state = {
        "valence": 0.0,  # -1 to 1
        "arousal": 0.5,  # 0 to 1
        "stress_level": 0.0,
        "energy_level": 0.5,
        "mood": "neutral"
    }
    
    # Process heart rate
    if biometric_data.get('heart_rate'):
        hr = biometric_data['heart_rate']
        if hr > 100:
            emotional_state["arousal"] = min(1.0, 0.5 + (hr - 100) / 100)
            emotional_state["energy_level"] = min(1.0, 0.5 + (hr - 70) / 100)
        elif hr < 60:
            emotional_state["arousal"] = max(0.0, 0.5 - (60 - hr) / 60)
            emotional_state["energy_level"] = max(0.0, 0.5 - (70 - hr) / 70)
    
    # Process HRV
    if biometric_data.get('heart_rate_variability'):
        hrv = biometric_data['heart_rate_variability']
        if hrv < 20:
            emotional_state["stress_level"] = min(1.0, (20 - hrv) / 20)
            emotional_state["valence"] = max(-1.0, emotional_state["valence"] - 0.5)
        elif hrv > 50:
            emotional_state["valence"] = min(1.0, emotional_state["valence"] + 0.3)
    
    # Process voice stress
    if biometric_data.get('voice_stress_indicators'):
        voice_stress = analyze_voice_stress(biometric_data['voice_stress_indicators'])
        emotional_state["stress_level"] = max(emotional_state["stress_level"], voice_stress)
        if voice_stress > 0.7:
            emotional_state["valence"] = max(-1.0, emotional_state["valence"] - 0.4)
    
    # Determine mood based on valence and arousal
    valence = emotional_state["valence"]
    arousal = emotional_state["arousal"]
    
    if valence > 0.3 and arousal > 0.6:
        emotional_state["mood"] = "excited"
    elif valence > 0.3 and arousal < 0.4:
        emotional_state["mood"] = "content"
    elif valence < -0.3 and arousal > 0.6:
        emotional_state["mood"] = "anxious"
    elif valence < -0.3 and arousal < 0.4:
        emotional_state["mood"] = "sad"
    elif arousal > 0.7:
        emotional_state["mood"] = "energetic"
    elif arousal < 0.3:
        emotional_state["mood"] = "calm"
    else:
        emotional_state["mood"] = "neutral"
    
    return emotional_state