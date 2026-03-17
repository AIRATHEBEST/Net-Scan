from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.services.security_service import SecurityService
from backend.api.routes.auth import get_current_user
from backend.models.user import User
from backend.models.device import Device, Vulnerability
import uuid

router = APIRouter()
security_service = SecurityService()

@router.post("/scan/{device_id}")
async def scan_device_vulnerabilities(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Scan device for vulnerabilities"""
    try:
        vulnerabilities = await security_service.scan_vulnerabilities(
            db,
            str(device_id)
        )
        return {"vulnerabilities": vulnerabilities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vulnerabilities/{device_id}")
async def get_device_vulnerabilities(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get known vulnerabilities for device"""
    # Verify user owns this device
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get vulnerabilities from database
    result = await db.execute(
        select(Vulnerability).where(
            Vulnerability.device_id == device_id,
            Vulnerability.resolved == False
        )
    )
    vulnerabilities = result.scalars().all()
    
    return {
        "vulnerabilities": [
            {
                "id": str(vuln.id),
                "cve_id": vuln.cve_id,
                "severity": vuln.severity,
                "title": vuln.title,
                "description": vuln.description,
                "recommendation": vuln.recommendation,
                "cvss_score": vuln.cvss_score,
                "discovered_at": vuln.discovered_at.isoformat()
            }
            for vuln in vulnerabilities
        ]
    }
