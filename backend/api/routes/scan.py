from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.services.scan_service import ScanService
from backend.api.routes.auth import get_current_user
from backend.models.user import User
from backend.models.network import Network, ScanHistory
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
    # Verify user owns this network
    result = await db.execute(
        select(Network).where(
            Network.id == network_id,
            Network.user_id == current_user.id
        )
    )
    network = result.scalar_one_or_none()
    
    if not network:
        raise HTTPException(status_code=404, detail="Network not found")
    
    # Get scan history
    result = await db.execute(
        select(ScanHistory)
        .where(ScanHistory.network_id == network_id)
        .order_by(ScanHistory.started_at.desc())
        .limit(50)
    )
    scans = result.scalars().all()
    
    return {
        "history": [
            {
                "id": str(scan.id),
                "started_at": scan.started_at.isoformat(),
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
                "devices_found": scan.devices_found,
                "new_devices": scan.new_devices,
                "status": scan.status
            }
            for scan in scans
        ]
    }
