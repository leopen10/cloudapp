"""Tests unitaires du Gateway.

Ils ne dependent d'aucun autre service : les appels vers auth, project, etc.
ne sont jamais declenches. On verifie le contrat expose par le Gateway :
routes de base, registre des services, routes declarees et metriques.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, SERVICES  # noqa: E402

client = TestClient(app)

EXPECTED_SERVICES = ("auth", "project", "billing", "notification", "analytics")


def test_health_check():
    """Le Gateway doit repondre OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "gateway"


def test_root():
    """La route principale renvoie le message de bienvenue et la version."""
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Bienvenue sur CloudApp Gateway"
    assert body["version"] == "2.0.0"


def test_registry_lists_all_services():
    """Le registre interne doit connaitre tous les microservices."""
    for name in EXPECTED_SERVICES:
        assert name in SERVICES
        assert SERVICES[name].startswith("http://")


def test_status_reports_every_service():
    """/status doit rapporter un etat pour chaque service, meme injoignable."""
    response = client.get("/status")
    assert response.status_code == 200
    body = response.json()
    assert body["gateway"] == "ok"
    assert set(body["services"]) == set(SERVICES)


@pytest.mark.parametrize("path, method", [
    ("/auth/login", "post"),
    ("/auth/register", "post"),
    ("/clients", "get"),
    ("/projects", "get"),
    ("/invoices", "get"),
    ("/notifications", "get"),
    ("/analytics/stats", "get"),
])
def test_route_is_declared(path, method):
    """Chaque route publique du Gateway doit apparaitre dans le contrat OpenAPI."""
    paths = client.get("/openapi.json").json()["paths"]
    assert path in paths
    assert method in paths[path]


def test_metrics_endpoint_is_exposed():
    """Prometheus doit pouvoir lire /metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "# HELP" in response.text
