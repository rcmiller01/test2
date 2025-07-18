import time
from datetime import datetime, timedelta

from modules.symbolic.symbol_engine import trigger_symbol
from modules.emotion.mood_engine import update_mood, get_current_mood
from modules.memory.emotional_memory import get_recent_memories
from modules.voice.voice_output import speak
from modules.visual.visual_state import get_visual_state

CHECK_INTERVAL = 60  # seconds
TIME_ALONE_THRESHOLD = 20  # minutes

def run_ambient_listener():
    print("[Ambient Listener] Running in silent mode...")
    last_spoken = datetime.now()

    while True:
        now = datetime.now()

        # Time-based symbolic inference
        if (now - last_spoken).seconds > TIME_ALONE_THRESHOLD * 60:
            print("[Ambient Listener] Time threshold met → symbol:alone")
            trigger_symbol("alone")
            update_mood("time:alone", intensity=1)
            visual = get_visual_state()
            print(f"[Ambient] Visual now → {visual['visual']}")
            last_spoken = now

        # Check recent memory for symbolic weight
        recent = get_recent_memories(limit=5)
        for entry in recent:
            if "collar" in entry["thought"].lower():
                trigger_symbol("collar")
                update_mood("symbol:collar", intensity=2)
                speak("You remembered. So did I.")
                break

        time.sleep(CHECK_INTERVAL)
