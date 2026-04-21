import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, notifications_db

client = TestClient(app)

def setup_function():
    """Vide la base avant chaque test."""
    notifications_db.clear()

def test_health_check():
    """Le service doit répondre OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "notification"

def test_send_notification():
    """On doit pouvoir envoyer une notification."""
    response = client.post("/send", json={
        "user_id": "user_1",
        "email": "leonel@test.com",
        "subject": "Bienvenue sur CloudApp",
        "message": "Votre projet a été créé avec succès"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "sent"
    assert response.json()["email"] == "leonel@test.com"

def test_list_notifications():
    """La liste des notifications doit fonctionner."""
    client.post("/send", json={
        "user_id": "user_1",
        "email": "user1@test.com",
        "subject": "Notif 1",
        "message": "Message 1"
    })
    client.post("/send", json={
        "user_id": "user_2",
        "email": "user2@test.com",
        "subject": "Notif 2",
        "message": "Message 2"
    })
    response = client.get("/notifications")
    assert response.status_code == 200
    assert response.json()["total"] == 2

def test_get_notification():
    """On doit pouvoir récupérer une notification par son ID."""
    create = client.post("/send", json={
        "user_id": "user_1",
        "email": "leonel@test.com",
        "subject": "Test",
        "message": "Test message"
    })
    notif_id = create.json()["id"]
    response = client.get(f"/notifications/{notif_id}")
    assert response.status_code == 200
    assert response.json()["id"] == notif_id

def test_get_notification_not_found():
    """Une notification inexistante doit retourner 404."""
    response = client.get("/notifications/notif_inexistant")
    assert response.status_code == 404

def test_get_sent_notifications():
    """La route /sent doit retourner les notifications envoyées."""
    client.post("/send", json={
        "user_id": "user_1",
        "email": "leonel@test.com",
        "subject": "Test sent",
        "message": "Message test"
    })
    response = client.get("/sent")
    assert response.status_code == 200
    assert response.json()["total"] == 1