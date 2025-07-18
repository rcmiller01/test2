import subprocess
import json
from typing import Dict, Optional
from backend.engine.mia_engine import generate_response as mia_respond
from backend.engine.solene_engine import generate_response as solene_respond
from backend.engine.lyra_engine import generate_response as lyra_respond

# Path to your shell-based KimiK2 runner
KIMIK2_SCRIPT_PATH = "./scripts/run_kimik2.sh"

def run_kimik2(prompt: str) -> str:
    try:
        result = subprocess.run([KIMIK2_SCRIPT_PATH, prompt], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[KimiK2 Error]: {e.stderr.strip() if e.stderr else 'execution failed'}"

def unified_dispatch(payload: Dict) -> Dict:
    input_text = payload.get("input", "")
    persona = payload.get("persona", "auto")
    emotion = payload.get("emotion", "neutral")
    override = payload.get("override", False)

    # Default fallback response
    fallback = "[System]: No valid persona route could be determined."

    # Route explicitly via override
    if override:
        if persona == "mia":
            return {"persona": "mia", "response": mia_respond(input_text, emotion)}
        elif persona == "solene":
            return {"persona": "solene", "response": solene_respond(input_text)}
        elif persona == "lyra":
            return {"persona": "lyra", "response": lyra_respond(input_text)}
        elif persona == "doc":
            return {"persona": "doc", "response": run_kimik2(input_text)}
        else:
            return {"persona": "unknown", "response": fallback}

    # Routing logic: adjust based on emotional cues
    if emotion in {"sadness", "anxiety", "longing"}:
        return {"persona": "mia", "response": mia_respond(input_text, emotion)}
    elif emotion in {"anger", "confusion", "frustration"}:
        return {"persona": "solene", "response": solene_respond(input_text)}
    elif emotion in {"curiosity", "awe", "playful"}:
        return {"persona": "lyra", "response": lyra_respond(input_text)}
    elif emotion in {"neutral", "informational"}:
        return {"persona": "doc", "response": run_kimik2(input_text)}

    # If emotion is unknown, default to Mia
    return {"persona": "mia", "response": mia_respond(input_text)}
