from fastapi import FastAPI
from app.routers import monitor, incidents, alerts, logs, dashboard, config, health
from app.core import scanner
from app.core import config as cfg
import asyncio

app = FastAPI(title="DefenX Backend", version="0.1")

# routers
app.include_router(monitor.router, prefix="/monitor", tags=["Monitoring"])
app.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(logs.router, prefix="/logs", tags=["Logs"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(config.router, prefix="/config", tags=["Config"])
app.include_router(health.router, tags=["Health"])

# Periodic scanner task
async def _periodic_scanner():
    interval = cfg.scan_interval_seconds
    while True:
        try:
            asyncio.create_task(scanner.perform_scan())
        except Exception as e:
            scanner.add_log("periodic-scanner", f"periodic scan spawn error: {e}", "error")
        await asyncio.sleep(interval)

@app.on_event("startup")
async def startup_tasks():
    # start periodic scanning loop
    asyncio.create_task(_periodic_scanner())
    scanner.add_log("startup", "Periodic scanner started", "info")
