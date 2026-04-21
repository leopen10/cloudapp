import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, events_db, stats_db

client = TestClient(app)

def setup_function():
    """Vide la base avant chaque test."""
    events_db.clear()
    stats_db["total_projects"] = 0
    stats_db["total_invoices"] = 0
    stats_db["total_notifications"] = 0
    stats_db["total_users"] = 0

def test_health_check():
    """Le service doit répondre OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "analytics"

def test_track_event():
    """On doit pouvoir enregistrer un événement."""
    response = client.post("/track", json={
        "event_type": "project_created",
        "user_id": "user_1",
        "data": {"project_id": "proj_1", "name": "Mon Projet"}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "tracked"
    assert response.json()["event_type"] == "project_created"

def test_stats_updated_after_event():
    """Les stats doivent être mises à jour après un événement."""
    client.post("/track", json={
        "event_type": "project_created",
        "user_id": "user_1",
        "data": {"project_id": "proj_1"}
    })
    response = client.get("/stats")
    assert response.status_code == 200
    assert response.json()["stats"]["total_projects"] == 1

def test_list_events():
    """La liste des événements doit fonctionner."""
    client.post("/track", json={
        "event_type": "user_registered",
        "user_id": "user_1",
        "data": {"email": "user1@test.com"}
    })
    client.post("/track", json={
        "event_type": "invoice_created",
        "user_id": "user_1",
        "data": {"invoice_id": "inv_1"}
    })
    response = client.get("/events")
    assert response.status_code == 200
    assert response.json()["total"] == 2

def test_get_event():
    """On doit pouvoir récupérer un événement par son ID."""
    create = client.post("/track", json={
        "event_type": "notification_sent",
        "user_id": "user_1",
        "data": {"notif_id": "notif_1"}
    })
    event_id = create.json()["id"]
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["id"] == event_id

def test_get_event_not_found():
    """Un événement inexistant doit retourner 404."""
    response = client.get("/events/evt_inexistant")
    assert response.status_code == 404