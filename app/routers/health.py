from fastapi import APIRouter
from app.core import scanner, health_monitor

router = APIRouter()

@router.get("/")
async def health():
    try:
        return {
            "backend": "ok",
            "scanner": "ok",
            "server": health_monitor.HEALTH_STATUS
        }
    except Exception:
        return {"backend": "ok", "scanner": "unreachable", "server": "unreachable"}

@router.get("/metrics")
async def metrics():
    try:
        return {
            "total_logs": len(scanner.LOGS),
            "total_incidents": len(scanner.INCIDENTS),
            "active_alerts": sum(1 for a in scanner.ALERTS if not a.get("ack")),
            "server_alerts": len(health_monitor.HEALTH_STATUS.get("alerts", []))
        }
    except Exception as e:
        return {"error": str(e)}

# Start health monitor in the background when FastAPI starts
@router.on_event("startup")
async def start_health_monitor():
    import asyncio
    asyncio.create_task(health_monitor.monitor_health(interval=60))  # checks every 60s
