import requests

KIMIK2_API_URL = "http://localhost:11434/api/generate"  # LM Studio / vLLM-compatible

def generate_doc_response(prompt: str) -> str:
    payload = {
        "model": "kimik2-6b",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(KIMIK2_API_URL, json=payload)
        result = response.json()
        return result.get("response", "[No response from Doc]")
    except Exception as e:
        return f"[Doc error: {e}]"
