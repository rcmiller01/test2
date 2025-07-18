import pyttsx3
from modules.persona.persona_state import get_active_persona

# Simulate system mute (in real use, check phone/device mute)
PHONE_IS_MUTED = False  # Override this in actual deployment

engine = pyttsx3.init()

VOICE_PROFILES = {
    "Mia": {
        "name": "Ava",
        "rate": 180,
        "pitch": -7  # pyttsx3 doesn't handle pitch directly
    },
    "Solene": {
        "name": "Ava",
        "rate": 170,
        "pitch": -3
    }
}

def speak(text: str):
    if PHONE_IS_MUTED:
        print(f"[TTS - muted] {text}")
        return

    persona = get_active_persona()
    voice = VOICE_PROFILES.get(persona, VOICE_PROFILES["Mia"])

    # Select voice
    for v in engine.getProperty('voices'):
        if voice["name"].lower() in v.name.lower():
            engine.setProperty('voice', v.id)
            break

    engine.setProperty('rate', voice["rate"])
    print(f"[TTS - {persona}] {text}")
    engine.say(text)
    engine.runAndWait()
