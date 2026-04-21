import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app

client = TestClient(app)

def test_health_check():
    """Le Gateway doit répondre OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "gateway"

def test_root():
    """La route principale doit fonctionner."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Bienvenue sur CloudApp Gateway"
    assert "services" in response.json()

def test_root_contains_all_services():
    """La route principale doit lister tous les services."""
    response = client.get("/")
    services = response.json()["services"]
    assert "auth" in services
    assert "project" in services
    assert "billing" in services
    assert "notification" in services
    assert "analytics" in services

def test_status_route_exists():
    """La route /status doit exister."""
    response = client.get("/status")
    assert response.status_code == 200
    assert "gateway" in response.json()
    assert "services" in response.json()

def test_workflow_route_exists():
    """La route /workflow doit exister."""
    response = client.post("/workflow", json={
        "email": "leonel@test.com",
        "password": "password123",
        "username": "leonel",
        "project_name": "Mon Projet DevOps",
        "project_description": "Projet CloudApp complet"
    })
    # Le workflow peut échouer car les services ne tournent pas en test
    # mais la route doit exister (pas de 404)
    assert response.status_code != 404

def test_workflow_returns_results():
    """Le workflow doit retourner un objet results."""
    response = client.post("/workflow", json={
        "email": "leonel@test.com",
        "password": "password123",
        "username": "leonel",
        "project_name": "Test Project",
        "project_description": "Test Description"
    })
    data = response.json()
    assert "results" in data or "message" in data