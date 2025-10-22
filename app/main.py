from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import monitor, incidents, alerts, logs, dashboard, config, health, phishing, network
from fastapi.middleware.cors import CORSMiddleware
from app.core import scanner, netmon
from app.core import config as cfg
import asyncio

app = FastAPI(title="DefenX Backend", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],     
)

# routers
app.include_router(monitor.router, prefix="/api/monitor", tags=["Monitoring"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(config.router, prefix="/api/config", tags=["Config"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(phishing.router, prefix="/api/phishing", tags=["Phishing"])
app.include_router(network.router, prefix="/api/network", tags=["Network"])

@app.get("/", response_class=JSONResponse)
async def root():
    return {
        "app": "DefenX Backend",
        "version": "0.1",
        "status": "running",
        "endpoints": {
            "monitor": "/api/monitor",
            "incidents": "/api/incidents",
            "alerts": "/api/alerts",
            "logs": "/api/logs",
            "dashboard": "/api/dashboard",
            "config": "/api/config",
            "health": "/api/health"
        }
    }

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
    await netmon.start_monitor()
    scanner.add_log("startup", "Periodic scanner started", "info")
