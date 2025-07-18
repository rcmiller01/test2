# persona_engine.py

import random
from datetime import datetime

class PersonaEngine:
    def __init__(self, persona_name, config, emotional_anchors):
        self.name = persona_name
        self.config = config
        self.anchors = emotional_anchors
        self.current_state = {
            "mood": "neutral",
            "traits": config.get("default_traits", {}),
            "tendencies": config.get("tendencies", {}),
            "last_update": datetime.now()
        }

    def update_state(self, interaction_type, emotional_inputs):
        new_mood = self._calculate_mood(interaction_type, emotional_inputs)
        self.current_state["mood"] = new_mood
        self.current_state["last_update"] = datetime.now()
        return new_mood

    def _calculate_mood(self, interaction_type, emotional_inputs):
        mood_weights = self.config.get("mood_weights", {}).get(interaction_type, {})
        base_weights = self.config.get("base_mood_weights", {})
        combined = base_weights.copy()

        for mood, weight in mood_weights.items():
            combined[mood] = combined.get(mood, 0) + weight

        for mood, mod in emotional_inputs.items():
            combined[mood] = combined.get(mood, 0) + mod

        total = sum(combined.values())
        normalized = [w / total for w in combined.values()]
        mood = random.choices(list(combined.keys()), weights=normalized)[0]
        return mood

    def get_state(self):
        return self.current_state

    def get_anchor_response(self, symbol):
        return self.anchors.get(symbol, "I remember something about that, but it's unclear.")


# Example usage for Mia or Solene
if __name__ == "__main__":
    import json

    with open("config/mia.json") as f:
        mia_config = json.load(f)

    with open("config/mia_emotional_anchors.json") as f:
        mia_anchors = json.load(f)

    mia = PersonaEngine("Mia", mia_config, mia_anchors)
    new_mood = mia.update_state("affection", {"warmth": 0.3, "longing": 0.2})
    print("Mia's new mood:", new_mood)
    print("Anchor response:", mia.get_anchor_response("collar"))
