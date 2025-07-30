from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..orchestrator import orchestrator

router = APIRouter()

@router.get('/api/analytics/realtime')
async def get_realtime_analytics():
    return orchestrator.analytics_logger.get_real_time_stats()

@router.get('/api/logs/export')
async def export_analytics():
    path = orchestrator.analytics_logger.export_analytics()
    return {'export_path': path}

@router.get('/api/reflection/summary')
async def get_reflection_summary():
    if not orchestrator.reflection_engine:
        raise HTTPException(status_code=503, detail='Reflection engine not available')
    return orchestrator.reflection_engine.get_reflection_summary()

@router.get('/api/metrics/realtime')
async def get_realtime_metrics():
    if not orchestrator.metrics_collector:
        raise HTTPException(status_code=503, detail='Metrics collector not available')
    return orchestrator.metrics_collector.get_realtime_status()
