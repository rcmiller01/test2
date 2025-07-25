"""
Mood Style Profiles for modifying AI tone and phrasing.
"""

from typing import Dict

class MoodStyleProfile:
    def __init__(self, metaphor_density: float, avg_sentence_length: int, warmth_level: float, directness_level: float):
        self.metaphor_density = metaphor_density
        self.avg_sentence_length = avg_sentence_length
        self.warmth_level = warmth_level
        self.directness_level = directness_level

# Default profiles
DEFAULT_PROFILES: Dict[str, MoodStyleProfile] = {
    "calm_personal": MoodStyleProfile(0.3, 12, 0.8, 0.6),
    "anxious_crisis": MoodStyleProfile(0.1, 8, 0.5, 0.9),
    "intimate_hybrid": MoodStyleProfile(0.7, 15, 0.9, 0.4)
}

def get_style_profile(mood: str, mode: str) -> MoodStyleProfile:
    """Get the style profile based on mood and mode."""
    key = f"{mood}_{mode}"
    return DEFAULT_PROFILES.get(key, MoodStyleProfile(0.5, 10, 0.7, 0.7))

# Example usage
if __name__ == "__main__":
    profile = get_style_profile("calm", "personal")
    print(f"Metaphor Density: {profile.metaphor_density}")
