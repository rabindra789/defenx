# # app/core/config.py
from typing import List

# Default scan configuration
scan_ports_default: List[int] = [80, 443, 22, 21, 25, 23, 53, 110, 143, 587,
    3306, 3389, 8080, 8443, 111, 135, 139, 445, 993, 995,
    179, 1723, 5870, 5900, 5901, 5902, 69, 5060, 5061, 636,
    389, 1433, 1521, 1720, 2049, 2181, 2375, 2376, 27017, 3128,
    3268, 3307, 3310, 3388, 3690, 4369, 4444, 4567, 5000, 5432,
    5672, 6000, 6379, 6667, 7000, 7199, 7474, 8000, 8008, 8444,
    8888, 9100, 9200, 9300, 10000, 11211, 1194, 12345, 137, 138,
    161, 162, 3899, 5001, 5050, 54321, 5500, 5984, 6060, 6666,
    7001, 7777, 8001, 8081, 8090, 8181, 9000, 9001, 9101, 9999,
    1122, 1434, 2869, 49152, 49153, 49154, 49155, 49156, 49157, 49158]
scan_timeout: int = 1               # seconds per port
scan_concurrency: int = 200         # concurrent port checks
scan_target: str = "127.0.0.1"      # the server itself
scan_interval_seconds: int = 60     # automatic scan interval in seconds

