import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException
from ..orchestrator import orchestrator

router = APIRouter()


def _sanitize_path(env_var: str, default: str) -> str:
    path = os.getenv(env_var, default)
    path = os.path.normpath(path)
    if not Path(path).is_file():
        raise HTTPException(status_code=400, detail=f'Invalid path: {path}')
    return path

@router.post('/api/quantization/start')
async def start_quant_loop():
    bootloader_path = _sanitize_path('QUANT_BOOTLOADER_PATH', 'autopilot_bootloader.py')
    try:
        proc = subprocess.Popen(['python', bootloader_path, '--launch-now'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
        return {'status': 'started', 'pid': proc.pid, 'bootloader': bootloader_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/api/quantization/stop')
async def stop_quant_loop():
    bootloader_path = _sanitize_path('QUANT_BOOTLOADER_PATH', 'autopilot_bootloader.py')
    try:
        result = subprocess.run(['python', bootloader_path, '--stop'], capture_output=True, text=True, timeout=30)
        return {'status': 'stopped', 'output': result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/quantization/status')
async def quant_status():
    bootloader_path = _sanitize_path('QUANT_BOOTLOADER_PATH', 'autopilot_bootloader.py')
    try:
        result = subprocess.run(['python', bootloader_path, '--status'], capture_output=True, text=True, timeout=30)
        status = {'available': result.returncode == 0, 'timestamp': datetime.now().isoformat()}
        if result.returncode == 0:
            try:
                status.update(json.loads(result.stdout.splitlines()[-1]))
            except Exception:
                status['raw'] = result.stdout
        return status
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
