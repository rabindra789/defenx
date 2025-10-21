# app/routers/alerts.py

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.core import scanner

router = APIRouter()

# Get latest alerts
@router.get("/latest")
async def latest_alerts(
    limit: int = Query(10, description="Number of latest alerts to fetch"),
    severity: Optional[str] = Query(None, description="Filter by severity: Low, Medium, High")
):
    try:
        return scanner.latest_alerts(limit=limit, severity_filter=severity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Acknowledge an alert
@router.post("/acknowledge")
async def acknowledge_alert(alert_id: str = Query(..., description="ID of the alert to acknowledge")):
    try:
        alert = scanner.ack_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return {"message": f"Alert {alert_id} acknowledged", "alert": alert}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
