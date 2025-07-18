import requests

OPENCHAT_URL = "http://localhost:11434/api/generate"  # OpenChat endpoint

def generate_solene_response(prompt: str) -> str:
    payload = {
        "model": "openchat",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OPENCHAT_URL, json=payload)
        return response.json().get("response", "[Solene says nothing]")
    except Exception as e:
        return f"[Solene error: {e}]"
