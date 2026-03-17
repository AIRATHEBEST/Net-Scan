from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON, Enum, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from backend.core.database import Base

class DeviceType(str, enum.Enum):
    SMARTPHONE = "smartphone"
    LAPTOP = "laptop"
    TABLET = "tablet"
    TV = "tv"
    CAMERA = "camera"
    ROUTER = "router"
    IOT = "iot"
    DESKTOP = "desktop"
    PRINTER = "printer"
    UNKNOWN = "unknown"

class SecurityLevel(str, enum.Enum):
    SECURE = "secure"
    WARNING = "warning"
    CRITICAL = "critical"

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    network_id = Column(UUID(as_uuid=True), ForeignKey("networks.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Device identifiers
    mac_address = Column(String(17), nullable=False, index=True)
    ip_address = Column(String(15), nullable=False)
    hostname = Column(String(255))
    
    # Device information
    name = Column(String(255))
    vendor = Column(String(255))
    device_type = Column(Enum(DeviceType), default=DeviceType.UNKNOWN)
    os = Column(String(100))
    os_version = Column(String(50))
    
    # Network information
    open_ports = Column(ARRAY(Integer), default=[])
    services = Column(JSON, default={})
    
    # Status
    status = Column(String(20), default="online")
    is_new = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.SECURE)
    
    # Fingerprinting
    dhcp_fingerprint = Column(String(255))
    user_agent = Column(String(500))
    mdns_services = Column(JSON, default={})
    
    # Timestamps
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    network = relationship("Network", back_populates="devices")
    user = relationship("User", back_populates="devices")
    history = relationship("DeviceHistory", back_populates="device", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="device", cascade="all, delete-orphan")
    traffic_logs = relationship("TrafficLog", back_populates="device", cascade="all, delete-orphan")

class DeviceHistory(Base):
    __tablename__ = "device_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(20))
    ip_address = Column(String(15))
    open_ports = Column(ARRAY(Integer))
    bandwidth_usage = Column(Float, default=0.0)
    
    device = relationship("Device", back_populates="history")

class TrafficLog(Base):
    __tablename__ = "traffic_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    protocol = Column(String(20))
    src_port = Column(Integer)
    dst_port = Column(Integer)
    bytes_sent = Column(Float, default=0.0)
    bytes_received = Column(Float, default=0.0)
    application = Column(String(100))
    
    device = relationship("Device", back_populates="traffic_logs")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    
    cve_id = Column(String(20), index=True)
    severity = Column(String(20))
    title = Column(String(500))
    description = Column(String(2000))
    recommendation = Column(String(1000))
    cvss_score = Column(Float)
    
    discovered_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    
    device = relationship("Device", back_populates="vulnerabilities")
