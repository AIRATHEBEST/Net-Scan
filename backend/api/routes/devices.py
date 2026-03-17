from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.models.device import Device
from backend.models.user import User
from backend.api.routes.auth import get_current_user
import uuid

router = APIRouter()

@router.get("/")
async def get_devices(
    network_id: uuid.UUID = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all devices for user"""
    query = select(Device).where(Device.user_id == current_user.id)
    
    if network_id:
        query = query.where(Device.network_id == network_id)
    
    result = await db.execute(query)
    devices = result.scalars().all()
    
    return {"devices": [
        {
            "id": str(d.id),
            "name": d.name or d.hostname or "Unknown Device",
            "ip": d.ip_address,
            "mac": d.mac_address,
            "vendor": d.vendor,
            "type": d.device_type,
            "status": d.status,
            "openPorts": d.open_ports,
            "services": d.services,
            "securityLevel": d.security_level,
            "lastSeen": d.last_seen.isoformat(),
            "isNew": d.is_new
        }
        for d in devices
    ]}

@router.get("/{device_id}")
async def get_device(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get device details"""
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {
        "id": str(device.id),
        "name": device.name,
        "ip": device.ip_address,
        "mac": device.mac_address,
        "vendor": device.vendor,
        "type": device.device_type,
        "os": device.os,
        "status": device.status,
        "openPorts": device.open_ports,
        "services": device.services,
        "securityLevel": device.security_level,
        "firstSeen": device.first_seen.isoformat(),
        "lastSeen": device.last_seen.isoformat()
    }

@router.patch("/{device_id}")
async def update_device(
    device_id: uuid.UUID,
    name: str = None,
    is_blocked: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update device settings"""
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if name is not None:
        device.name = name
    if is_blocked is not None:
        device.is_blocked = is_blocked
    
    await db.commit()
    return {"message": "Device updated"}
