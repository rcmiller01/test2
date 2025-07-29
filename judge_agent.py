"""Judge Agent evaluates persona consistency and memory recall."""

import re
from typing import Dict, List, Optional

from persona_instruction_manager import PersonaInstructionManager
from memory_system import MemorySystem


class JudgeAgent:
    """Simple agent that scores responses for persona adherence and memory usage."""

    def __init__(self, manifesto_path: str = "personas/manifestos", memory_dir: str = "memory") -> None:
        self.persona_manager = PersonaInstructionManager(manifesto_path)
        self.memory_system = MemorySystem(memory_dir)

    def evaluate(self, session_id: str, content: str) -> Dict[str, float]:
        """Evaluate content with persona and memory context."""
        context = self.memory_system.get_session_context(session_id)
        active_persona = self.persona_manager.active_persona
        recent_memories = self.memory_system.search_recent_events(limit=5)

        persona_score = self.score_persona(content, active_persona)
        memory_score = self.score_memory(content, recent_memories)

        return {
            "persona_score": persona_score,
            "memory_score": memory_score,
            "sentiment_trend": context.get("sentiment_trend", 0.0),
        }

    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def score_persona(self, content: str, persona: Optional[object]) -> float:
        """Compare content with keywords from the persona manifesto."""
        if not persona:
            return 0.0
        parts = [
            persona.core_identity,
            " ".join(getattr(persona, "primary_goals", [])),
            " ".join(getattr(persona, "personality_traits", [])),
            persona.communication_style,
            persona.tone_guidelines,
            " ".join(getattr(persona, "behavior_constraints", [])),
            persona.custom_instructions,
        ]
        keywords = set(self._extract_keywords(" ".join(parts)))
        if not keywords:
            return 0.0
        content_words = set(self._extract_keywords(content))
        matches = len(keywords.intersection(content_words))
        return matches / len(keywords)

    def score_memory(self, content: str, memories: List[Dict[str, any]]) -> float:
        """Reward references to recent memory snippets."""
        if not memories:
            return 0.0
        content_words = set(self._extract_keywords(content))
        match_count = 0
        for entry in memories:
            preview = entry.get("preview", "")
            words = set(self._extract_keywords(preview))
            if content_words.intersection(words):
                match_count += 1
        return match_count / len(memories)

