from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.services.device_intelligence import DeviceIntelligenceEngine
from backend.services.presence_detection import PresenceDetectionSystem
from backend.services.smart_alerts import SmartAlertsEngine
from backend.services.internet_monitoring import InternetMonitoringService
from backend.services.real_dpi import RealDPIEngine
from backend.services.ai_insights import AIInsightsEngine
from backend.services.router_integration import RouterIntegrationService
from backend.services.behavioral_analysis import BehavioralAnalysisEngine
from backend.services.cloud_intelligence import CloudIntelligenceNetwork
from backend.services.plugin_system import PluginSystem
from backend.models.device import Device
from backend.models.user import User, Alert
from backend.api.routes.auth import get_current_user
import uuid

router = APIRouter()

# Initialize all services
intelligence_engine = DeviceIntelligenceEngine()
presence_system = PresenceDetectionSystem()
alerts_engine = SmartAlertsEngine()
internet_monitor = InternetMonitoringService()
dpi_engine = RealDPIEngine()
ai_insights = AIInsightsEngine()
router_integration = RouterIntegrationService()
behavioral_analysis = BehavioralAnalysisEngine()
cloud_intelligence = CloudIntelligenceNetwork()
plugin_system = PluginSystem()

# ========== Tier 1: Device Intelligence ==========

