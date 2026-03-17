import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from backend.models.device import Device, SecurityLevel
from backend.models.user import Alert, User
from backend.services.notification_service import NotificationService
import uuid

logger = logging.getLogger(__name__)

class SmartAlertsEngine:
    """
    🔔 Tier 1 Feature #3: Smart Alerts Engine
    
    Not just alerts — meaningful, actionable alerts:
    - New unknown device detection
    - Device active at unusual times
    - Suspicious open ports
    - Device spoofing detection
    - Security threats
    - Bandwidth anomalies
    """
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.alert_rules = self._load_alert_rules()
    
    def _load_alert_rules(self) -> Dict:
        """Load smart alert rules"""
        return {
            'suspicious_ports': {
                'critical': [23, 3389, 5900, 1433, 3306],  # Telnet, RDP, VNC, SQL
                'warning': [21, 25, 110, 143, 445],  # FTP, SMTP, POP3, IMAP, SMB
                'description': {
                    23: 'Telnet (unencrypted remote access)',
                    3389: 'RDP (Remote Desktop)',
                    5900: 'VNC (Remote Desktop)',
                    1433: 'MS SQL Server',
                    3306: 'MySQL Database',
                    21: 'FTP (unencrypted file transfer)',
                    445: 'SMB (file sharing)'
                }
            },
            'unusual_timing': {
                'night_hours': list(range(0, 6)),  # 12am-6am
                'work_hours': list(range(9, 17)),  # 9am-5pm
            },
            'mac_spoofing': {
                'check_interval_hours': 24,
                'max_ip_changes': 5
            },
            'bandwidth_anomaly': {
                'threshold_multiplier': 3.0,  # 3x normal usage
                'check_window_hours': 1
            }
        }
    
    async def check_new_device(
        self,
        db: AsyncSession,
        device: Device
    ) -> Optional[Dict[str, any]]:
        """
        Alert for new unknown devices
        """
        
        if not device.is_new:
            return None
        
        # Assess threat level
        threat_level = 'info'
        concerns = []
        
        # Check for suspicious characteristics
        if device.security_level == SecurityLevel.CRITICAL:
            threat_level = 'critical'
            concerns.append('Critical security issues detected')
        elif device.security_level == SecurityLevel.WARNING:
            threat_level = 'warning'
            concerns.append('Security warnings present')
        
        # Check for suspicious ports
        suspicious_ports = self._check_suspicious_ports(device.open_ports)
        if suspicious_ports['critical']:
            threat_level = 'critical'
            concerns.append(f"Critical ports open: {', '.join(map(str, suspicious_ports['critical']))}")
        elif suspicious_ports['warning']:
            if threat_level == 'info':
                threat_level = 'warning'
            concerns.append(f"Warning ports open: {', '.join(map(str, suspicious_ports['warning']))}")
        
        # Check if device type is unknown
        if device.device_type == 'unknown':
            concerns.append('Device type could not be identified')
        
        # Create alert
        alert_title = "🚨 New Device Detected" if threat_level == 'critical' else "⚠️ New Device Joined Network"
        
        device_name = device.name or device.hostname or f"Unknown ({device.vendor})"
        
        alert_message = f"Device '{device_name}' ({device.ip_address}) joined your network.\n\n"
        
        if concerns:
            alert_message += "Concerns:\n" + "\n".join(f"• {c}" for c in concerns)
        else:
            alert_message += "No immediate concerns detected."
        
        alert = Alert(
            user_id=device.user_id,
            title=alert_title,
            message=alert_message,
            severity=threat_level,
            category='new_device'
        )
        
        db.add(alert)
        await db.commit()
        
        # Send push notification
        result = await db.execute(
            select(User).where(User.id == device.user_id)
        )
        user = result.scalar_one_or_none()
        
        if user and user.push_notifications and user.fcm_token:
            await self.notification_service.send_push_notification(
                user.fcm_token,
                alert_title,
                f"{device_name} joined your network",
                {'device_id': str(device.id), 'alert_type': 'new_device'}
            )
        
        return {
            'alert_id': str(alert.id),
            'threat_level': threat_level,
            'concerns': concerns
        }
    
    def _check_suspicious_ports(self, open_ports: List[int]) -> Dict[str, List[int]]:
        """Check for suspicious open ports"""
        
        rules = self.alert_rules['suspicious_ports']
        
        critical = [p for p in open_ports if p in rules['critical']]
        warning = [p for p in open_ports if p in rules['warning']]
        
        return {
            'critical': critical,
            'warning': warning,
            'descriptions': {
                p: rules['description'].get(p, 'Unknown service')
                for p in (critical + warning)
            }
        }
    
    async def check_unusual_activity(
        self,
        db: AsyncSession,
        device: Device,
        timestamp: datetime = None
    ) -> Optional[Dict[str, any]]:
        """
        Check for unusual device activity timing
        """
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        current_hour = timestamp.hour
        
        # Get device's typical usage pattern
        from backend.services.presence_detection import PresenceDetectionSystem
        presence_system = PresenceDetectionSystem()
        
        pattern = await presence_system.analyze_presence_patterns(db, device.id)
        
        if pattern.get('pattern') == 'insufficient_data':
            return None
        
        typical_hours = pattern.get('typical_online_hours', [])
        
        if not typical_hours:
            return None
        
        # Check if current hour is unusual
        is_unusual = False
        reason = ""
        
        # Night activity for typically daytime device
        if pattern.get('pattern') == 'daytime_usage' and current_hour in self.alert_rules['unusual_timing']['night_hours']:
            is_unusual = True
            reason = "Device active during unusual nighttime hours"
        
        # Daytime activity for typically nighttime device
        elif pattern.get('pattern') == 'nighttime_usage' and current_hour in self.alert_rules['unusual_timing']['work_hours']:
            is_unusual = True
            reason = "Device active during unusual daytime hours"
        
        if is_unusual:
            device_name = device.name or device.hostname or 'Unknown Device'
            
            alert = Alert(
                user_id=device.user_id,
                title="⏰ Unusual Device Activity",
                message=f"Device '{device_name}' is active at an unusual time.\n\n{reason}\n\nTypical online hours: {min(typical_hours)}:00 - {max(typical_hours)}:00",
                severity='warning',
                category='unusual_activity'
            )
            
            db.add(alert)
            await db.commit()
            
            return {
                'alert_id': str(alert.id),
                'reason': reason,
                'typical_hours': typical_hours,
                'current_hour': current_hour
            }
        
        return None
    
    async def check_port_scanning(
        self,
        db: AsyncSession,
        device: Device
    ) -> Optional[Dict[str, any]]:
        """
        Detect potential port scanning activity
        """
        
        suspicious_ports = self._check_suspicious_ports(device.open_ports)
        
        if not suspicious_ports['critical'] and not suspicious_ports['warning']:
            return None
        
        device_name = device.name or device.hostname or 'Unknown Device'
        
        # Build alert message
        message_parts = [f"Device '{device_name}' ({device.ip_address}) has suspicious ports open:\n"]
        
        if suspicious_ports['critical']:
            message_parts.append("\n🔴 Critical Ports:")
            for port in suspicious_ports['critical']:
                desc = suspicious_ports['descriptions'].get(port, 'Unknown')
                message_parts.append(f"  • Port {port}: {desc}")
        
        if suspicious_ports['warning']:
            message_parts.append("\n⚠️ Warning Ports:")
            for port in suspicious_ports['warning']:
                desc = suspicious_ports['descriptions'].get(port, 'Unknown')
                message_parts.append(f"  • Port {port}: {desc}")
        
        message_parts.append("\n\nRecommendation: Review this device and close unnecessary ports.")
        
        severity = 'critical' if suspicious_ports['critical'] else 'warning'
        
        alert = Alert(
            user_id=device.user_id,
            title="🔍 Suspicious Ports Detected",
            message="\n".join(message_parts),
            severity=severity,
            category='port_security'
        )
        
        db.add(alert)
        await db.commit()
        
        return {
            'alert_id': str(alert.id),
            'suspicious_ports': suspicious_ports
        }
    
    async def check_mac_spoofing(
        self,
        db: AsyncSession,
        device: Device
    ) -> Optional[Dict[str, any]]:
        """
        Detect potential MAC address spoofing
        Looks for same MAC with multiple IPs or rapid IP changes
        """
        
        # Get device history for last 24 hours
        since = datetime.utcnow() - timedelta(
            hours=self.alert_rules['mac_spoofing']['check_interval_hours']
        )
        
        from backend.models.device import DeviceHistory
        
        result = await db.execute(
            select(DeviceHistory)
            .where(
                and_(
                    DeviceHistory.device_id == device.id,
                    DeviceHistory.timestamp >= since
                )
            )
            .order_by(DeviceHistory.timestamp.desc())
        )
        
        history = result.scalars().all()
        
        # Check for multiple IP addresses
        unique_ips = set(h.ip_address for h in history if h.ip_address)
        
        if len(unique_ips) > self.alert_rules['mac_spoofing']['max_ip_changes']:
            device_name = device.name or device.hostname or 'Unknown Device'
            
            alert = Alert(
                user_id=device.user_id,
                title="🚨 Potential MAC Spoofing Detected",
                message=f"Device '{device_name}' (MAC: {device.mac_address}) has used {len(unique_ips)} different IP addresses in the last 24 hours.\n\nThis could indicate:\n• MAC address spoofing\n• DHCP issues\n• Network misconfiguration\n\nIPs used: {', '.join(unique_ips)}",
                severity='critical',
                category='spoofing'
            )
            
            db.add(alert)
            await db.commit()
            
            return {
                'alert_id': str(alert.id),
                'unique_ips': list(unique_ips),
                'ip_change_count': len(unique_ips)
            }
        
        return None
    
    async def check_all_alerts(
        self,
        db: AsyncSession,
        device: Device
    ) -> List[Dict[str, any]]:
        """
        Run all alert checks for a device
        Returns list of triggered alerts
        """
        
        alerts = []
        
        # Check for new device
        new_device_alert = await self.check_new_device(db, device)
        if new_device_alert:
            alerts.append(new_device_alert)
        
        # Check for unusual activity
        unusual_activity_alert = await self.check_unusual_activity(db, device)
        if unusual_activity_alert:
            alerts.append(unusual_activity_alert)
        
        # Check for suspicious ports
        port_alert = await self.check_port_scanning(db, device)
        if port_alert:
            alerts.append(port_alert)
        
        # Check for MAC spoofing
        spoofing_alert = await self.check_mac_spoofing(db, device)
        if spoofing_alert:
            alerts.append(spoofing_alert)
        
        return alerts
