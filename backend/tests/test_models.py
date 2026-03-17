"""
Tests for database models
"""
import pytest
from datetime import datetime
from backend.models.user import User
from backend.models.device import Device, SecurityLevel


def test_user_model_creation():
    """Test User model can be instantiated"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_superuser is False


def test_device_model_creation():
    """Test Device model can be instantiated"""
    device = Device(
        mac_address="00:11:22:33:44:55",
        ip_address="192.168.1.100",
        vendor="Test Vendor",
        device_type="laptop",
        status="online",
        security_level=SecurityLevel.SECURE
    )
    assert device.mac_address == "00:11:22:33:44:55"
    assert device.ip_address == "192.168.1.100"
    assert device.vendor == "Test Vendor"
    assert device.device_type == "laptop"
    assert device.status == "online"
    assert device.security_level == SecurityLevel.SECURE


def test_device_security_level_enum():
    """Test SecurityLevel enum values"""
    assert SecurityLevel.SECURE.value == "secure"
    assert SecurityLevel.WARNING.value == "warning"
    assert SecurityLevel.CRITICAL.value == "critical"
