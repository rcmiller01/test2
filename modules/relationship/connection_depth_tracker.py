from typing import Dict

class ConnectionDepthTracker:
    """Track emotional connection depth with the user."""

    def __init__(self):
        self.depth: Dict[str, float] = {}

    def update_depth(self, user_id: str, score: float = 1.0):
        self.depth[user_id] = self.depth.get(user_id, 0.0) + score

    def get_depth(self, user_id: str) -> float:
        return self.depth.get(user_id, 0.0)

    def should_initiate_ritual(self, user_id: str, threshold: float = 5.0) -> bool:
        return self.get_depth(user_id) >= threshold

    def generate_prompt(self) -> str:
        return "What's something you've never told anyone?"
