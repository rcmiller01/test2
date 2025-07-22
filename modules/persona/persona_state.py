import asyncio
from backend.database.mongodb_client import mongodb_client

async def get_active_persona() -> str:
    if not mongodb_client.is_connected:
        await mongodb_client.connect()
    config_collection = mongodb_client.db.get_collection("config")
    doc = await config_collection.find_one({"key": "active_persona"})
    return doc["value"] if doc else None

async def set_active_persona(name: str):
    if not mongodb_client.is_connected:
        await mongodb_client.connect()
    config_collection = mongodb_client.db.get_collection("config")
    await config_collection.update_one(
        {"key": "active_persona"},
        {"$set": {"key": "active_persona", "value": name}},
        upsert=True
    )

async def load_personas() -> dict:
    if not mongodb_client.is_connected:
        await mongodb_client.connect()
    collection = mongodb_client.db[mongodb_client.collections['personas']]
    personas = {}
    async for doc in collection.find({}):
        name = doc.get("name")
        if name:
            doc["_id"] = str(doc["_id"])
            personas[name] = doc
    return personas 