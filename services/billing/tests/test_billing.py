import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, invoices_db

client = TestClient(app)

def setup_function():
    """Vide la base avant chaque test."""
    invoices_db.clear()

def test_health_check():
    """Le service doit répondre OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "billing"

def test_create_invoice():
    """On doit pouvoir créer une facture."""
    response = client.post("/invoices", json={
        "project_id": "proj_1",
        "owner_id": "user_1",
        "amount": 99.99,
        "description": "Abonnement mensuel CloudApp"
    })
    assert response.status_code == 200
    assert response.json()["amount"] == 99.99
    assert response.json()["status"] == "pending"
    assert response.json()["message"] == "Facture créée avec succès"

def test_list_invoices():
    """La liste des factures doit fonctionner."""
    client.post("/invoices", json={
        "project_id": "proj_1",
        "owner_id": "user_1",
        "amount": 50.0,
        "description": "Facture 1"
    })
    client.post("/invoices", json={
        "project_id": "proj_2",
        "owner_id": "user_2",
        "amount": 75.0,
        "description": "Facture 2"
    })
    response = client.get("/invoices")
    assert response.status_code == 200
    assert response.json()["total"] == 2

def test_get_invoice():
    """On doit pouvoir récupérer une facture par son ID."""
    create = client.post("/invoices", json={
        "project_id": "proj_1",
        "owner_id": "user_1",
        "amount": 99.99,
        "description": "Test facture"
    })
    invoice_id = create.json()["id"]
    response = client.get(f"/invoices/{invoice_id}")
    assert response.status_code == 200
    assert response.json()["id"] == invoice_id

def test_get_invoice_not_found():
    """Une facture inexistante doit retourner 404."""
    response = client.get("/invoices/inv_inexistant")
    assert response.status_code == 404

def test_pay_invoice():
    """On doit pouvoir marquer une facture comme payée."""
    create = client.post("/invoices", json={
        "project_id": "proj_1",
        "owner_id": "user_1",
        "amount": 99.99,
        "description": "Facture à payer"
    })
    invoice_id = create.json()["id"]
    response = client.put(f"/invoices/{invoice_id}/pay")
    assert response.status_code == 200
    assert response.json()["invoice"]["status"] == "paid"