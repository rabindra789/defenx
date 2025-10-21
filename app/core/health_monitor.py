import psutil
import asyncio
from datetime import datetime
from typing import List, Dict

HEALTH_STATUS: Dict = {
    "cpu": 0,
    "memory": 0,
    "disk": 0,
    "services": {},
    "timestamp": None,
    "alerts": []
}

# Critical services to monitor
CRITICAL_SERVICES = ["sshd", "nginx"]

# Thresholds for alerts
CPU_THRESHOLD = 90  # percent
MEM_THRESHOLD = 85  # percent
DISK_THRESHOLD = 90  # percent

async def monitor_health(interval: int = 60):
    while True:
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent

            services_status = {}
            for svc in CRITICAL_SERVICES:
                services_status[svc] = psutil.pid_exists(get_service_pid(svc))

            alerts: List[Dict] = []

            if cpu > CPU_THRESHOLD:
                alerts.append({"type": "CPU", "value": cpu, "severity": "WARNING", "timestamp": datetime.utcnow().isoformat()})
            if mem > MEM_THRESHOLD:
                alerts.append({"type": "Memory", "value": mem, "severity": "WARNING", "timestamp": datetime.utcnow().isoformat()})
            if disk > DISK_THRESHOLD:
                alerts.append({"type": "Disk", "value": disk, "severity": "WARNING", "timestamp": datetime.utcnow().isoformat()})
            for svc, running in services_status.items():
                if not running:
                    alerts.append({"type": "Service", "service": svc, "severity": "CRITICAL", "timestamp": datetime.utcnow().isoformat()})

            # Update shared status
            HEALTH_STATUS.update({
                "cpu": cpu,
                "memory": mem,
                "disk": disk,
                "services": services_status,
                "timestamp": datetime.utcnow().isoformat(),
                "alerts": alerts
            })

        except Exception as e:
            HEALTH_STATUS["alerts"].append({"type": "Exception", "message": str(e), "severity": "CRITICAL", "timestamp": datetime.utcnow().isoformat()})

        await asyncio.sleep(interval)


def get_service_pid(service_name: str) -> int:
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] == service_name:
            return proc.info["pid"]
    return 0
