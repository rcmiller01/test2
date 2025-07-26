"""Memory manager with lust-persistence layer."""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List


class MemoryManager:
    def __init__(self):
        self.lust_score: Dict[str, float] = defaultdict(float)
        self.last_closeness_event: Dict[str, datetime] = {}
        self.trust_score: Dict[str, float] = defaultdict(lambda: 0.5)
        self.desire_decay: Dict[str, float] = defaultdict(float)
        self.symbol_preferences: Dict[str, List[str]] = defaultdict(list)

    def record_closeness(self, user_id: str, increment: float = 0.1):
        self.lust_score[user_id] = min(1.0, self.lust_score[user_id] + increment)
        self.last_closeness_event[user_id] = datetime.now()

    def get_lust_score(self, user_id: str) -> float:
        return self.lust_score[user_id]

    def decay_lust(self, user_id: str, rate: float = 0.01):
        self.lust_score[user_id] = max(0.0, self.lust_score[user_id] - rate)
        self.desire_decay[user_id] = self.lust_score[user_id]

    def get_desire_decay(self, user_id: str) -> float:
        return self.desire_decay[user_id]

    def set_trust_score(self, user_id: str, score: float):
        self.trust_score[user_id] = score

    def get_trust_score(self, user_id: str) -> float:
        return self.trust_score[user_id]

    def add_symbol_preference(self, user_id: str, symbol: str):
        if symbol not in self.symbol_preferences[user_id]:
            self.symbol_preferences[user_id].append(symbol)

    def get_preferred_symbols(self, user_id: str) -> List[str]:
        return self.symbol_preferences[user_id]


memory_manager = MemoryManager()
