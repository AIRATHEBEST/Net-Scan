from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.models.network import Network
from backend.models.user import User
from backend.api.routes.auth import get_current_user
from pydantic import BaseModel
import uuid

router = APIRouter()

class NetworkCreate(BaseModel):
    name: str
    subnet: str
    interface: str
    gateway: str = None

@router.get("/")
async def get_networks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all networks for user"""
    result = await db.execute(
        select(Network).where(Network.user_id == current_user.id)
    )
    networks = result.scalars().all()
    
    return {"networks": [
        {
            "id": str(n.id),
            "name": n.name,
            "subnet": n.subnet,
            "gateway": n.gateway,
            "interface": n.interface,
            "isActive": n.is_active,
            "autoScan": n.auto_scan
        }
        for n in networks
    ]}

@router.post("/")
async def create_network(
    network: NetworkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new network"""
    db_network = Network(
        user_id=current_user.id,
        name=network.name,
        subnet=network.subnet,
        interface=network.interface,
        gateway=network.gateway
    )
    db.add(db_network)
    await db.commit()
    
    return {"id": str(db_network.id), "message": "Network created"}

@router.patch("/{network_id}")
async def update_network(
    network_id: uuid.UUID,
    auto_scan: bool = None,
    scan_interval: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update network settings"""
    result = await db.execute(
        select(Network).where(
            Network.id == network_id,
            Network.user_id == current_user.id
        )
    )
    network = result.scalar_one_or_none()
    
    if not network:
        raise HTTPException(status_code=404, detail="Network not found")
    
    if auto_scan is not None:
        network.auto_scan = auto_scan
    if scan_interval is not None:
        network.scan_interval = scan_interval
    
    await db.commit()
    return {"message": "Network updated"}
