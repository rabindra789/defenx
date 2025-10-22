from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import os
from typing import Any, Dict, List, Union, TypedDict, Sequence

router = APIRouter(
    prefix="/devices",
    tags=["devices"]
)

# ---------- FILE PATHS ----------
METRICS_FILE = "/var/lib/defenx/netmon_metrics.json"
INCIDENTS_FILE = "/var/lib/defenx/incidents.json"
DEVICES_FILE = "/var/lib/defenx/devices.json"


# ---------- TYPES ----------
class Incident(TypedDict, total=False):
    ip: str
    status: str
    description: str


# ---------- HELPERS ----------
def load_json_file(path: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Safely load a JSON file and return consistent typed data."""
    try:
        if not os.path.exists(path) or os.stat(path).st_size == 0:
            # Default type based on file name
            if "incident" in path:
                return []
            return {}
        with open(path, "r") as f:
            data = json.load(f)
            if "incident" in path:
                return data if isinstance(data, list) else []
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        if "incident" in path:
            return []
        return {}


def calculate_device_status(device_ip: str, metrics: Dict[str, Any], incidents: Sequence[Dict[str, Any]]) -> str:
    """Derive the security status of a given device."""
    status = "secure"

    # --- Incident-based threat detection ---
    active_incidents = [
        inc for inc in incidents
        if inc.get("ip") == device_ip and inc.get("status") == "active"
    ]
    if active_incidents:
        return "alert"

    # --- Network metric anomaly detection ---
    top_bytes = metrics.get("top_ips", {}).get(device_ip, 0)
    total_throughput = (
        metrics.get("bytes_sent_per_sec", 0) +
        metrics.get("bytes_recv_per_sec", 0)
    )

    if top_bytes > 5_000_000 or total_throughput > 1_000_000:
        status = "warning"

    return status


# ---------- ROUTES ----------
@router.get("/map")
async def device_map():
    devices_data = load_json_file(DEVICES_FILE)
    metrics_data = load_json_file(METRICS_FILE)
    incidents_data = load_json_file(INCIDENTS_FILE)

    if not isinstance(devices_data, dict):
        devices_data = {}
    if not isinstance(metrics_data, dict):
        metrics_data = {}
    if not isinstance(incidents_data, list):
        incidents_data = []

    devices_list = []
    for ip, info in devices_data.items():
        device_status = calculate_device_status(ip, metrics_data, incidents_data)
        devices_list.append({
            "ip": ip,
            "name": info.get("name", ip),
            "status": device_status
        })

    return JSONResponse(content={
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "devices": devices_list
    })


@router.get("/status-summary")
async def status_summary():
    devices_data = load_json_file(DEVICES_FILE)
    metrics_data = load_json_file(METRICS_FILE)
    incidents_data = load_json_file(INCIDENTS_FILE)

    if not isinstance(devices_data, dict):
        devices_data = {}
    if not isinstance(metrics_data, dict):
        metrics_data = {}
    if not isinstance(incidents_data, list):
        incidents_data = []

    summary = {"secure": 0, "warning": 0, "alert": 0}

    for ip in devices_data.keys():
        status = calculate_device_status(ip, metrics_data, incidents_data)
        summary[status] += 1

    return JSONResponse(content={
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": summary
    })
