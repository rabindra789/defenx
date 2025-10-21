from fastapi import FastAPI
from app.routers import monitor, incidents, alerts, logs, dashboard, config, health

app = FastAPI(title="DefenX Backend", version="0.1")

# Routers
app.include_router(monitor.router, prefix="/monitor", tags=["Monitoring"])
app.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(logs.router, prefix="/logs", tags=["Logs"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(config.router, prefix="/config", tags=["Config"])
app.include_router(health.router, tags=["Health"])
