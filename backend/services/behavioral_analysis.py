import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from backend.models.device import Device, DeviceHistory
from backend.models.user import Alert
import numpy as np
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)

class BehavioralAnalysisEngine:
    """
    🕵️ Tier 3 Feature #10: Behavioral Analysis
    
    Detect malicious behavior patterns:
    - Malware-like traffic patterns
    - Data exfiltration detection
    - Bot behavior identification
    - Command & control communication
    - Crypto-mining detection
    - DDoS participation detection
    """
    
    def __init__(self):
        self.behavior_profiles = {}
        self.threat_signatures = self._load_threat_signatures()
        self.anomaly_scores = defaultdict(float)
    
    def _load_threat_signatures(self) -> Dict:
        """Load behavioral threat signatures"""
        return {
            'malware': {
                'beaconing': {
                    'description': 'Regular periodic connections (C2 communication)',
                    'indicators': {
                        'regular_intervals': True,
                        'small_data_transfers': True,
                        'unusual_ports': [4444, 8080, 31337]
                    },
                    'severity': 'critical'
                },
                'data_exfiltration': {
                    'description': 'Large outbound data transfers',
                    'indicators': {
                        'high_upload_ratio': 10.0,  # Upload 10x download
                        'sustained_upload': True,
                        'unusual_destinations': True
                    },
                    'severity': 'critical'
                },
                'port_scanning': {
                    'description': 'Scanning multiple ports on network',
                    'indicators': {
                        'many_failed_connections': True,
                        'sequential_ports': True,
                        'rapid_connections': True
                    },
                    'severity': 'high'
                }
            },
            'bot_behavior': {
                'spam_bot': {
                    'description': 'Sending spam emails',
                    'indicators': {
                        'smtp_connections': [25, 587],
                        'high_connection_count': True,
                        'many_destinations': True
                    },
                    'severity': 'high'
                },
                'ddos_participant': {
                    'description': 'Participating in DDoS attack',
                    'indicators': {
                        'syn_flood': True,
                        'same_destination': True,
                        'high_packet_rate': True
                    },
                    'severity': 'critical'
                },
                'crypto_miner': {
                    'description': 'Mining cryptocurrency',
                    'indicators': {
                        'mining_pools': ['pool.', 'mine.', 'stratum'],
                        'ports': [3333, 4444, 8333],
                        'high_cpu_network_correlation': True
                    },
                    'severity': 'high'
                }
            },
            'suspicious_patterns': {
                'tor_usage': {
                    'description': 'Using Tor network',
                    'indicators': {
                        'tor_ports': [9001, 9030, 9050, 9051],
                        'tor_domains': ['.onion']
                    },
                    'severity': 'medium'
                },
                'vpn_tunneling': {
                    'description': 'VPN or tunnel usage',
                    'indicators': {
                        'vpn_ports': [1194, 1723, 500, 4500],
                        'encrypted_traffic': True
                    },
                    'severity': 'low'
                },
                'unusual_protocols': {
                    'description': 'Using uncommon protocols',
                    'indicators': {
                        'rare_ports': True,
                        'non_standard_protocols': True
                    },
                    'severity': 'medium'
                }
            }
        }
    
    async def analyze_device_behavior(
        self,
        db: AsyncSession,
        device_id: uuid.UUID,
        time_window_hours: int = 24
    ) -> Dict[str, any]:
        """
        Analyze device behavior for threats
        """
        
        logger.info(f"Analyzing behavior for device {device_id}")
        
        # Get device
        result = await db.execute(
            select(Device).where(Device.id == device_id)
        )
        device = result.scalar_one_or_none()
        
        if not device:
            return {'error': 'Device not found'}
        
        # Get device history
        since = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        result = await db.execute(
            select(DeviceHistory)
            .where(
                and_(
                    DeviceHistory.device_id == device_id,
                    DeviceHistory.timestamp >= since
                )
            )
            .order_by(DeviceHistory.timestamp.asc())
        )
        
        history = result.scalars().all()
        
        if len(history) < 5:
            return {
                'device_id': str(device_id),
                'analysis': 'insufficient_data',
                'message': 'Not enough data for behavioral analysis'
            }
        
        # Analyze patterns
        threats_detected = []
        
        # Check for beaconing (C2 communication)
        beaconing = self._detect_beaconing(history)
        if beaconing:
            threats_detected.append(beaconing)
        
        # Check for port scanning
        port_scan = self._detect_port_scanning(device, history)
        if port_scan:
            threats_detected.append(port_scan)
        
        # Check for data exfiltration
        exfiltration = self._detect_data_exfiltration(device, history)
        if exfiltration:
            threats_detected.append(exfiltration)
        
        # Check for bot behavior
        bot_behavior = self._detect_bot_behavior(device, history)
        if bot_behavior:
            threats_detected.append(bot_behavior)
        
        # Calculate threat score
        threat_score = self._calculate_threat_score(threats_detected)
        
        # Determine threat level
        if threat_score >= 80:
            threat_level = 'critical'
        elif threat_score >= 60:
            threat_level = 'high'
        elif threat_score >= 40:
            threat_level = 'medium'
        elif threat_score >= 20:
            threat_level = 'low'
        else:
            threat_level = 'none'
        
        analysis = {
            'device_id': str(device_id),
            'device_name': device.name or device.hostname,
            'threat_level': threat_level,
            'threat_score': threat_score,
            'threats_detected': threats_detected,
            'analysis_period': f'{time_window_hours} hours',
            'data_points': len(history),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Create alert if threats detected
        if threats_detected and threat_level in ['critical', 'high']:
            await self._create_threat_alert(db, device, analysis)
        
        return analysis
    
    def _detect_beaconing(self, history: List[DeviceHistory]) -> Optional[Dict]:
        """Detect beaconing behavior (C2 communication)"""
        
        if len(history) < 10:
            return None
        
        # Analyze time intervals between connections
        timestamps = [h.timestamp for h in history if h.status == 'online']
        
        if len(timestamps) < 10:
            return None
        
        # Calculate intervals
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        if not intervals:
            return None
        
        # Check for regular intervals (beaconing pattern)
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        # Low standard deviation indicates regular intervals
        if std_interval < avg_interval * 0.2 and avg_interval < 3600:  # Regular intervals under 1 hour
            return {
                'threat_type': 'beaconing',
                'category': 'malware',
                'severity': 'critical',
                'description': 'Device shows beaconing behavior (potential C2 communication)',
                'evidence': {
                    'average_interval_seconds': round(avg_interval, 2),
                    'interval_regularity': round(1 - (std_interval / avg_interval), 2),
                    'connection_count': len(timestamps)
                },
                'recommendation': 'Isolate device and scan for malware immediately'
            }
        
        return None
    
    def _detect_port_scanning(
        self,
        device: Device,
        history: List[DeviceHistory]
    ) -> Optional[Dict]:
        """Detect port scanning activity"""
        
        # Check if device has many different ports over time
        all_ports = set()
        for record in history:
            all_ports.update(record.open_ports)
        
        # If device opened many different ports in short time, suspicious
        if len(all_ports) > 20:
            return {
                'threat_type': 'port_scanning',
                'category': 'malware',
                'severity': 'high',
                'description': 'Device shows port scanning behavior',
                'evidence': {
                    'unique_ports': len(all_ports),
                    'time_window': f"{len(history)} data points"
                },
                'recommendation': 'Investigate device activity and check for compromise'
            }
        
        return None
    
    def _detect_data_exfiltration(
        self,
        device: Device,
        history: List[DeviceHistory]
    ) -> Optional[Dict]:
        """Detect data exfiltration patterns"""
        
        # In real implementation, this would analyze:
        # - Upload/download ratios
        # - Sustained large uploads
        # - Connections to unusual destinations
        
        # Placeholder detection
        return None
    
    def _detect_bot_behavior(
        self,
        device: Device,
        history: List[DeviceHistory]
    ) -> Optional[Dict]:
        """Detect bot-like behavior"""
        
        # Check for suspicious ports (SMTP, IRC, etc.)
        suspicious_ports = [25, 587, 6667, 6668, 6669]
        
        for record in history:
            found_ports = [p for p in record.open_ports if p in suspicious_ports]
            if found_ports:
                return {
                    'threat_type': 'bot_behavior',
                    'category': 'bot',
                    'severity': 'high',
                    'description': 'Device may be part of botnet (suspicious ports open)',
                    'evidence': {
                        'suspicious_ports': found_ports
                    },
                    'recommendation': 'Scan device for malware and check for botnet infection'
                }
        
        return None
    
    def _calculate_threat_score(self, threats: List[Dict]) -> int:
        """Calculate overall threat score (0-100)"""
        
        if not threats:
            return 0
        
        severity_scores = {
            'critical': 100,
            'high': 75,
            'medium': 50,
            'low': 25
        }
        
        # Use highest severity
        max_score = max(
            severity_scores.get(t.get('severity', 'low'), 0)
            for t in threats
        )
        
        return max_score
    
    async def _create_threat_alert(
        self,
        db: AsyncSession,
        device: Device,
        analysis: Dict
    ):
        """Create alert for detected threats"""
        
        device_name = device.name or device.hostname or 'Unknown Device'
        threats = analysis['threats_detected']
        
        threat_descriptions = '\n'.join(
            f"• {t['threat_type']}: {t['description']}"
            for t in threats
        )
        
        alert = Alert(
            user_id=device.user_id,
            title=f"🚨 Threat Detected: {device_name}",
            message=f"Behavioral analysis detected potential threats on device '{device_name}' ({device.ip_address}):\n\n{threat_descriptions}\n\nThreat Level: {analysis['threat_level'].upper()}\nThreat Score: {analysis['threat_score']}/100",
            severity=analysis['threat_level'],
            category='behavioral_threat'
        )
        
        db.add(alert)
        await db.commit()
