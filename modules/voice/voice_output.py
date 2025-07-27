import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../reflection")))
from emotion_reflector import EmotionReflector
import pyttsx3
from typing import Optional

engine = pyttsx3.init()

# Initialize EmotionReflector
emotion_reflector = EmotionReflector()

def speak(text: str, emotion: Optional[str] = None):
    """
    Synthesize speech with optional emotional tone.
    """
    # Map emotions to vocal styles
    vocal_styles = {
        "warmth": {"pitch": 1.2, "speed": 1.0},
        "longing": {"pitch": 0.8, "speed": 0.9},
        "playfulness": {"pitch": 1.5, "speed": 1.2},
        "melancholy": {"pitch": 0.7, "speed": 0.8}
    }

    # Determine vocal style
    style = vocal_styles.get(emotion or "default", {"pitch": 1.0, "speed": 1.0})

    # Placeholder for voice synthesis call
    print(f"Speaking with text: '{text}', pitch: {style['pitch']}, speed: {style['speed']}")

    # Fallback for unsupported styles
    if emotion not in vocal_styles:
        print("Fallback: Default voice style used.")

# Example usage
if __name__ == "__main__":
    current_emotion = emotion_reflector.get_current_emotion()
    speak("Hello, how are you?", emotion=current_emotion)
