from backend.database.mongodb_client import mongodb_client
import asyncio

def load_personas() -> dict:
    """Load persona definitions from MongoDB."""
    loop = asyncio.get_event_loop()
    personas = {}
    async def fetch():
        if not mongodb_client.is_connected:
            await mongodb_client.connect()
        collection = mongodb_client.db[mongodb_client.collections['personas']]
        cursor = collection.find({})
        async for doc in cursor:
            name = doc.get("name")
            if name:
                doc["_id"] = str(doc["_id"])
                personas[name] = doc
        return personas
    return loop.run_until_complete(fetch()) 