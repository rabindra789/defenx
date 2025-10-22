#!/usr/bin/env python3
import json
import time
from threading import Thread, Lock
from scapy.all import sniff
from scapy.layers.inet import IP

METRICS_FILE = "/var/lib/defenx/netmon_metrics.json"

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

def save_metrics():
    with metrics_lock:
        with open(METRICS_FILE, "w") as f:
            json.dump(metrics, f)

def packet_handler(pkt):
    if IP in pkt:
        ip_layer = pkt[IP]
        size = len(pkt)
        with metrics_lock:
            metrics["bytes_sent"] += size
            metrics["bytes_recv"] += size  # treat all packets same
            metrics["top_ips"].setdefault(ip_layer.src, 0)
            metrics["top_ips"][ip_layer.src] += size

def update_per_sec():
    global _last_bytes_sent, _last_bytes_recv
    while True:
        time.sleep(1)
        with metrics_lock:
            metrics["bytes_sent_per_sec"] = metrics["bytes_sent"] - _last_bytes_sent
            metrics["bytes_recv_per_sec"] = metrics["bytes_recv"] - _last_bytes_recv
            _last_bytes_sent = metrics["bytes_sent"]
            _last_bytes_recv = metrics["bytes_recv"]
        save_metrics()

def start_capture(interface="eth0"):
    Thread(target=update_per_sec, daemon=True).start()
    sniff(prn=packet_handler, store=False, iface=interface)

if __name__ == "__main__":
    start_capture("eth0")
