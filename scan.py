from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.services.scan_service import ScanService
from backend.api.routes.auth import get_current_user
from backend.models.user import User
import uuid

router = APIRouter()
scan_service = ScanService()

@router.post("/network/{network_id}")
async def start_network_scan(
    network_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a full network scan"""
    try:
        result = await scan_service.perform_full_scan(
            db,
            network_id,
            current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/interfaces")
async def get_network_interfaces(
    current_user: User = Depends(get_current_user)
):
    """Get available network interfaces"""
    interfaces = scan_service.network_scanner.get_network_interfaces()
    return {"interfaces": interfaces}

@router.get("/history/{network_id}")
async def get_scan_history(
    network_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scan history for a network"""
    # TODO: Implement scan history retrieval
    return {"history": []}
