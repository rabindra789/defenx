# app/routers/network.py
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core import netmon

router = APIRouter()


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
