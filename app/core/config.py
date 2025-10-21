# app/core/config.py

# app/core/config.py

from typing import List

# Default scan configuration
scan_ports_default: List[int] = [22, 80, 443, 3306, 8080]
scan_timeout: int = 2               # seconds per port
scan_concurrency: int = 100         # concurrent port checks
scan_target: str = "127.0.0.1"      # the server itself
scan_interval_seconds: int = 60      # automatic scan interval in seconds