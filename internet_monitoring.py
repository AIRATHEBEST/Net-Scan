import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import subprocess
import re
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.user import Alert
import uuid

logger = logging.getLogger(__name__)

class InternetMonitoringService:
    """
    🌐 Tier 1 Feature #4: Internet Monitoring
    
    Features:
    - Speed test (Ookla-style)
    - Ping monitoring (Google DNS, Cloudflare)
    - ISP detection
    - Outage detection and alerts
    - Connection quality metrics
    """
    
    def __init__(self):
        self.monitoring_targets = {
            'google_dns': '8.8.8.8',
            'cloudflare_dns': '1.1.1.1',
            'google': 'www.google.com',
            'cloudflare': 'www.cloudflare.com'
        }
        
        self.outage_threshold = 3  # Failed pings before declaring outage
        self.ping_interval = 60  # seconds
    
    async def run_speed_test(self) -> Dict[str, any]:
        """
        Run internet speed test
        Returns download/upload speeds and latency
        """
        
        logger.info("Running speed test...")
        
        try:
            # Use speedtest-cli if available
            result = await asyncio.create_subprocess_shell(
                'speedtest-cli --json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                import json
                data = json.loads(stdout.decode())
                
                return {
                    'download_mbps': round(data['download'] / 1_000_000, 2),
                    'upload_mbps': round(data['upload'] / 1_000_000, 2),
                    'ping_ms': round(data['ping'], 2),
                    'server': data['server']['sponsor'],
                    'server_location': f"{data['server']['name']}, {data['server']['country']}",
                    'timestamp': datetime.utcnow().isoformat(),
                    'isp': data['client']['isp']
                }
            
        except Exception as e:
            logger.error(f"Speed test failed: {e}")
        
        # Fallback to simple HTTP-based test
        return await self._simple_speed_test()
    
    async def _simple_speed_test(self) -> Dict[str, any]:
        """Simple HTTP-based speed test fallback"""
        
        test_url = "http://speedtest.tele2.net/10MB.zip"
        
        try:
            start_time = datetime.utcnow()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(test_url, timeout=30.0)
                
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                if response.status_code == 200:
                    # Calculate download speed
                    bytes_downloaded = len(response.content)
                    mbps = (bytes_downloaded * 8) / (duration * 1_000_000)
                    
                    return {
                        'download_mbps': round(mbps, 2),
                        'upload_mbps': None,  # Not tested
                        'ping_ms': None,
                        'server': 'Tele2 Speedtest',
                        'timestamp': datetime.utcnow().isoformat(),
                        'method': 'http_fallback'
                    }
        
        except Exception as e:
            logger.error(f"Simple speed test failed: {e}")
        
        return {
            'error': 'Speed test failed',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def ping_host(self, host: str, count: int = 4) -> Dict[str, any]:
        """
        Ping a host and return latency statistics
        """
        
        try:
            # Use system ping command
            result = await asyncio.create_subprocess_shell(
                f'ping -c {count} {host}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            output = stdout.decode()
            
            if result.returncode == 0:
                # Parse ping output
                # Look for: rtt min/avg/max/mdev = X/Y/Z/W ms
                match = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', output)
                
                if match:
                    return {
                        'host': host,
                        'reachable': True,
                        'min_ms': float(match.group(1)),
                        'avg_ms': float(match.group(2)),
                        'max_ms': float(match.group(3)),
                        'mdev_ms': float(match.group(4)),
                        'packet_loss': 0,
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            # Ping failed
            return {
                'host': host,
                'reachable': False,
                'error': 'Host unreachable',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Ping failed for {host}: {e}")
            return {
                'host': host,
                'reachable': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_internet_connectivity(self) -> Dict[str, any]:
        """
        Check internet connectivity by pinging multiple targets
        """
        
        results = {}
        
        # Ping all monitoring targets
        for name, host in self.monitoring_targets.items():
            results[name] = await self.ping_host(host, count=3)
        
        # Determine overall connectivity
        reachable_count = sum(1 for r in results.values() if r.get('reachable'))
        total_count = len(results)
        
        connectivity_status = 'online' if reachable_count >= 2 else 'offline'
        
        # Calculate average latency
        latencies = [r.get('avg_ms') for r in results.values() if r.get('reachable')]
        avg_latency = sum(latencies) / len(latencies) if latencies else None
        
        return {
            'status': connectivity_status,
            'reachable_targets': reachable_count,
            'total_targets': total_count,
            'average_latency_ms': round(avg_latency, 2) if avg_latency else None,
            'details': results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def detect_isp(self) -> Dict[str, any]:
        """
        Detect ISP information
        """
        
        try:
            async with httpx.AsyncClient() as client:
                # Use ipinfo.io for ISP detection
                response = await client.get('https://ipinfo.io/json', timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return {
                        'isp': data.get('org', 'Unknown'),
                        'ip': data.get('ip'),
                        'city': data.get('city'),
                        'region': data.get('region'),
                        'country': data.get('country'),
                        'location': data.get('loc'),
                        'timezone': data.get('timezone')
                    }
        
        except Exception as e:
            logger.error(f"ISP detection failed: {e}")
        
        return {'isp': 'Unknown', 'error': 'Detection failed'}
    
    async def monitor_internet_health(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        duration_minutes: int = 60
    ) -> Dict[str, any]:
        """
        Monitor internet health over a period
        Checks connectivity, latency, and detects outages
        """
        
        logger.info(f"Starting internet health monitoring for {duration_minutes} minutes")
        
        monitoring_data = {
            'start_time': datetime.utcnow().isoformat(),
            'checks': [],
            'outages': [],
            'average_latency': None,
            'max_latency': None,
            'min_latency': None,
            'uptime_percentage': None
        }
        
        checks_count = (duration_minutes * 60) // self.ping_interval
        failed_checks = 0
        latencies = []
        
        for i in range(checks_count):
            # Check connectivity
            connectivity = await self.check_internet_connectivity()
            
            monitoring_data['checks'].append(connectivity)
            
            if connectivity['status'] == 'offline':
                failed_checks += 1
                
                # Detect outage
                if failed_checks >= self.outage_threshold:
                    outage = {
                        'detected_at': connectivity['timestamp'],
                        'duration_seconds': failed_checks * self.ping_interval
                    }
                    monitoring_data['outages'].append(outage)
                    
                    # Send alert
                    await self._send_outage_alert(db, user_id, outage)
            else:
                failed_checks = 0  # Reset counter
                
                if connectivity['average_latency_ms']:
                    latencies.append(connectivity['average_latency_ms'])
            
            # Wait for next check
            if i < checks_count - 1:
                await asyncio.sleep(self.ping_interval)
        
        # Calculate statistics
        if latencies:
            monitoring_data['average_latency'] = round(sum(latencies) / len(latencies), 2)
            monitoring_data['max_latency'] = round(max(latencies), 2)
            monitoring_data['min_latency'] = round(min(latencies), 2)
        
        successful_checks = len(monitoring_data['checks']) - sum(
            1 for c in monitoring_data['checks'] if c['status'] == 'offline'
        )
        monitoring_data['uptime_percentage'] = round(
            (successful_checks / len(monitoring_data['checks'])) * 100, 2
        )
        
        monitoring_data['end_time'] = datetime.utcnow().isoformat()
        
        return monitoring_data
    
    async def _send_outage_alert(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        outage: Dict
    ):
        """Send alert for internet outage"""
        
        alert = Alert(
            user_id=user_id,
            title="🌐 Internet Outage Detected",
            message=f"Your internet connection has been down for {outage['duration_seconds']} seconds.\n\nDetected at: {outage['detected_at']}",
            severity='critical',
            category='internet_outage'
        )
        
        db.add(alert)
        await db.commit()
    
    async def get_connection_quality(self) -> Dict[str, any]:
        """
        Get overall connection quality score
        """
        
        # Run connectivity check
        connectivity = await self.check_internet_connectivity()
        
        if connectivity['status'] == 'offline':
            return {
                'quality': 'poor',
                'score': 0,
                'message': 'No internet connection'
            }
        
        avg_latency = connectivity.get('average_latency_ms', 0)
        
        # Score based on latency
        if avg_latency < 20:
            quality = 'excellent'
            score = 100
        elif avg_latency < 50:
            quality = 'good'
            score = 80
        elif avg_latency < 100:
            quality = 'fair'
            score = 60
        else:
            quality = 'poor'
            score = 40
        
        return {
            'quality': quality,
            'score': score,
            'latency_ms': avg_latency,
            'message': f"Connection quality is {quality} (avg latency: {avg_latency}ms)"
        }
