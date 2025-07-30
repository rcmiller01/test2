from fastapi import APIRouter, HTTPException
from datetime import datetime

from typing import Optional


from ..orchestrator import orchestrator

router = APIRouter()


@router.get("/api/analytics/realtime")
async def get_realtime_analytics():
    return orchestrator.analytics_logger.get_real_time_stats()

@router.get("/api/analytics/daily")
async def get_daily_analytics(days: int = 7):
    return orchestrator.analytics_logger.get_daily_analytics(days)

@router.get("/api/analytics/performance")
async def get_performance_report():
    return orchestrator.analytics_logger.get_handler_performance_report()

@router.get("/api/logs/search")
async def search_logs(query: str, log_type: str = "routing", hours: int = 24, limit: int = 50):
    results = orchestrator.analytics_logger.search_logs(query, log_type, hours, limit)
    return {"query": query, "results": results, "count": len(results)}

@router.get("/api/logs/export")
async def export_analytics():
    export_path = orchestrator.analytics_logger.export_analytics()
    return {"export_path": export_path}

@router.post("/api/vote_preference")
async def vote_preference(vote):
    vote_data = vote.dict()
    vote_data["timestamp"] = datetime.now().isoformat()
    try:
        stats = orchestrator.analytics_logger.log_preference_vote(vote_data)
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to record vote")

@router.post("/api/system/cleanup")
async def cleanup_system(days_to_keep: int = 30):
    cleaned = orchestrator.analytics_logger.cleanup_old_logs(days_to_keep)
    return {"cleaned_entries": cleaned}

@router.get("/api/system/health")
async def system_health():
    analytics = orchestrator.analytics_logger.get_real_time_stats()
    memory = orchestrator.memory_system.get_memory_summary()
    persona = orchestrator.personality_system.get_current_persona()
    health_factors = []
    if analytics.get("handler_details"):
        avg_success_rate = sum(h.get("success_rate", 0) for h in analytics["handler_details"].values()) / len(analytics["handler_details"])
        health_factors.append(avg_success_rate)
    active_sessions = memory["short_term"]["active_sessions"]
    memory_health = max(0, 1.0 - (active_sessions / 50))
    health_factors.append(memory_health)
    avg_latency = analytics.get("performance", {}).get("avg_latency_seconds", 0)
    latency_health = max(0, 1.0 - (avg_latency / 10))
    health_factors.append(latency_health)
    overall_health = sum(health_factors) / len(health_factors) if health_factors else 0.5
    if overall_health >= 0.8:
        health_status = "excellent"
    elif overall_health >= 0.6:
        health_status = "good"
    elif overall_health >= 0.4:
        health_status = "fair"
    else:
        health_status = "poor"
    return {
        "health_score": round(overall_health, 3),
        "health_status": health_status,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "analytics": analytics,
            "memory": memory,
            "personality": {
                "current": persona["name"],
                "icon": persona["icon"]
            }
        }
    }
