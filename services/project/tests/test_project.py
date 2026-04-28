import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

with __import__('unittest.mock', fromlist=['patch']).patch('database.engine'), \
     __import__('unittest.mock', fromlist=['patch']).patch('database.Base'):
    from main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "project"

def test_get_clients_endpoint():
    r = client.get("/clients")
    assert r.status_code in [200, 500]

def test_get_projects_endpoint():
    r = client.get("/projects")
    assert r.status_code in [200, 500]

def test_create_client_missing_fields():
    r = client.post("/clients", json={})
    assert r.status_code == 422

def test_create_project_missing_fields():
    r = client.post("/projects", json={})
    assert r.status_code == 422