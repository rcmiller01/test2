import requests

QWEN_URL = "http://localhost:11434/api/generate"  # Qwen-2 Chat endpoint

def generate_lyra_response(prompt: str) -> str:
    payload = {
        "model": "qwen2-chat",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(QWEN_URL, json=payload)
        return response.json().get("response", "[Lyra is thinking...]")
    except Exception as e:
        return f"[Lyra error: {e}]"
