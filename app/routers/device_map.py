from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import os

router = APIRouter(
    prefix="/devices",
    tags=["devices"]
)

METRICS_FILE = "/var/lib/defenx/netmon_metrics.json"
INCIDENTS_FILE = "/var/lib/defenx/incidents.json"  # example path for your incident logs
DEVICES_FILE = "/var/lib/defenx/devices.json"

def load_json_file(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def calculate_device_status(device_ip, metrics, incidents):
    """
    Calculate device status based on:
    - Top talkers (high bytes/sec → warning)
    - Any active incidents → alert
    - Otherwise → secure
    """
    status = "secure"

    # Incident check
    device_incidents = [i for i in incidents if i.get("ip") == device_ip and i.get("status") == "active"]
    if device_incidents:
        status = "alert"
    else:
        # Check top talkers metric
        top_bytes = metrics.get("top_ips", {}).get(device_ip, 0)
        bytes_per_sec = metrics.get("bytes_sent_per_sec", 0) + metrics.get("bytes_recv_per_sec", 0)
        # If device has unusually high traffic, mark warning
        if top_bytes > 5_000_000 or bytes_per_sec > 1_000_000:
            status = "warning"

    return status

@router.get("/map")
async def device_map():
    """
    Returns list of devices with status for frontend Device Map.
    """
    devices = load_json_file(DEVICES_FILE)
    metrics = load_json_file(METRICS_FILE)
    incidents = load_json_file(INCIDENTS_FILE)

    device_list = []
    for ip, info in devices.items():
        device_status = calculate_device_status(ip, metrics, incidents)
        device_list.append({
            "ip": ip,
            "name": info.get("name", ip),
            "status": device_status
        })

    return JSONResponse(content={
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "devices": device_list
    })

@router.get("/status-summary")
async def status_summary():
    """
    Returns a summary of devices count by status.
    """
    devices = load_json_file(DEVICES_FILE)
    metrics = load_json_file(METRICS_FILE)
    incidents = load_json_file(INCIDENTS_FILE)

    summary = {"secure": 0, "warning": 0, "alert": 0}
    for ip in devices.keys():
        status = calculate_device_status(ip, metrics, incidents)
        summary[status] += 1

    return JSONResponse(content={
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": summary
    })
