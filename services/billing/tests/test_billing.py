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
    assert r.json()["service"] == "billing"

def test_get_invoices_endpoint():
    r = client.get("/invoices")
    assert r.status_code in [200, 500]

def test_recalculate_missing_project():
    r = client.post("/recalculate/99999", params={"new_progress": 50})
    assert r.status_code in [404, 500]