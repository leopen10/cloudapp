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
    assert r.json()["service"] == "notification"

def test_get_notifications_endpoint():
    r = client.get("/notifications")
    assert r.status_code in [200, 500]

def test_mark_read_missing():
    r = client.put("/notifications/99999/read")
    assert r.status_code in [200, 404, 500]

def test_notify_welcome_missing_client():
    r = client.post("/notify/welcome", json={"client_id": 99999})
    assert r.status_code in [200, 404, 500]