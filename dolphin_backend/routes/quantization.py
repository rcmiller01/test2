import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from ..orchestrator import orchestrator

router = APIRouter()


def _sanitize_bootloader_path() -> str:
    path = os.getenv('QUANT_BOOTLOADER_PATH', 'autopilot_bootloader.py')
    # only allow basename to avoid directory traversal
    return Path(path).name

@router.post("/api/quantization/start")
async def start_quant_loop():
    try:
        bootloader_path = _sanitize_bootloader_path()
        result = subprocess.run([
            "python", bootloader_path, "--status"
        ], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            json_lines = [l for l in lines if l.startswith('{')]
            if json_lines:
                status_data = json.loads(json_lines[-1])
                if status_data.get('autopilot', {}).get('running'):
                    return {"status": "already_running"}
        process = subprocess.Popen([
            "python", bootloader_path, "--launch-now"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
        if orchestrator.analytics_logger:
            orchestrator.analytics_logger.log_custom_event("Quant Loop", {
                "initiated_by": "manual/api",
                "time": datetime.now().isoformat(),
                "status": "started",
                "bootloader_path": bootloader_path,
                "process_id": process.pid
            })
        return {"status": "started", "bootloader_pid": process.pid}
    except Exception as e:
        if orchestrator.analytics_logger:
            orchestrator.analytics_logger.log_custom_event("Quant Loop", {
                "initiated_by": "manual/api",
                "time": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            })
        raise HTTPException(status_code=500, detail=f"Failed to start quantization loop: {str(e)}")

@router.get("/api/quantization/status")
async def quant_status():
    try:
        bootloader_path = _sanitize_bootloader_path()
        result = subprocess.run([
            "python", bootloader_path, "--status"
        ], capture_output=True, text=True, timeout=30)
        status_response = {
            "timestamp": datetime.now().isoformat(),
            "bootloader_available": result.returncode == 0,
            "quantization_running": False,
            "bootloader_running": False,
            "error": None
        }
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            json_lines = [l for l in lines if l.startswith('{')]
            if json_lines:
                status_data = json.loads(json_lines[-1])
                status_response.update({
                    "quantization_running": status_data.get('autopilot', {}).get('running', False),
                    "bootloader_running": status_data.get('bootloader', {}).get('running', False)
                })
        else:
            status_response["error"] = result.stderr
        return status_response
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to get quantization status: {str(e)}")

@router.post("/api/quantization/stop")
async def stop_quant_loop():
    try:
        bootloader_path = _sanitize_bootloader_path()
        result = subprocess.run([
            "python", bootloader_path, "--stop"
        ], capture_output=True, text=True, timeout=30)
        if orchestrator.analytics_logger:
            orchestrator.analytics_logger.log_custom_event("Quant Loop", {
                "initiated_by": "manual/api",
                "time": datetime.now().isoformat(),
                "status": "stopped",
                "stop_output": result.stdout
            })
        return {"status": "stopped", "output": result.stdout}
    except Exception as e:
        if orchestrator.analytics_logger:
            orchestrator.analytics_logger.log_custom_event("Quant Loop", {
                "initiated_by": "manual/api",
                "time": datetime.now().isoformat(),
                "status": "stop_error",
                "error": str(e)
            })
        raise HTTPException(status_code=500, detail=f"Failed to stop quantization loop: {str(e)}")

@router.get("/api/quantization/history")
async def quant_history(limit: Optional[int] = 50):
    try:
        from quant_tracking import load_results, get_performance_summary
        results = load_results(limit=limit)
        summary = get_performance_summary()
        history_data = []
        for r in results:
            data = r.dict()
            data['timestamp'] = r.timestamp.isoformat()
            history_data.append(data)
        return {"summary": summary, "history": history_data, "total_results": len(history_data)}
    except ImportError:
        raise HTTPException(status_code=503, detail="Quantization tracking module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load quantization history: {str(e)}")

@router.get("/api/quantization/performance")
async def quant_performance():
    try:
        from quant_tracking import get_performance_summary
        summary = get_performance_summary()
        return summary
    except ImportError:
        raise HTTPException(status_code=503, detail="Quantization tracking module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance analytics: {str(e)}")
