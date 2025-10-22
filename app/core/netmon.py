# app/core/netmon.py
import asyncio
import time
from typing import Dict, Optional, Any
# import psutil

try:
    import psutil
except ImportError:
    psutil = None

_latest_metrics: Optional[Dict] = None
_metrics_lock = asyncio.Lock()
_monitor_task: Optional[asyncio.Task] = None
_MONITOR_INTERVAL = 1.0  # seconds


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


async def _sample_once(prev: Optional[Any]):
    """Take one sample and compute bytes/sec difference."""
    if psutil is None:
        return {
            "timestamp": _now(),
            "bytes_sent": 0,
            "bytes_recv": 0,
            "bytes_sent_per_sec": 0.0,
            "bytes_recv_per_sec": 0.0,
        }, None

    now_sample = psutil.net_io_counters(pernic=False)
    if prev is None:
        metrics = {
            "timestamp": _now(),
            "bytes_sent": now_sample.bytes_sent,
            "bytes_recv": now_sample.bytes_recv,
            "bytes_sent_per_sec": 0.0,
            "bytes_recv_per_sec": 0.0,
        }
        return metrics, now_sample

    elapsed = _MONITOR_INTERVAL
    metrics = {
        "timestamp": _now(),
        "bytes_sent": now_sample.bytes_sent,
        "bytes_recv": now_sample.bytes_recv,
        "bytes_sent_per_sec": round((now_sample.bytes_sent - prev.bytes_sent) / elapsed, 2),
        "bytes_recv_per_sec": round((now_sample.bytes_recv - prev.bytes_recv) / elapsed, 2),
    }
    return metrics, now_sample


async def _monitor_loop():
    """Runs forever, updates _latest_metrics every second."""
    global _latest_metrics
    prev = None
    while True:
        try:
            metrics, prev = await _sample_once(prev)
            async with _metrics_lock:
                _latest_metrics = metrics
        except Exception:
            pass
        await asyncio.sleep(_MONITOR_INTERVAL)


async def start_monitor():
    """Launch the continuous monitor loop once."""
    global _monitor_task
    if _monitor_task is None or _monitor_task.done():
        loop = asyncio.get_running_loop()
        _monitor_task = loop.create_task(_monitor_loop())


async def get_latest_metrics() -> Dict:
    """Return latest metrics snapshot."""
    async with _metrics_lock:
        if _latest_metrics is not None:
            return _latest_metrics.copy()
    # Fallback for very early call
    if psutil:
        sample = psutil.net_io_counters(pernic=False)
        return {
            "timestamp": _now(),
            "bytes_sent": sample.bytes_sent,
            "bytes_recv": sample.bytes_recv,
            "bytes_sent_per_sec": 0.0,
            "bytes_recv_per_sec": 0.0,
        }
    return {
        "timestamp": _now(),
        "bytes_sent": 0,
        "bytes_recv": 0,
        "bytes_sent_per_sec": 0.0,
        "bytes_recv_per_sec": 0.0,
    }
