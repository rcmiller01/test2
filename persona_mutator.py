"""Persona Mutator Module

Generates mutated variants of existing personas for testing.
"""

from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class PersonaMutator:
    """Create randomized mutations of persona definitions."""

    def __init__(self, base_dir: str = "personas", output_dir: str = "mutated_personas"):
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_persona(self, file_path: str) -> Dict[str, Any]:
        """Load a persona definition from JSON."""
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def mutate(self, base_persona: Dict[str, Any], intensity: str = "moderate") -> Dict[str, Any]:
        """Return a new persona mutated from ``base_persona``."""
        mutated = json.loads(json.dumps(base_persona))  # deep copy

        level_map = {"light": 1, "moderate": 2, "radical": 4}
        level = level_map.get(intensity, 2)

        possible_tones = [
            "empathetic",
            "assertive",
            "playful",
            "professional",
            "casual",
        ]
        handlers = ["DOLPHIN", "KIMI", "OPENROUTER"]
        verbosity = ["short", "medium", "long"]

        for _ in range(level):
            field = random.choice(["tone", "temperature", "handler", "emotion", "verbosity"])
            if field == "tone":
                if "prompt_style" not in mutated:
                    mutated["prompt_style"] = {}
                mutated["prompt_style"]["tone"] = random.choice(possible_tones)
            elif field == "temperature":
                mutated["response_temperature"] = round(random.uniform(0.2, 1.0), 2)
            elif field == "handler":
                mutated["preferred_handler"] = random.choice(handlers)
            elif field == "emotion":
                base_value = float(mutated.get("emotional_responsiveness", 0.5))
                delta = random.uniform(-0.3, 0.3)
                mutated["emotional_responsiveness"] = max(0.0, min(1.0, round(base_value + delta, 2)))
            elif field == "verbosity":
                mutated["response_length"] = random.choice(verbosity)

        meta = mutated.setdefault("metadata", {})
        parent_id = base_persona.get("id", meta.get("parent_id", "unknown"))
        generation = meta.get("generation", 0) + 1
        meta.update({
            "parent_id": parent_id,
            "mutation_type": intensity,
            "generation": generation,
        })

        return mutated

    def save_mutation(self, mutated_persona: Dict[str, Any], parent_id: str) -> str:
        """Save ``mutated_persona`` to disk and return the file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{parent_id}_{timestamp}.json"
        path = self.output_dir / file_name
        with open(path, "w", encoding="utf-8") as f:
            json.dump(mutated_persona, f, indent=2, ensure_ascii=False)
        return str(path)


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate mutated personas")
    parser.add_argument("persona_file", help="Path to base persona JSON")
    parser.add_argument("--intensity", choices=["light", "moderate", "radical"], default="moderate")
    parser.add_argument("--output-dir", default="mutated_personas", help="Directory for mutated personas")

    args = parser.parse_args()

    mutator = PersonaMutator(output_dir=args.output_dir)
    base = mutator.load_persona(args.persona_file)
    mutated = mutator.mutate(base, args.intensity)
    path = mutator.save_mutation(mutated, base.get("id", "persona"))
    print(f"Saved mutated persona to {path}")


if __name__ == "__main__":
    _cli()
