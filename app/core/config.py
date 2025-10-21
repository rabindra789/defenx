# app/core/config.py

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Default scan configuration
    scan_ports_default: List[int] = [22, 80, 443, 3306, 8080]
    scan_timeout: int = 2               # seconds per port
    scan_concurrency: int = 100         # concurrent port checks
    scan_target: str = "127.0.0.1"      # default target (server itself)
    scan_interval_seconds: int = 300    # periodic scan every 5 minutes

settings = Settings()