@router.get("/device/{device_id}/details")
async def get_detailed_device_info(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed device identification"""
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    details = await intelligence_engine.identify_device_detailed(
        mac=device.mac_address,
        ip=device.ip_address,
        vendor=device.vendor,
        hostname=device.hostname,
        open_ports=device.open_ports,
        services=device.services,
        os_info={'name': device.os} if device.os else None,
        dhcp_fingerprint=device.dhcp_fingerprint,
        user_agent=device.user_agent,
        mdns_services=device.mdns_services
    )
    
    capabilities = await intelligence_engine.extract_device_capabilities({
        'device_type': device.device_type,
        'open_ports': device.open_ports,
        'services': device.services
    })
    
    return {
        'device_id': str(device.id),
        'identification': details,
        'capabilities': capabilities
    }

# ========== Tier 1: Presence Detection ==========

@router.get("/device/{device_id}/presence/history")
async def get_presence_history(
    device_id: uuid.UUID,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get device presence history"""
    history = await presence_system.get_device_presence_history(db, device_id, days)
    return {"history": history}

@router.get("/device/{device_id}/presence/patterns")
async def get_presence_patterns(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get device presence patterns"""
    patterns = await presence_system.analyze_presence_patterns(db, device_id)
    return patterns

# ========== Tier 1: Smart Alerts ==========

@router.post("/device/{device_id}/alerts/check")
async def check_device_alerts(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run all alert checks for a device"""
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    alerts = await alerts_engine.check_all_alerts(db, device)
    return {"alerts": alerts}

@router.get("/alerts")
async def get_user_alerts(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user alerts"""
    query = select(Alert).where(Alert.user_id == current_user.id)
    if unread_only:
        query = query.where(Alert.read == False)
    query = query.order_by(Alert.created_at.desc()).limit(50)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return {"alerts": [
        {
            "id": str(a.id),
            "title": a.title,
            "message": a.message,
            "severity": a.severity,
            "category": a.category,
            "read": a.read,
            "created_at": a.created_at.isoformat()
        }
        for a in alerts
    ]}

# ========== Tier 1: Internet Monitoring ==========

@router.post("/internet/speedtest")
async def run_speedtest(current_user: User = Depends(get_current_user)):
    """Run internet speed test"""
    result = await internet_monitor.run_speed_test()
    return result

@router.get("/internet/connectivity")
async def check_connectivity(current_user: User = Depends(get_current_user)):
    """Check internet connectivity"""
    result = await internet_monitor.check_internet_connectivity()
    return result

@router.get("/internet/isp")
async def get_isp_info(current_user: User = Depends(get_current_user)):
    """Get ISP information"""
    result = await internet_monitor.detect_isp()
    return result

# ========== Tier 1: Real DPI ==========

@router.post("/dpi/start")
async def start_dpi_capture(
    interface: str = None,
    duration: int = 60,
    current_user: User = Depends(get_current_user)
):
    """Start DPI packet capture"""
    await dpi_engine.start_capture(interface, duration)
    return {"status": "capturing", "duration": duration}

@router.get("/dpi/device/{ip_address}/applications")
async def get_device_applications(
    ip_address: str,
    current_user: User = Depends(get_current_user)
):
    """Get applications used by device"""
    result = dpi_engine.get_device_applications(ip_address)
    return result

@router.get("/dpi/device/{ip_address}/dns")
async def get_dns_history(
    ip_address: str,
    current_user: User = Depends(get_current_user)
):
    """Get DNS query history"""
    result = dpi_engine.get_dns_history(ip_address)
    return {"dns_history": result}

@router.get("/dpi/summary")
async def get_dpi_summary(current_user: User = Depends(get_current_user)):
    """Get network-wide DPI summary"""
    result = dpi_engine.get_network_summary()
    return result

# ========== Tier 2: AI Insights ==========

@router.get("/network/{network_id}/insights")
async def get_network_insights(
    network_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered network insights"""
    insights = await ai_insights.analyze_network_health(db, network_id)
    return insights

@router.get("/device/{device_id}/insights")
async def get_device_insights(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI insights for device"""
    insights = await ai_insights.get_device_insights(db, device_id)
    return insights

# ========== Tier 2: Router Integration ==========

@router.post("/router/discover")
async def discover_router(current_user: User = Depends(get_current_user)):
    """Discover router via UPnP"""
    result = await router_integration.discover_router()
    return result

@router.post("/router/block")
async def block_device(
    mac_address: str,
    reason: str = "Security",
    current_user: User = Depends(get_current_user)
):
    """Block device from network"""
    result = await router_integration.block_device(mac_address, reason)
    return result

@router.post("/router/qos")
async def set_qos(
    mac_address: str,
    priority: str,
    current_user: User = Depends(get_current_user)
):
    """Set QoS priority"""
    result = await router_integration.set_qos_priority(mac_address, priority)
    return result

@router.get("/router/status")
async def get_router_status(current_user: User = Depends(get_current_user)):
    """Get router status"""
    result = await router_integration.get_router_status()
    return result

# ========== Tier 3: Behavioral Analysis ==========

@router.post("/device/{device_id}/behavior/analyze")
async def analyze_behavior(
    device_id: uuid.UUID,
    time_window_hours: int = 24,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze device behavior for threats"""
    result = await behavioral_analysis.analyze_device_behavior(
        db, device_id, time_window_hours
    )
    return result

# ========== Tier 3: Cloud Intelligence ==========

@router.post("/cloud/submit-fingerprint")
async def submit_fingerprint(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit device fingerprint to cloud"""
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device_data = {
        'vendor': device.vendor,
        'device_type': device.device_type,
        'mac_address': device.mac_address,
        'open_ports': device.open_ports
    }
    
    result = await cloud_intelligence.submit_device_fingerprint(
        device_data, str(current_user.id)
    )
    return result

@router.get("/cloud/threats")
async def get_global_threats(current_user: User = Depends(get_current_user)):
    """Get global threat intelligence"""
    threats = await cloud_intelligence.get_global_threats()
    return {"threats": threats}

# ========== Tier 3: Plugin System ==========

@router.post("/plugins/load/{plugin_name}")
async def load_plugin(
    plugin_name: str,
    current_user: User = Depends(get_current_user)
):
    """Load a plugin"""
    result = await plugin_system.load_plugin(plugin_name)
    return result

@router.get("/plugins")
async def list_plugins(current_user: User = Depends(get_current_user)):
    """List all plugins"""
    plugins = await plugin_system.list_plugins()
    return {"plugins": plugins}

@router.post("/plugins/{plugin_name}/enable")
async def enable_plugin(
    plugin_name: str,
    current_user: User = Depends(get_current_user)
):
    """Enable a plugin"""
    success = await plugin_system.enable_plugin(plugin_name)
    return {"success": success}

@router.post("/plugins/{plugin_name}/disable")
async def disable_plugin(
    plugin_name: str,
    current_user: User = Depends(get_current_user)
):
    """Disable a plugin"""
    success = await plugin_system.disable_plugin(plugin_name)
    return {"success": success}
