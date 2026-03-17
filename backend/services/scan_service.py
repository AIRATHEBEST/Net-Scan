import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.scanner.network_scanner import NetworkScanner
from backend.scanner.port_scanner import PortScanner
from backend.scanner.mac_vendor import MACVendorLookup
from backend.scanner.device_fingerprint import DeviceFingerprint
from backend.models.device import Device, DeviceHistory, SecurityLevel
from backend.models.network import Network, ScanHistory
from backend.services.notification_service import NotificationService
import uuid

logger = logging.getLogger(__name__)

class ScanService:
    def __init__(self):
        self.network_scanner = NetworkScanner()
        self.port_scanner = PortScanner()
        self.mac_lookup = MACVendorLookup()
        self.fingerprint = DeviceFingerprint()
        self.notification_service = NotificationService()
    
    async def perform_full_scan(
        self,
        db: AsyncSession,
        network_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Dict[str, any]:
        """
        Perform complete network scan including:
        - Device discovery (ARP)
        - Port scanning
        - Service detection
        - Device fingerprinting
        """
        logger.info(f"Starting full scan for network {network_id}")
        
        # Get network info
        result = await db.execute(
            select(Network).where(Network.id == network_id)
        )
        network = result.scalar_one_or_none()
        
        if not network:
            raise ValueError(f"Network {network_id} not found")
        
        # Create scan history
        scan_history = ScanHistory(
            network_id=network_id,
            started_at=datetime.utcnow(),
            status="running"
        )
        db.add(scan_history)
        await db.commit()
        
        try:
            # Step 1: ARP scan for device discovery
            discovered_devices = await self.network_scanner.scan_network(
                network.subnet
            )
            
            logger.info(f"Discovered {len(discovered_devices)} devices")
            
            # Step 2: Process each device
            new_devices = 0
            processed_devices = []
            
            for device_data in discovered_devices:
                try:
                    device_info = await self._process_device(
                        db,
                        device_data,
                        network_id,
                        user_id
                    )
                    
                    if device_info.get('is_new'):
                        new_devices += 1
                    
                    processed_devices.append(device_info)
                    
                except Exception as e:
                    logger.error(f"Error processing device {device_data.get('ip')}: {e}")
            
            # Update scan history
            scan_history.completed_at = datetime.utcnow()
            scan_history.devices_found = len(processed_devices)
            scan_history.new_devices = new_devices
            scan_history.status = "completed"
            await db.commit()
            
            # Send notifications for new devices
            if new_devices > 0:
                await self.notification_service.send_new_device_alert(
                    user_id,
                    new_devices
                )
            
            return {
                'scan_id': str(scan_history.id),
                'devices_found': len(processed_devices),
                'new_devices': new_devices,
                'devices': processed_devices
            }
            
        except Exception as e:
            logger.error(f"Error in full scan: {e}")
            scan_history.status = "failed"
            await db.commit()
            raise
    
    async def _process_device(
        self,
        db: AsyncSession,
        device_data: Dict,
        network_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Dict[str, any]:
        """Process individual device"""
        ip = device_data['ip']
        mac = device_data['mac']
        
        logger.info(f"Processing device {ip} ({mac})")
        
        # Check if device exists
        result = await db.execute(
            select(Device).where(
                Device.mac_address == mac,
                Device.network_id == network_id
            )
        )
        existing_device = result.scalar_one_or_none()
        
        # Lookup vendor
        vendor = await self.mac_lookup.lookup(mac)
        
        # Port scan (quick scan for speed)
        port_info = await self.port_scanner.quick_scan(ip)
        
        # Device fingerprinting
        is_gateway = (ip == await self.network_scanner.get_gateway())
        
        fingerprint_result = await self.fingerprint.identify_device(
            mac=mac,
            ip=ip,
            vendor=vendor,
            hostname=None,  # TODO: Get from DHCP/DNS
            open_ports=port_info['open_ports'],
            services=port_info['services'],
            os_info=port_info['os'],
            is_gateway=is_gateway
        )
        
        # Determine security level
        security_level = self._assess_security(port_info['open_ports'])
        
        if existing_device:
            # Update existing device
            existing_device.ip_address = ip
            existing_device.open_ports = port_info['open_ports']
            existing_device.services = port_info['services']
            existing_device.status = "online"
            existing_device.last_seen = datetime.utcnow()
            existing_device.security_level = security_level
            
            if port_info['os']:
                existing_device.os = port_info['os']['name']
            
            # Add history entry
            history = DeviceHistory(
                device_id=existing_device.id,
                timestamp=datetime.utcnow(),
                status="online",
                ip_address=ip,
                open_ports=port_info['open_ports']
            )
            db.add(history)
            
            await db.commit()
            
            return {
                'id': str(existing_device.id),
                'ip': ip,
                'mac': mac,
                'vendor': vendor,
                'type': existing_device.device_type,
                'is_new': False
            }
        
        else:
            # Create new device
            new_device = Device(
                network_id=network_id,
                user_id=user_id,
                mac_address=mac,
                ip_address=ip,
                vendor=vendor,
                device_type=fingerprint_result['type'],
                open_ports=port_info['open_ports'],
                services=port_info['services'],
                status="online",
                is_new=True,
                security_level=security_level,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow()
            )
            
            if port_info['os']:
                new_device.os = port_info['os']['name']
            
            db.add(new_device)
            await db.commit()
            
            return {
                'id': str(new_device.id),
                'ip': ip,
                'mac': mac,
                'vendor': vendor,
                'type': new_device.device_type,
                'is_new': True
            }
    
    def _assess_security(self, open_ports: List[int]) -> SecurityLevel:
        """Assess device security level based on open ports"""
        critical_ports = {22, 23, 3389, 5900}  # SSH, Telnet, RDP, VNC
        warning_ports = {21, 25, 110, 143}  # FTP, SMTP, POP3, IMAP
        
        if any(port in critical_ports for port in open_ports):
            return SecurityLevel.CRITICAL
        
        if any(port in warning_ports for port in open_ports) or len(open_ports) > 10:
            return SecurityLevel.WARNING
        
        return SecurityLevel.SECURE
