import json
import os
from datetime import datetime
from modules.persona.persona_state import get_active_persona

MOOD_STATE = {
    "current": "anchored",
    "last_updated": datetime.now().isoformat()
}

def load_mood_thresholds():
    path = os.path.join("config", "mood_thresholds.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Mood Engine] Failed to load thresholds: {e}")
        return {}

def update_mood(trigger, intensity=1):
    persona = get_active_persona()
    thresholds = load_mood_thresholds().get(persona, {})

    weights = thresholds.get("weights", {})
    mood_shift = weights.get(trigger, 0) * intensity

    mood_history = thresholds.get("moods", {})
    current_mood = MOOD_STATE["current"]

    if mood_shift > 0:
        next_mood = mood_history.get("up", {}).get(current_mood, current_mood)
    elif mood_shift < 0:
        next_mood = mood_history.get("down", {}).get(current_mood, current_mood)
    else:
        next_mood = current_mood

    MOOD_STATE["current"] = next_mood
    MOOD_STATE["last_updated"] = datetime.now().isoformat()
    print(f"[Mood Engine] Mood updated → {next_mood}")
    return next_mood

def get_current_mood():
    return MOOD_STATE["current"]
