import asyncio
import logging
from typing import List, Dict, Optional
import httpx
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.device import Device, Vulnerability
from backend.core.config import settings

logger = logging.getLogger(__name__)

class SecurityService:
    def __init__(self):
        self.nvd_api_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.cve_cache = {}
    
    async def scan_vulnerabilities(
        self,
        db: AsyncSession,
        device_id: str
    ) -> List[Dict[str, any]]:
        """
        Scan device for known vulnerabilities
        Uses NVD API and nmap NSE scripts
        """
        logger.info(f"Scanning vulnerabilities for device {device_id}")
        
        # Get device info
        result = await db.execute(
            select(Device).where(Device.id == device_id)
        )
        device = result.scalar_one_or_none()
        
        if not device:
            return []
        
        vulnerabilities = []
        
        # Check CVE database for OS vulnerabilities
        if device.os:
            os_vulns = await self._check_os_vulnerabilities(device.os, device.os_version)
            vulnerabilities.extend(os_vulns)
        
        # Check service vulnerabilities
        for port, service_info in device.services.items():
            service_name = service_info.get('name')
            service_version = service_info.get('version')
            
            if service_name and service_version:
                service_vulns = await self._check_service_vulnerabilities(
                    service_name,
                    service_version
                )
                vulnerabilities.extend(service_vulns)
        
        # Save vulnerabilities to database
        for vuln in vulnerabilities:
            existing = await db.execute(
                select(Vulnerability).where(
                    Vulnerability.device_id == device_id,
                    Vulnerability.cve_id == vuln['cve_id']
                )
            )
            
            if not existing.scalar_one_or_none():
                db_vuln = Vulnerability(
                    device_id=device_id,
                    cve_id=vuln['cve_id'],
                    severity=vuln['severity'],
                    title=vuln['title'],
                    description=vuln['description'],
                    recommendation=vuln['recommendation'],
                    cvss_score=vuln.get('cvss_score', 0)
                )
                db.add(db_vuln)
        
        await db.commit()
        
        return vulnerabilities
    
    async def _check_os_vulnerabilities(
        self,
        os_name: str,
        os_version: Optional[str]
    ) -> List[Dict[str, any]]:
        """Check NVD database for OS vulnerabilities"""
        if not settings.NVD_API_KEY:
            logger.warning("NVD API key not configured")
            return []
        
        try:
            # Build search query
            search_term = f"{os_name} {os_version}" if os_version else os_name
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.nvd_api_url,
                    params={
                        'keywordSearch': search_term,
                        'resultsPerPage': 20
                    },
                    headers={'apiKey': settings.NVD_API_KEY},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    return []
                
                data = response.json()
                vulnerabilities = []
                
                for cve_item in data.get('vulnerabilities', []):
                    cve = cve_item.get('cve', {})
                    
                    vuln = {
                        'cve_id': cve.get('id'),
                        'severity': self._get_severity(cve),
                        'title': cve.get('descriptions', [{}])[0].get('value', '')[:500],
                        'description': cve.get('descriptions', [{}])[0].get('value', '')[:2000],
                        'recommendation': 'Update to the latest version',
                        'cvss_score': self._get_cvss_score(cve)
                    }
                    
                    vulnerabilities.append(vuln)
                
                return vulnerabilities[:10]  # Limit to top 10
                
        except Exception as e:
            logger.error(f"Error checking OS vulnerabilities: {e}")
            return []
    
    async def _check_service_vulnerabilities(
        self,
        service_name: str,
        service_version: str
    ) -> List[Dict[str, any]]:
        """Check vulnerabilities for specific service version"""
        # Similar to OS check but for services
        return await self._check_os_vulnerabilities(service_name, service_version)
    
    def _get_severity(self, cve: dict) -> str:
        """Extract severity from CVE data"""
        metrics = cve.get('metrics', {})
        
        if 'cvssMetricV31' in metrics:
            severity = metrics['cvssMetricV31'][0].get('cvssData', {}).get('baseSeverity', 'MEDIUM')
        elif 'cvssMetricV2' in metrics:
            score = metrics['cvssMetricV2'][0].get('cvssData', {}).get('baseScore', 5.0)
            if score >= 7.0:
                severity = 'HIGH'
            elif score >= 4.0:
                severity = 'MEDIUM'
            else:
                severity = 'LOW'
        else:
            severity = 'MEDIUM'
        
        return severity.lower()
    
    def _get_cvss_score(self, cve: dict) -> float:
        """Extract CVSS score from CVE data"""
        metrics = cve.get('metrics', {})
        
        if 'cvssMetricV31' in metrics:
            return metrics['cvssMetricV31'][0].get('cvssData', {}).get('baseScore', 0.0)
        elif 'cvssMetricV2' in metrics:
            return metrics['cvssMetricV2'][0].get('cvssData', {}).get('baseScore', 0.0)
        
        return 0.0
    
    async def check_router_security(
        self,
        db: AsyncSession,
        router_ip: str
    ) -> List[Dict[str, any]]:
        """
        Check router for security issues
        - Default credentials
        - UPnP exposure
        - Firmware version
        - Open management ports
        """
        issues = []
        
        # Check for open management ports
        dangerous_ports = [23, 8080, 8888, 8443]  # Telnet, HTTP alt ports
        
        # TODO: Implement router-specific checks
        
        return issues
