import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from backend.models.device import Device, DeviceHistory
from backend.models.user import Alert
import uuid

logger = logging.getLogger(__name__)

class PresenceDetectionSystem:
    """
    📊 Tier 1 Feature #2: Presence Detection System
    
    Tracks:
    - Device online/offline events
    - First seen / last seen timestamps
    - Connection duration analytics
    - Presence patterns
    
    Provides insights like:
    "John's phone left the network at 08:32"
    "Device typically online 9am-5pm on weekdays"
    """
    
    def __init__(self):
        self.presence_cache = {}
        self.pattern_cache = {}
    
    async def track_device_presence(
        self,
        db: AsyncSession,
        device_id: uuid.UUID,
        status: str,
        timestamp: datetime = None
    ) -> Dict[str, any]:
        """
        Track device presence change
        Returns presence event details
        """
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Get device
        result = await db.execute(
            select(Device).where(Device.id == device_id)
        )
        device = result.scalar_one_or_none()
        
        if not device:
            return {}
        
        old_status = device.status
        
        # Detect status change
        if old_status != status:
            event = await self._create_presence_event(
                db,
                device,
                old_status,
                status,
                timestamp
            )
            
            # Update device status
            device.status = status
            if status == 'online':
                device.last_seen = timestamp
            
            await db.commit()
            
            return event
        
        return {}
    
    async def _create_presence_event(
        self,
        db: AsyncSession,
        device: Device,
        old_status: str,
        new_status: str,
        timestamp: datetime
    ) -> Dict[str, any]:
        """Create presence event and alert"""
        
        event = {
            'device_id': str(device.id),
            'device_name': device.name or device.hostname or 'Unknown Device',
            'old_status': old_status,
            'new_status': new_status,
            'timestamp': timestamp.isoformat(),
            'event_type': 'online' if new_status == 'online' else 'offline'
        }
        
        # Calculate connection duration if going offline
        if new_status == 'offline' and device.last_seen:
            duration = timestamp - device.last_seen
            event['duration_seconds'] = duration.total_seconds()
            event['duration_formatted'] = self._format_duration(duration)
        
        # Create history entry
        history = DeviceHistory(
            device_id=device.id,
            timestamp=timestamp,
            status=new_status,
            ip_address=device.ip_address,
            open_ports=device.open_ports
        )
        db.add(history)
        
        # Create alert for new devices or unusual events
        alert_message = None
        alert_severity = 'info'
        
        if new_status == 'online':
            if device.is_new:
                alert_message = f"New device '{event['device_name']}' joined the network"
                alert_severity = 'warning'
            else:
                alert_message = f"Device '{event['device_name']}' came online"
        else:
            alert_message = f"Device '{event['device_name']}' went offline"
        
        # Check for unusual timing
        is_unusual = await self._is_unusual_timing(db, device, timestamp)
        if is_unusual:
            alert_message += " (unusual time)"
            alert_severity = 'warning'
        
        # Create alert
        if alert_message:
            alert = Alert(
                user_id=device.user_id,
                title=f"Device {event['event_type'].title()}",
                message=alert_message,
                severity=alert_severity,
                category='presence'
            )
            db.add(alert)
        
        return event
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration in human-readable format"""
        
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} seconds"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            return f"{days}d {hours}h"
    
    async def get_device_presence_history(
        self,
        db: AsyncSession,
        device_id: uuid.UUID,
        days: int = 7
    ) -> List[Dict[str, any]]:
        """Get device presence history"""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(DeviceHistory)
            .where(
                and_(
                    DeviceHistory.device_id == device_id,
                    DeviceHistory.timestamp >= since
                )
            )
            .order_by(DeviceHistory.timestamp.desc())
        )
        
        history = result.scalars().all()
        
        return [
            {
                'timestamp': h.timestamp.isoformat(),
                'status': h.status,
                'ip_address': h.ip_address
            }
            for h in history
        ]
    
    async def analyze_presence_patterns(
        self,
        db: AsyncSession,
        device_id: uuid.UUID
    ) -> Dict[str, any]:
        """
        Analyze device presence patterns
        Returns typical online times, usage patterns, etc.
        """
        
        # Get 30 days of history
        history = await self.get_device_presence_history(db, device_id, days=30)
        
        if len(history) < 10:
            return {
                'pattern': 'insufficient_data',
                'message': 'Not enough data to determine pattern'
            }
        
        # Analyze patterns
        online_times = []
        offline_times = []
        
        for event in history:
            hour = datetime.fromisoformat(event['timestamp']).hour
            if event['status'] == 'online':
                online_times.append(hour)
            else:
                offline_times.append(hour)
        
        # Determine typical online hours
        if online_times:
            avg_online_hour = sum(online_times) // len(online_times)
            
            # Categorize usage pattern
            if 6 <= avg_online_hour <= 22:
                pattern = 'daytime_usage'
                message = 'Typically online during daytime hours'
            else:
                pattern = 'nighttime_usage'
                message = 'Typically online during nighttime hours'
        else:
            pattern = 'always_online'
            message = 'Device is always online'
        
        # Calculate uptime percentage
        online_count = len([h for h in history if h['status'] == 'online'])
        uptime_percentage = (online_count / len(history)) * 100
        
        return {
            'pattern': pattern,
            'message': message,
            'uptime_percentage': round(uptime_percentage, 2),
            'typical_online_hours': list(set(online_times)),
            'total_events': len(history)
        }
    
    async def _is_unusual_timing(
        self,
        db: AsyncSession,
        device: Device,
        timestamp: datetime
    ) -> bool:
        """Check if device activity is at unusual time"""
        
        # Get device pattern
        pattern = await self.analyze_presence_patterns(db, device.id)
        
        if pattern.get('pattern') == 'insufficient_data':
            return False
        
        current_hour = timestamp.hour
        typical_hours = pattern.get('typical_online_hours', [])
        
        if not typical_hours:
            return False
        
        # Check if current hour is far from typical hours
        min_hour = min(typical_hours)
        max_hour = max(typical_hours)
        
        # Consider unusual if outside typical range by more than 3 hours
        if current_hour < min_hour - 3 or current_hour > max_hour + 3:
            return True
        
        return False
    
    async def get_network_presence_summary(
        self,
        db: AsyncSession,
        network_id: uuid.UUID
    ) -> Dict[str, any]:
        """Get presence summary for entire network"""
        
        result = await db.execute(
            select(Device).where(Device.network_id == network_id)
        )
        devices = result.scalars().all()
        
        online_devices = [d for d in devices if d.status == 'online']
        offline_devices = [d for d in devices if d.status == 'offline']
        
        # Get recent activity (last 24 hours)
        since = datetime.utcnow() - timedelta(hours=24)
        
        recent_activity = []
        for device in devices:
            if device.last_seen and device.last_seen >= since:
                recent_activity.append({
                    'device_id': str(device.id),
                    'device_name': device.name or device.hostname or 'Unknown',
                    'last_seen': device.last_seen.isoformat(),
                    'status': device.status
                })
        
        return {
            'total_devices': len(devices),
            'online_devices': len(online_devices),
            'offline_devices': len(offline_devices),
            'recent_activity': sorted(
                recent_activity,
                key=lambda x: x['last_seen'],
                reverse=True
            )[:10]
        }
