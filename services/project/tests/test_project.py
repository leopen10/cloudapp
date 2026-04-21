import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, projects_db

client = TestClient(app)

def setup_function():
    """Vide la base avant chaque test."""
    projects_db.clear()

def test_health_check():
    """Le service doit répondre OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "project"

def test_create_project():
    """On doit pouvoir créer un projet."""
    response = client.post("/projects", json={
        "name": "Mon Projet DevOps",
        "description": "Projet CloudApp complet",
        "owner_id": "user_1"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Mon Projet DevOps"
    assert response.json()["status"] == "active"
    assert response.json()["message"] == "Projet créé avec succès"

def test_list_projects():
    """La liste des projets doit fonctionner."""
    client.post("/projects", json={
        "name": "Projet 1",
        "description": "Description 1",
        "owner_id": "user_1"
    })
    client.post("/projects", json={
        "name": "Projet 2",
        "description": "Description 2",
        "owner_id": "user_2"
    })
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json()["total"] == 2

def test_get_project():
    """On doit pouvoir récupérer un projet par son ID."""
    create = client.post("/projects", json={
        "name": "Projet Test",
        "description": "Description test",
        "owner_id": "user_1"
    })
    project_id = create.json()["id"]
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id

def test_get_project_not_found():
    """Un projet inexistant doit retourner 404."""
    response = client.get("/projects/proj_inexistant")
    assert response.status_code == 404

def test_delete_project():
    """On doit pouvoir supprimer un projet."""
    create = client.post("/projects", json={
        "name": "Projet à supprimer",
        "description": "Description",
        "owner_id": "user_1"
    })
    project_id = create.json()["id"]
    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    # # # # assert "supprimé" in response.json()["message"]