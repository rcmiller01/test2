import os
import aiohttp
import logging
import time

logger = logging.getLogger(__name__)

MCP_HOST = os.getenv("MCP_HOST", "http://localhost:8000")

async def route_to_mcp(task_request: dict) -> dict:
    """Send a structured task to the MCP server."""
    url = f"{MCP_HOST}/api/mcp/route-task"
    start = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=task_request, timeout=10) as resp:
                resp.raise_for_status()
                data = await resp.json()
        logger.info(
            "Routed to MCP: intent_type=%s request_id=%s time_ms=%d",
            task_request.get("intent_type"),
            task_request.get("request_id"),
            int((time.time() - start) * 1000),
        )
        return data
    except Exception as e:
        logger.error("MCP routing failed: %s", e)
        return {"error": str(e)}
