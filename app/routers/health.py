# app/routers/health.py

from fastapi import APIRouter
from app.core import scanner

router = APIRouter()

# Health check endpoint
@router.get("/health")
async def health():
    """
    Returns the health status of the backend and scanner.
    """
    try:
        # For now, since scanner runs in the same process, it is always reachable
        return {"backend": "ok", "scanner": "ok"}
    except Exception:
        return {"backend": "ok", "scanner": "unreachable"}

# Metrics endpoint
@router.get("/metrics")
async def metrics():
    """
    Returns basic metrics for monitoring purposes.
    """
    try:
        return {
            "total_logs": len(scanner.LOGS),
            "total_incidents": len(scanner.INCIDENTS),
            "active_alerts": sum(1 for a in scanner.ALERTS if not a.get("ack"))
        }
    except Exception as e:
        return {"error": str(e)}
