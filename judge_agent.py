class JudgeAgent:
    """Simple heuristic-based response evaluator."""

    def evaluate(self, response: str, session_context: dict) -> dict:
        persona = session_context.get("persona", "unknown")
        length_score = min(len(response) / 100, 1.0)
        persona_alignment = 1.0 if persona.lower() in response.lower() else 0.5
        relevance = 1.0 if session_context.get("session_context") else 0.8
        overall = round((length_score + persona_alignment + relevance) / 3, 2)
        return {
            "length_score": round(length_score, 2),
            "persona_alignment": round(persona_alignment, 2),
            "relevance": round(relevance, 2),
            "overall": overall
        }
