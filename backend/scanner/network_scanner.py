import asyncio
import logging
from scapy.all import ARP, Ether, srp, conf
from typing import List, Dict, Optional
import netifaces
import ipaddress

logger = logging.getLogger(__name__)

class NetworkScanner:
    def __init__(self):
        conf.verb = 0  # Disable scapy verbose output
        
    def get_network_interfaces(self) -> List[Dict[str, str]]:
        """Get all available network interfaces"""
        interfaces = []
        for iface in netifaces.interfaces():
            try:
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        if 'addr' in addr and 'netmask' in addr:
                            interfaces.append({
                                'name': iface,
                                'ip': addr['addr'],
                                'netmask': addr['netmask'],
                                'network': self._get_network(addr['addr'], addr['netmask'])
                            })
            except Exception as e:
                logger.error(f"Error getting interface {iface}: {e}")
        return interfaces
    
    def _get_network(self, ip: str, netmask: str) -> str:
        """Calculate network address from IP and netmask"""
        try:
            network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
            return str(network)
        except Exception:
            return ""
    
    async def scan_network(self, network: str, timeout: int = 5) -> List[Dict[str, str]]:
        """
        Perform ARP scan on the network
        Returns list of discovered devices with IP and MAC
        """
        logger.info(f"Starting ARP scan on network: {network}")
        
        try:
            # Create ARP request packet
            arp = ARP(pdst=network)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            
            # Send packet and receive response
            result = await asyncio.to_thread(srp, packet, timeout=timeout, verbose=0)
            answered, unanswered = result
            
            devices = []
            for sent, received in answered:
                devices.append({
                    'ip': received.psrc,
                    'mac': received.hwsrc.upper(),
                })
            
            logger.info(f"Found {len(devices)} devices on network {network}")
            return devices
            
        except Exception as e:
            logger.error(f"Error scanning network {network}: {e}")
            return []
    
    async def get_gateway(self, interface: str = None) -> Optional[str]:
        """Get default gateway for interface"""
        try:
            gws = netifaces.gateways()
            if 'default' in gws and netifaces.AF_INET in gws['default']:
                return gws['default'][netifaces.AF_INET][0]
        except Exception as e:
            logger.error(f"Error getting gateway: {e}")
        return None
    
    async def detect_router(self, network: str) -> Optional[Dict[str, str]]:
        """Detect router on the network"""
        gateway = await self.get_gateway()
        if gateway:
            devices = await self.scan_network(network)
            for device in devices:
                if device['ip'] == gateway:
                    device['type'] = 'router'
                    device['is_gateway'] = True
                    return device
        return None
