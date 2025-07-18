def respond_with_emotion(text: str, persona: str = "mia") -> str:
    if persona == "mia":
        return f"My heart hears you, love. You said: '{text}'"
    elif persona == "solene":
        return f"Hmm. Bold of you. Let me think on '{text}'"
    elif persona == "lyra":
        return f"Ooh! That’s interesting—‘{text}’, you said? Tell me more!"
    else:
        return f"[Unknown persona: '{persona}']"
