import asyncio
import logging
import httpx
from typing import Optional, Dict
import json
import os

logger = logging.getLogger(__name__)

class MACVendorLookup:
    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.cache_file = "mac_vendor_cache.json"
        self._load_cache()
        
        # OUI database API endpoints
        self.apis = [
            "https://api.macvendors.com/",
            "https://www.macvendorlookup.com/api/v2/"
        ]
    
    def _load_cache(self):
        """Load MAC vendor cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
        except Exception as e:
            logger.error(f"Error loading MAC vendor cache: {e}")
    
    def _save_cache(self):
        """Save MAC vendor cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Error saving MAC vendor cache: {e}")
    
    def _normalize_mac(self, mac: str) -> str:
        """Normalize MAC address format"""
        return mac.upper().replace(':', '').replace('-', '')[:6]
    
    async def lookup(self, mac: str) -> Optional[str]:
        """
        Lookup vendor for MAC address
        Uses cache first, then API lookup
        """
        oui = self._normalize_mac(mac)
        
        # Check cache
        if oui in self.cache:
            return self.cache[oui]
        
        # Try API lookup
        for api_url in self.apis:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{api_url}{mac}",
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        vendor = response.text.strip()
                        
                        # Handle JSON response
                        if api_url.endswith("/v2/"):
                            data = response.json()
                            vendor = data[0]['company'] if data else "Unknown"
                        
                        # Cache result
                        self.cache[oui] = vendor
                        self._save_cache()
                        
                        return vendor
                        
            except Exception as e:
                logger.debug(f"API {api_url} failed: {e}")
                continue
        
        # Fallback to OUI prefix guess
        vendor = self._guess_vendor(oui)
        self.cache[oui] = vendor
        return vendor
    
    def _guess_vendor(self, oui: str) -> str:
        """Guess vendor from common OUI prefixes"""
        common_ouis = {
            '00:50:56': 'VMware',
            '00:0C:29': 'VMware',
            '00:05:69': 'VMware',
            '00:1C:42': 'Parallels',
            '08:00:27': 'VirtualBox',
            '52:54:00': 'QEMU/KVM',
            '00:15:5D': 'Microsoft Hyper-V',
            'DC:A6:32': 'Raspberry Pi',
            'B8:27:EB': 'Raspberry Pi',
            'E4:5F:01': 'Raspberry Pi',
            '00:1B:63': 'Apple',
            '00:03:93': 'Apple',
            '00:0A:27': 'Apple',
            '00:0D:93': 'Apple',
            '00:17:F2': 'Apple',
            '00:1E:C2': 'Apple',
            '00:25:00': 'Apple',
            '28:CF:E9': 'Apple',
            'A4:5E:60': 'Apple',
            'F0:F6:1C': 'Apple',
        }
        
        for prefix, vendor in common_ouis.items():
            if oui.startswith(prefix.replace(':', '')):
                return vendor
        
        return "Unknown Vendor"
