# app/routers/monitor.py

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from app.core import scanner

router = APIRouter()

# Trigger a scan on this server
@router.post("/scan", response_model=None)
async def trigger_scan(
    target: str = Query(..., description="IP or hostname to scan"),
    ports: Optional[List[int]] = Query(None, description="List of ports to scan"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Trigger a scan on a target. Uses background tasks if provided.
    """
    try:
        if background_tasks:
            background_tasks.add_task(scanner.perform_scan, target, ports)
            return {"message": f"Scan scheduled for {target}"}
        else:
            result = await scanner.perform_scan(target, ports)
            return {"message": f"Scan completed for {target}", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get system status / metrics
@router.get("/status", response_model=None)
async def system_status():
    """
    Returns health and basic status of the scanner.
    """
    try:
        return {
            "status": "ok",
            "total_incidents": len(scanner.INCIDENTS),
            "active_alerts": sum(1 for a in scanner.ALERTS if not a.get("ack")),
            "logs_count": len(scanner.LOGS)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
