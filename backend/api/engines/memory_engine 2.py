from google.cloud import firestore
from datetime import datetime

db = firestore.Client()
collection = db.collection("memory_log")

def save_memory(persona, trigger_type, mood, symbol, summary):
    doc = {
        "timestamp": datetime.utcnow().isoformat(),
        "persona": persona,
        "trigger_type": trigger_type,
        "mood": mood,
        "symbol": symbol,
        "summary": summary
    }
    collection.add(doc)
    return True
