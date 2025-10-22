# app/routers/network.py
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core import netmon
from fastapi.responses import JSONResponse
from datetime import datetime
import json

router = APIRouter()

METRICS_FILE = "/var/lib/defenx/netmon_metrics.json"

@router.get("/metrics")
async def get_metrics():
    data = await netmon.get_latest_metrics()
    return data


@router.websocket("/ws")
async def network_ws(ws: WebSocket):
    await ws.accept()
    await netmon.start_monitor()
    try:
        while True:
            metrics = await netmon.get_latest_metrics()
            await ws.send_json(metrics)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass

@router.get("/top-talkers")
async def top_talkers():
    try:
        with open(METRICS_FILE, "r") as f:
            metrics = json.load(f)
    except FileNotFoundError:
        return JSONResponse(status_code=503, content={"error": "Metrics not available"})

    # Sort top IPs by bytes
    sorted_ips = sorted(metrics.get("top_ips", {}).items(), key=lambda x: x[1], reverse=True)
    top_5 = [{"ip": ip, "bytes": count} for ip, count in sorted_ips[:5]]

    return JSONResponse(content={
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "top_talkers": top_5,
        "bytes_sent_per_sec": metrics.get("bytes_sent_per_sec", 0),
        "bytes_recv_per_sec": metrics.get("bytes_recv_per_sec", 0)
    })