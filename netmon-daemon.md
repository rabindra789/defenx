```python
#!/usr/bin/env python3
import json, time, os
from threading import Thread, Lock
from scapy.all import sniff
from scapy.layers.inet import IP

# ---------- Paths ----------
METRICS_DIR = "/var/lib/defenx"
METRICS_FILE = os.path.join(METRICS_DIR, "netmon_metrics.json")
DEVICES_FILE = os.path.join(METRICS_DIR, "devices.json")  # device info for API

os.makedirs(METRICS_DIR, exist_ok=True)

# ---------- Metrics ----------
metrics = {
    "bytes_sent": 0,
    "bytes_recv": 0,
    "bytes_sent_per_sec": 0,
    "bytes_recv_per_sec": 0,
    "top_ips": {}
}

metrics_lock = Lock()
_last_bytes_sent = 0
_last_bytes_recv = 0

# ---------- Devices ----------
# Format: { ip: { "name": "Device-1", "status": "secure" } }
# Initially empty, will auto-register IPs seen
devices = {}
devices_lock = Lock()

# ---------- Helper ----------
def atomic_write(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

# ---------- Packet Capture ----------
def packet_handler(pkt):
    if IP in pkt:
        ip = pkt[IP].src
        size = len(pkt)

        # Update metrics
        with metrics_lock:
            metrics["bytes_sent"] += size
            metrics["bytes_recv"] += size
            metrics["top_ips"].setdefault(ip, 0)
            metrics["top_ips"][ip] += size

        # Auto-register device
        with devices_lock:
            if ip not in devices:
                devices[ip] = {"name": ip, "status": "secure"}

# ---------- Update per second ----------
def update_per_sec():
    global _last_bytes_sent, _last_bytes_recv
    while True:
        time.sleep(1)
        with metrics_lock:
            metrics["bytes_sent_per_sec"] = metrics["bytes_sent"] - _last_bytes_sent
            metrics["bytes_recv_per_sec"] = metrics["bytes_recv"] - _last_bytes_recv
            _last_bytes_sent = metrics["bytes_sent"]
            _last_bytes_recv = metrics["bytes_recv"]
            atomic_write(METRICS_FILE, metrics)

        # Update device status
        with devices_lock, metrics_lock:
            for ip, info in devices.items():
                top_bytes = metrics["top_ips"].get(ip, 0)
                bytes_per_sec = metrics["bytes_sent_per_sec"] + metrics["bytes_recv_per_sec"]
                if top_bytes > 5_000_000 or bytes_per_sec > 1_000_000:
                    info["status"] = "warning"
                else:
                    info["status"] = "secure"
            atomic_write(DEVICES_FILE, devices)

# ---------- Start Capture ----------
def start_capture(interface="eth0"):
    Thread(target=update_per_sec, daemon=True).start()
    sniff(prn=packet_handler, store=False, iface=interface)

# ---------- Main ----------
if __name__ == "__main__":
    # Change "enX0" to your actual interface if needed
    start_capture("enX0")
```


Run `netmon_daemon.py` as a **systemd service** so it starts automatically on boot, keeps running in the background, and writes metrics to `/var/lib/defenx`.

---

### **1️⃣ Create the service file**

Run:

```bash
sudo nano /etc/systemd/system/defenx-netmon.service
```

Paste this:

```ini
[Unit]
Description=DefenX Network Monitoring Daemon
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
ExecStart=/usr/bin/python3 /usr/local/bin/netmon_daemon.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

**Notes:**

* `User` and `Group` should be the user that has access to `/var/lib/defenx` and `python3`.
* `ExecStart` must point to the **full path** of your `netmon_daemon.py`.
  For example, if your script is in `/home/ubuntu/defenx/netmon_daemon.py`, use that path.
* `Restart=always` ensures it comes back if it crashes.

---

### **2️⃣ Make the script executable**

```bash
sudo chmod +x /usr/local/bin/netmon_daemon.py
```

Or wherever your script is located.

---

### **3️⃣ Reload systemd and enable the service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable defenx-netmon.service
sudo systemctl start defenx-netmon.service
```

---

### **4️⃣ Check the service status**

```bash
sudo systemctl status defenx-netmon.service
```
---

### **5️⃣ Verify the files are being written**

```bash
ls -l /var/lib/defenx
cat /var/lib/defenx/devices.json
cat /var/lib/defenx/netmon_metrics.json
```
