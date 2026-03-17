from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.services.security_service import SecurityService
from backend.api.routes.auth import get_current_user
from backend.models.user import User
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
    # TODO: Fetch from database
    return {"vulnerabilities": []}
