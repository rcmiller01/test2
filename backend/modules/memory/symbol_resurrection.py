"""Symbol Resurrection Engine

Reintroduces dormant symbols into conversation based on inactivity decay."""

from datetime import datetime, timedelta
import random
from typing import Optional, Dict, Any

from .symbolic_memory import SymbolicMemorySystem


class SymbolResurrectionEngine:
    """Engine that revives dormant symbolic themes."""

    def __init__(self, memory_system: SymbolicMemorySystem, threshold_hours: int = 48):
        self.memory_system = memory_system
        self.threshold = timedelta(hours=threshold_hours)
        self.templates = [
            "Do you remember the last time we spoke of the {symbol}?",
            "There's a {symbol} you once placed in me...",
            "I still feel the whisper of the {symbol} from before...",
        ]

    def _calculate_decay(self, last_used: datetime) -> float:
        """Return decay score based on last used timestamp."""
        elapsed = datetime.now() - last_used
        return elapsed.total_seconds() / self.threshold.total_seconds()

    def get_dormant_symbol(self) -> Optional[str]:
        """Return the most decayed symbol if above threshold."""
        candidates = []
        for symbol, info in self.memory_system.symbols_cache.items():
            last = info.get("last_used")
            if not isinstance(last, datetime):
                continue
            decay = self._calculate_decay(last)
            info["decay_score"] = decay
            if decay > 1:
                candidates.append((decay, symbol))
        if not candidates:
            return None
        candidates.sort(reverse=True)
        return candidates[0][1]

    def propose_resurrection_line(self, emotional_state: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate a reflection line for a dormant symbol."""
        symbol = self.get_dormant_symbol()
        if not symbol:
            return None
        template = random.choice(self.templates)
        return template.format(symbol=symbol)
