import pytest
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Mock SQLAlchemy avant d'importer main
mock_db = MagicMock()
mock_session = MagicMock()

def get_mock_db():
    yield mock_session

with patch('database.engine'), patch('database.Base'):
    from main import app

client = TestClient(app)

def test_health_check():
    """Le service doit répondre OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "auth"

def test_health_version():
    """La version doit être présente."""
    response = client.get("/health")
    assert "version" in response.json()

def test_login_endpoint_exists():
    """L'endpoint login doit exister."""
    response = client.post("/login", json={
        "email": "test@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code in [200, 401, 422, 500]

def test_register_endpoint_exists():
    """L'endpoint register doit exister."""
    response = client.post("/register", json={
        "email": "new@test.com",
        "password": "password123",
        "username": "testuser",
        "role": "client"
    })
    assert response.status_code in [200, 400, 422, 500]

def test_users_endpoint_exists():
    """L'endpoint users doit exister."""
    response = client.get("/users")
    assert response.status_code in [200, 500]

def test_login_missing_fields():
    """Login sans email doit retourner 422."""
    response = client.post("/login", json={"password": "test"})
    assert response.status_code == 422

def test_register_missing_fields():
    """Register sans username doit retourner 422."""
    response = client.post("/register", json={
        "email": "test@test.com",
        "password": "test"
    })
    assert response.status_code == 422

def test_login_invalid_email_format():
    """Email invalide doit être rejeté."""
    response = client.post("/login", json={
        "email": "pasunemail",
        "password": "test123"
    })
    assert response.status_code in [401, 422]