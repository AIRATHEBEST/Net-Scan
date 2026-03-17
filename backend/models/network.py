from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.core.database import Base

class Network(Base):
    __tablename__ = "networks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    subnet = Column(String(18), nullable=False)
    gateway = Column(String(15))
    interface = Column(String(50))
    
    is_active = Column(Boolean, default=True)
    auto_scan = Column(Boolean, default=False)
    scan_interval = Column(Integer, default=300)  # seconds
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="networks")
    devices = relationship("Device", back_populates="network", cascade="all, delete-orphan")
    scans = relationship("ScanHistory", back_populates="network", cascade="all, delete-orphan")

class ScanHistory(Base):
    __tablename__ = "scan_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    network_id = Column(UUID(as_uuid=True), ForeignKey("networks.id"), nullable=False)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    devices_found = Column(Integer, default=0)
    new_devices = Column(Integer, default=0)
    status = Column(String(20), default="running")
    
    network = relationship("Network", back_populates="scans")
