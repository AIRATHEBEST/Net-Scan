import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class InternetMonitoringService:
    def __init__(self):
        pass

    async def run_speed_test(self):
        return {"download": 0, "upload": 0, "ping": 0}

    async def check_internet_connectivity(self):
        return {"status": "online"}

    async def detect_isp(self):
        return {"isp": "Unknown"}
