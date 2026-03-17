"""
Basic tests for NetScan API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "NetScan API — Advanced Network Intelligence Platform"
    assert data["version"] == "2.0.0"
    assert data["status"] == "running"


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_auth_register_missing_fields():
    """Test registration with missing fields"""
    response = client.post("/api/auth/register", json={})
    assert response.status_code == 422  # Validation error


def test_auth_register_invalid_email():
    """Test registration with invalid email"""
    response = client.post("/api/auth/register", json={
        "email": "not-an-email",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 422  # Validation error


def test_networks_list_unauthorized():
    """Test networks endpoint without auth token"""
    response = client.get("/api/networks")
    assert response.status_code == 403  # Forbidden


def test_devices_list_unauthorized():
    """Test devices endpoint without auth token"""
    response = client.get("/api/devices")
    assert response.status_code == 403  # Forbidden


def test_scan_interfaces_unauthorized():
    """Test scan interfaces endpoint without auth token"""
    response = client.get("/api/scan/interfaces")
    assert response.status_code == 403  # Forbidden


def test_security_scan_unauthorized():
    """Test security scan endpoint without auth token"""
    response = client.post("/api/security/scan/test-device-id")
    assert response.status_code == 403  # Forbidden
