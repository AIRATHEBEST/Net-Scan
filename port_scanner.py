import asyncio
import logging
import nmap
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class PortScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        
    async def scan_ports(
        self, 
        ip: str, 
        ports: str = "1-1000",
        timeout: int = 5
    ) -> Dict[str, any]:
        """
        Scan ports on a device using nmap
        Returns open ports, services, and OS detection
        """
        logger.info(f"Scanning ports on {ip}")
        
        try:
            # Run nmap scan in thread
            result = await asyncio.to_thread(
                self.nm.scan,
                ip,
                ports,
                arguments=f'-sV -O --host-timeout {timeout}s'
            )
            
            if ip not in self.nm.all_hosts():
                return {
                    'open_ports': [],
                    'services': {},
                    'os': None
                }
            
            host = self.nm[ip]
            
            # Extract open ports and services
            open_ports = []
            services = {}
            
            if 'tcp' in host:
                for port in host['tcp']:
                    port_info = host['tcp'][port]
                    if port_info['state'] == 'open':
                        open_ports.append(port)
                        services[str(port)] = {
                            'name': port_info.get('name', 'unknown'),
                            'product': port_info.get('product', ''),
                            'version': port_info.get('version', '')
                        }
            
            # OS detection
            os_info = None
            if 'osmatch' in host and host['osmatch']:
                os_match = host['osmatch'][0]
                os_info = {
                    'name': os_match.get('name', ''),
                    'accuracy': os_match.get('accuracy', 0)
                }
            
            return {
                'open_ports': sorted(open_ports),
                'services': services,
                'os': os_info
            }
            
        except Exception as e:
            logger.error(f"Error scanning ports on {ip}: {e}")
            return {
                'open_ports': [],
                'services': {},
                'os': None
            }
    
    async def quick_scan(self, ip: str) -> Dict[str, any]:
        """Quick scan of common ports"""
        common_ports = "21,22,23,25,53,80,110,143,443,445,3306,3389,5432,8080,8443"
        return await self.scan_ports(ip, common_ports, timeout=2)
    
    async def detect_vulnerabilities(self, ip: str, ports: List[int]) -> List[Dict[str, str]]:
        """
        Run vulnerability detection scripts
        Uses nmap NSE scripts for common vulnerabilities
        """
        logger.info(f"Running vulnerability scan on {ip}")
        
        vulnerabilities = []
        
        try:
            # Run vuln scripts
            port_str = ",".join(map(str, ports))
            result = await asyncio.to_thread(
                self.nm.scan,
                ip,
                port_str,
                arguments='--script vuln'
            )
            
            if ip in self.nm.all_hosts():
                host = self.nm[ip]
                if 'tcp' in host:
                    for port in host['tcp']:
                        port_info = host['tcp'][port]
                        if 'script' in port_info:
                            for script_name, script_output in port_info['script'].items():
                                if 'VULNERABLE' in script_output:
                                    vulnerabilities.append({
                                        'port': port,
                                        'script': script_name,
                                        'description': script_output[:500]
                                    })
            
        except Exception as e:
            logger.error(f"Error in vulnerability scan on {ip}: {e}")
        
        return vulnerabilities
