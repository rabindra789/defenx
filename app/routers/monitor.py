# app/routers/monitor.py

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List, Optional
from app.core import scanner

router = APIRouter()

@router.post("/scan", response_model=None)
async def trigger_scan(background_tasks: BackgroundTasks, ports: Optional[List[int]] = None):
    try:
        target = scanner.CONFIG.get("scan_target", "127.0.0.1")
        background_tasks.add_task(scanner.perform_scan, target, ports)
        return {"message": "Scan scheduled", "target": target}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan-now", response_model=None)
async def trigger_scan_now(ports: Optional[List[int]] = None):
    try:
        target = scanner.CONFIG.get("scan_target", "127.0.0.1")
        result = await scanner.perform_scan(target, ports)
        return {"message": "scan completed", "target": target, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/last")
async def last_scan():
    last = scanner.get_last_scan()
    if not last:
        return {"message": "no scans yet"}
    return last
