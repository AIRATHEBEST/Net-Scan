import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from backend.models.device import Device, DeviceHistory
from backend.models.user import Alert
import numpy as np
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)

class AIInsightsEngine:
    """
    🧠 Tier 2 Feature #6: AI Insights Layer
    
    Turn raw data into actionable insights:
    - "Your network is 30% slower due to device X"
    - "Camera is sending unusual traffic"
    - Anomaly detection with explanations
    - Performance recommendations
    - Security risk analysis
    """
    
    def __init__(self):
        self.insights_cache = {}
        self.anomaly_thresholds = {
            'bandwidth_spike': 3.0,  # 3x normal usage
            'connection_spike': 5.0,  # 5x normal connections
            'unusual_port': 0.1,  # Port seen <10% of time
            'traffic_pattern_change': 0.7  # 70% different from normal
        }
    
    async def analyze_network_health(
        self,
        db: AsyncSession,
        network_id: uuid.UUID
    ) -> Dict[str, any]:
        """
        Comprehensive network health analysis
        Returns insights, anomalies, and recommendations
        """
        
        logger.info(f"Analyzing network health for network {network_id}")
        
        # Get all devices on network
        result = await db.execute(
            select(Device).where(Device.network_id == network_id)
        )
        devices = result.scalars().all()
        
        insights = {
            'overall_health': 'good',
            'health_score': 85,
            'insights': [],
            'anomalies': [],
            'recommendations': [],
            'performance_analysis': {},
            'security_analysis': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Performance Analysis
        performance = await self._analyze_performance(db, devices)
        insights['performance_analysis'] = performance
        insights['insights'].extend(performance.get('insights', []))
        
        # Security Analysis
        security = await self._analyze_security(db, devices)
        insights['security_analysis'] = security
        insights['insights'].extend(security.get('insights', []))
        
        # Anomaly Detection
        anomalies = await self._detect_anomalies(db, devices)
        insights['anomalies'] = anomalies
        
        # Generate Recommendations
        recommendations = await self._generate_recommendations(
            performance, security, anomalies
        )
        insights['recommendations'] = recommendations
        
        # Calculate overall health score
        insights['health_score'] = self._calculate_health_score(
            performance, security, anomalies
        )
        
        # Determine overall health status
        if insights['health_score'] >= 80:
            insights['overall_health'] = 'excellent'
        elif insights['health_score'] >= 60:
            insights['overall_health'] = 'good'
        elif insights['health_score'] >= 40:
            insights['overall_health'] = 'fair'
        else:
            insights['overall_health'] = 'poor'
        
        return insights
    
    async def _analyze_performance(
        self,
        db: AsyncSession,
        devices: List[Device]
    ) -> Dict[str, any]:
        """Analyze network performance"""
        
        insights = []
        metrics = {
            'total_devices': len(devices),
            'online_devices': len([d for d in devices if d.status == 'online']),
            'average_response_time': 0,
            'bandwidth_usage': {},
            'slow_devices': []
        }
        
        # Identify slow devices
        for device in devices:
            if device.status == 'online':
                # Check if device has high latency or low bandwidth
                # (In real implementation, this would come from actual measurements)
                pass
        
        # Network congestion analysis
        online_ratio = metrics['online_devices'] / max(metrics['total_devices'], 1)
        
        if online_ratio > 0.8:
            insights.append({
                'type': 'performance',
                'severity': 'warning',
                'title': 'High Network Load',
                'message': f"{metrics['online_devices']} devices online ({int(online_ratio * 100)}% capacity). Network may be congested.",
                'recommendation': 'Consider limiting bandwidth-heavy activities or upgrading network capacity.'
            })
        
        # Identify bandwidth hogs (devices using disproportionate bandwidth)
        # This would use DPI data in real implementation
        
        metrics['insights'] = insights
        return metrics
    
    async def _analyze_security(
        self,
        db: AsyncSession,
        devices: List[Device]
    ) -> Dict[str, any]:
        """Analyze network security"""
        
        insights = []
        metrics = {
            'vulnerable_devices': 0,
            'critical_alerts': 0,
            'unknown_devices': 0,
            'suspicious_activity': []
        }
        
        for device in devices:
            # Check for security issues
            if device.security_level == 'critical':
                metrics['vulnerable_devices'] += 1
                
                insights.append({
                    'type': 'security',
                    'severity': 'critical',
                    'title': f'Critical Security Issue: {device.name or device.hostname}',
                    'message': f"Device {device.ip_address} has critical security vulnerabilities.",
                    'recommendation': f'Update device firmware or isolate from network.'
                })
            
            # Check for unknown devices
            if device.device_type == 'unknown':
                metrics['unknown_devices'] += 1
            
            # Check for suspicious ports
            suspicious_ports = [23, 3389, 5900, 1433, 3306]
            open_suspicious = [p for p in device.open_ports if p in suspicious_ports]
            
            if open_suspicious:
                metrics['suspicious_activity'].append({
                    'device': device.name or device.hostname,
                    'ip': device.ip_address,
                    'issue': f"Suspicious ports open: {', '.join(map(str, open_suspicious))}"
                })
                
                insights.append({
                    'type': 'security',
                    'severity': 'warning',
                    'title': f'Suspicious Ports: {device.name or device.hostname}',
                    'message': f"Device has potentially dangerous ports open: {', '.join(map(str, open_suspicious))}",
                    'recommendation': 'Close unnecessary ports or investigate device purpose.'
                })
        
        # Summary insights
        if metrics['vulnerable_devices'] > 0:
            insights.append({
                'type': 'security',
                'severity': 'critical',
                'title': 'Vulnerable Devices Detected',
                'message': f"{metrics['vulnerable_devices']} device(s) have critical security issues.",
                'recommendation': 'Review and secure vulnerable devices immediately.'
            })
        
        if metrics['unknown_devices'] > 3:
            insights.append({
                'type': 'security',
                'severity': 'warning',
                'title': 'Many Unknown Devices',
                'message': f"{metrics['unknown_devices']} devices could not be identified.",
                'recommendation': 'Review unknown devices and label them for better security monitoring.'
            })
        
        metrics['insights'] = insights
        return metrics
    
    async def _detect_anomalies(
        self,
        db: AsyncSession,
        devices: List[Device]
    ) -> List[Dict[str, any]]:
        """Detect network anomalies using ML-style analysis"""
        
        anomalies = []
        
        for device in devices:
            # Get device history (last 7 days)
            since = datetime.utcnow() - timedelta(days=7)
            
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
            
            if len(history) < 10:
                continue  # Not enough data
            
            # Analyze patterns
            device_anomalies = await self._analyze_device_patterns(device, history)
            anomalies.extend(device_anomalies)
        
        return anomalies
    
    async def _analyze_device_patterns(
        self,
        device: Device,
        history: List[DeviceHistory]
    ) -> List[Dict[str, any]]:
        """Analyze individual device patterns for anomalies"""
        
        anomalies = []
        device_name = device.name or device.hostname or f"Device {device.ip_address}"
        
        # Check for unusual port activity
        all_ports = []
        for record in history:
            all_ports.extend(record.open_ports)
        
        if all_ports:
            # Find ports that appear infrequently
            port_counts = defaultdict(int)
            for port in all_ports:
                port_counts[port] += 1
            
            total_records = len(history)
            unusual_ports = [
                port for port, count in port_counts.items()
                if count / total_records < self.anomaly_thresholds['unusual_port']
            ]
            
            if unusual_ports:
                anomalies.append({
                    'device': device_name,
                    'type': 'unusual_ports',
                    'severity': 'warning',
                    'description': f"Unusual ports detected: {', '.join(map(str, unusual_ports))}",
                    'recommendation': 'Investigate why these ports are occasionally open.'
                })
        
        # Check for status changes (frequent disconnects)
        status_changes = 0
        prev_status = None
        
        for record in sorted(history, key=lambda x: x.timestamp):
            if prev_status and record.status != prev_status:
                status_changes += 1
            prev_status = record.status
        
        if status_changes > 20:  # More than 20 status changes in 7 days
            anomalies.append({
                'device': device_name,
                'type': 'unstable_connection',
                'severity': 'warning',
                'description': f"Device has unstable connection ({status_changes} disconnects in 7 days)",
                'recommendation': 'Check device WiFi signal strength or network stability.'
            })
        
        return anomalies
    
    async def _generate_recommendations(
        self,
        performance: Dict,
        security: Dict,
        anomalies: List[Dict]
    ) -> List[Dict[str, any]]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Performance recommendations
        if performance.get('online_devices', 0) > 20:
            recommendations.append({
                'category': 'performance',
                'priority': 'medium',
                'title': 'Consider Network Upgrade',
                'description': 'You have many devices on the network. Consider upgrading to a mesh network or better router.',
                'impact': 'Improved speed and reliability for all devices'
            })
        
        # Security recommendations
        if security.get('vulnerable_devices', 0) > 0:
            recommendations.append({
                'category': 'security',
                'priority': 'high',
                'title': 'Update Vulnerable Devices',
                'description': f"{security['vulnerable_devices']} device(s) have security issues. Update firmware immediately.",
                'impact': 'Reduced risk of network compromise'
            })
        
        if security.get('unknown_devices', 0) > 5:
            recommendations.append({
                'category': 'security',
                'priority': 'medium',
                'title': 'Identify Unknown Devices',
                'description': 'Many devices could not be identified. Label them for better security monitoring.',
                'impact': 'Better visibility and control over network access'
            })
        
        # Anomaly-based recommendations
        unstable_devices = [a for a in anomalies if a.get('type') == 'unstable_connection']
        if len(unstable_devices) > 2:
            recommendations.append({
                'category': 'performance',
                'priority': 'medium',
                'title': 'Improve WiFi Coverage',
                'description': f"{len(unstable_devices)} devices have unstable connections. Consider adding WiFi extenders.",
                'impact': 'More reliable connections for mobile devices'
            })
        
        return recommendations
    
    def _calculate_health_score(
        self,
        performance: Dict,
        security: Dict,
        anomalies: List[Dict]
    ) -> int:
        """Calculate overall network health score (0-100)"""
        
        score = 100
        
        # Deduct for security issues
        score -= security.get('vulnerable_devices', 0) * 15
        score -= security.get('unknown_devices', 0) * 2
        score -= len(security.get('suspicious_activity', [])) * 5
        
        # Deduct for performance issues
        online_ratio = performance.get('online_devices', 0) / max(performance.get('total_devices', 1), 1)
        if online_ratio > 0.8:
            score -= 10
        
        # Deduct for anomalies
        score -= len(anomalies) * 3
        
        return max(0, min(100, score))
    
    async def get_device_insights(
        self,
        db: AsyncSession,
        device_id: uuid.UUID
    ) -> Dict[str, any]:
        """Get AI insights for specific device"""
        
        result = await db.execute(
            select(Device).where(Device.id == device_id)
        )
        device = result.scalar_one_or_none()
        
        if not device:
            return {'error': 'Device not found'}
        
        # Get device history
        since = datetime.utcnow() - timedelta(days=30)
        
        result = await db.execute(
            select(DeviceHistory)
            .where(
                and_(
                    DeviceHistory.device_id == device_id,
                    DeviceHistory.timestamp >= since
                )
            )
        )
        
        history = result.scalars().all()
        
        insights = {
            'device_name': device.name or device.hostname,
            'insights': [],
            'behavior_analysis': {},
            'recommendations': []
        }
        
        # Behavior analysis
        if history:
            online_count = len([h for h in history if h.status == 'online'])
            uptime_percentage = (online_count / len(history)) * 100
            
            insights['behavior_analysis'] = {
                'uptime_percentage': round(uptime_percentage, 2),
                'reliability': 'excellent' if uptime_percentage > 95 else 'good' if uptime_percentage > 80 else 'poor',
                'total_events': len(history)
            }
            
            # Generate insights
            if uptime_percentage < 80:
                insights['insights'].append({
                    'type': 'reliability',
                    'severity': 'warning',
                    'message': f"Device has {100 - uptime_percentage:.1f}% downtime. Consider checking connection stability."
                })
        
        # Security insights
        if device.security_level == 'critical':
            insights['insights'].append({
                'type': 'security',
                'severity': 'critical',
                'message': 'Device has critical security vulnerabilities. Update firmware immediately.'
            })
        
        return insights
