import requests

MYTHOMAX_URL = "http://localhost:11434/api/generate"  # MythoMax endpoint

def generate_mia_response(prompt: str) -> str:
    payload = {
        "model": "mythomax",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(MYTHOMAX_URL, json=payload)
        return response.json().get("response", "[Mia is quiet]")
    except Exception as e:
        return f"[Mia error: {e}]"
