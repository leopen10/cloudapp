"""Tests unitaires du service Analytics.

Le service lit et ecrit dans PostgreSQL : ces tests utilisent la base du
poste (en CI, un conteneur PostgreSQL jetable). Les tables sont creees au
demarrage de l'application (evenement startup -> init_db()).
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    # Le bloc "with" declenche l'evenement startup (creation des tables).
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    """Le service doit repondre OK."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "analytics"
    assert body["version"] == "2.0.0"


def test_track_event(client):
    """Un evenement complet est enregistre et recoit un identifiant."""
    response = client.post("/track", json={
        "event_type": "project_created",
        "client_id": 1,
        "project_id": 42,
        "data": "name=Mon Projet",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "tracked"
    assert body["event_type"] == "project_created"
    assert isinstance(body["id"], int)


def test_track_event_with_only_event_type(client):
    """Seul event_type est obligatoire."""
    response = client.post("/track", json={"event_type": "ping"})
    assert response.status_code == 200
    assert response.json()["status"] == "tracked"


def test_track_event_requires_event_type(client):
    """Sans event_type, la requete est rejetee."""
    response = client.post("/track", json={"project_id": 1})
    assert response.status_code == 422


def test_track_event_rejects_invalid_project_id(client):
    """project_id doit etre un entier."""
    response = client.post("/track", json={
        "event_type": "project_updated",
        "project_id": "pas-un-nombre",
    })
    assert response.status_code == 422


def test_stats_structure(client):
    """/stats expose les cinq compteurs attendus, avec des types coherents."""
    response = client.get("/stats")
    assert response.status_code == 200
    stats = response.json()
    for key in ("total_projects", "active_projects", "total_invoiced",
                "paid_invoiced", "pending_invoiced"):
        assert key in stats
    assert isinstance(stats["total_projects"], int)
    assert isinstance(stats["active_projects"], int)
    assert stats["active_projects"] <= stats["total_projects"]


def test_stats_amounts_are_consistent(client):
    """Le montant en attente vaut le total facture moins le total paye."""
    stats = client.get("/stats").json()
    assert stats["pending_invoiced"] == pytest.approx(
        stats["total_invoiced"] - stats["paid_invoiced"]
    )
    assert stats["paid_invoiced"] <= stats["total_invoiced"]


def test_metrics_endpoint_is_exposed(client):
    """Prometheus doit pouvoir lire /metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "# HELP" in response.text
