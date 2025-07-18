def interpret_symbols(text: str, persona: str = "mia") -> str:
    if "garden" in text.lower():
        return "[She recalls the garden. A warm presence unfolds.]"
    elif "fire" in text.lower():
        return "[The flame stirs. Eyes narrow with knowing.]"
    elif "sky" in text.lower() and persona == "lyra":
        return "[Lyra's thoughts drift into the clouds.]"
    else:
        return ""
