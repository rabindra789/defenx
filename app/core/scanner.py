# app/core/scanner.py

import asyncio
import time
import itertools
from typing import List, Dict, Optional, Tuple
import httpx

# In-memory storage
INCIDENTS: List[dict] = []
ALERTS: List[dict] = []
LOGS: List[dict] = []
CONFIG = {
    "scan_ports_default": [22, 80, 443, 3306, 8080],
    "scan_timeout": 2,
    "scan_concurrency": 100
}

# Counters for unique IDs
_incident_counter = itertools.count(1)
_alert_counter = itertools.count(1)
_log_counter = itertools.count(int(time.time() * 1000))

# Helpers
def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def add_log(source: str, message: str, severity: str = "info") -> dict:
    log_id = f"log-{next(_log_counter)}"
    entry = {"log_id": log_id, "timestamp": _now(), "source": source, "message": message, "severity": severity}
    LOGS.append(entry)
    return entry

def recent_logs(limit: int = 50) -> List[dict]:
    return LOGS[-limit:][::-1]

def search_logs(query: str, start: Optional[str] = None, end: Optional[str] = None) -> List[dict]:
    results = [l for l in LOGS if query.lower() in l["message"].lower()]
    return results

# Incidents & Alerts
def create_incident(typ: str, severity: str, source: str, details: str) -> dict:
    iid = f"INC-{next(_incident_counter)}"
    inc = {"incident_id": iid, "timestamp": _now(), "type": typ, "severity": severity, "status": "Open", "source": source, "details": details}
    INCIDENTS.append(inc)
    add_log(source, f"Incident created: {iid} - {typ}", "warning")
    return inc

def list_incidents() -> List[dict]:
    return INCIDENTS

def get_incident(incident_id: str) -> Optional[dict]:
    for inc in INCIDENTS:
        if inc["incident_id"] == incident_id:
            return inc
    return None

def create_alert(alert_type: str, severity: str, message: str) -> dict:
    aid = f"AL-{next(_alert_counter)}"
    al = {"alert_id": aid, "type": alert_type, "severity": severity, "message": message, "timestamp": _now(), "ack": False}
    ALERTS.append(al)
    add_log("alerts", f"Alert generated: {aid} - {alert_type}", "critical" if severity.lower() == "high" else "warning")
    return al

def list_alerts() -> List[dict]:
    return ALERTS

def latest_alerts(limit: int = 10, severity_filter: Optional[str] = None) -> List[dict]:
    items = ALERTS[::-1]
    if severity_filter:
        items = [a for a in items if a["severity"].lower() == severity_filter.lower()]
    return items[:limit]

def ack_alert(alert_id: str) -> Optional[dict]:
    for a in ALERTS:
        if a["alert_id"] == alert_id:
            a["ack"] = True
            add_log("alerts", f"Alert acknowledged: {alert_id}", "info")
            return a
    return None

# Scanner Logic
async def tcp_check(ip: str, port: int, timeout: int = 2) -> Tuple[int, bool]:
    try:
        fut = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(fut, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return port, True
    except Exception:
        return port, False

async def scan_ports(ip: str, ports: List[int], concurrency: int = 100) -> Dict[int, bool]:
    sem = asyncio.Semaphore(concurrency)
    results: Dict[int, bool] = {}

    async def worker(p: int):
        async with sem:
            port, is_open = await tcp_check(ip, p)
            results[port] = is_open

    tasks = [asyncio.create_task(worker(p)) for p in ports]
    await asyncio.gather(*tasks)
    return results

async def http_header_check(ip_or_host: str, timeout: int = 3) -> dict:
    url = f"http://{ip_or_host}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url)
            return {
                "status_code": r.status_code,
                "server": r.headers.get("server"),
                "security_headers": {k: v for k, v in r.headers.items() if k.lower().startswith("x-") or k.lower() in ["strict-transport-security", "content-security-policy"]}
            }
    except Exception as e:
        return {"error": str(e)}

async def perform_scan(target_ip: str, ports: Optional[List[int]] = None, concurrency: int = 100) -> dict:
    ports = ports or CONFIG["scan_ports_default"]
    add_log("scanner", f"Starting scan on {target_ip} ports={ports}", "info")

    port_results = await scan_ports(target_ip, ports, concurrency)
    open_ports = [p for p, is_open in port_results.items() if is_open]

    # Create incidents/alerts for high-risk ports
    if open_ports:
        details = f"Open ports on {target_ip}: {open_ports}"
        create_incident("open_ports", "Medium", "scanner", details)

        critical_ports = {22, 3306, 3389}
        if any(p in critical_ports for p in open_ports):
            create_alert("critical_port_open", "High", f"{target_ip} has critical open ports {open_ports}")

    http_info = await http_header_check(target_ip)
    add_log("scanner", f"HTTP check: {http_info}", "info")

    return {"scan_target": target_ip, "ports": port_results, "http_info": http_info}

# Dashboard helpers
def dashboard_overview() -> dict:
    return {
        "total_incidents": len(INCIDENTS),
        "active_alerts": sum(1 for a in ALERTS if not a.get("ack")),
        "total_logs": len(LOGS),
        "uptime": "demo-mode"
    }

def dashboard_trends() -> dict:
    # minimal trends placeholder
    return {
        "trend_data": [
            {"time": "09:00", "incidents": max(0, len(INCIDENTS)-3)},
            {"time": "10:00", "incidents": len(INCIDENTS)},
        ]
    }
