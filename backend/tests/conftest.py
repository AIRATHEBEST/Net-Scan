"""
Pytest configuration and fixtures
"""
import pytest
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv()


@pytest.fixture
def test_env():
    """Provide test environment variables"""
    return {
        "DATABASE_URL": os.getenv("DATABASE_URL", "postgresql://test:test@localhost/test_netscan"),
        "SECRET_KEY": "test-secret-key",
        "ALGORITHM": "HS256",
    }


@pytest.fixture
def mock_user():
    """Provide a mock user object"""
    from backend.models.user import User
    import uuid
    
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )


@pytest.fixture
def mock_device():
    """Provide a mock device object"""
    from backend.models.device import Device, SecurityLevel
    import uuid
    
    return Device(
        id=uuid.uuid4(),
        mac_address="00:11:22:33:44:55",
        ip_address="192.168.1.100",
        vendor="Test Vendor",
        device_type="laptop",
        status="online",
        security_level=SecurityLevel.SECURE
    )
