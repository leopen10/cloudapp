import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ajoute le dossier app au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, users_db

client = TestClient(app)

def setup_function():
    """Vide la base avant chaque test."""
    users_db.clear()

def test_health_check():
    """Le service doit répondre OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "auth"

def test_register_success():
    """On doit pouvoir créer un compte."""
    response = client.post("/register", json={
        "email": "leonel@test.com",
        "password": "password123",
        "username": "leonel"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "leonel@test.com"
    assert response.json()["message"] == "Compte créé avec succès"

def test_register_duplicate_email():
    """On ne peut pas créer deux comptes avec le même email."""
    # Premier enregistrement
    client.post("/register", json={
        "email": "leonel@test.com",
        "password": "password123",
        "username": "leonel"
    })
    # Deuxième avec le même email
    response = client.post("/register", json={
        "email": "leonel@test.com",
        "password": "autrepassword",
        "username": "leonel2"
    })
    assert response.status_code == 400

def test_login_success():
    """On doit pouvoir se connecter après inscription."""
    # Inscription
    client.post("/register", json={
        "email": "leonel@test.com",
        "password": "password123",
        "username": "leonel"
    })
    # Connexion
    response = client.post("/login", json={
        "email": "leonel@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Connexion réussie"

def test_login_wrong_password():
    """Mauvais mot de passe = refus."""
    client.post("/register", json={
        "email": "leonel@test.com",
        "password": "password123",
        "username": "leonel"
    })
    response = client.post("/login", json={
        "email": "leonel@test.com",
        "password": "MAUVAIS"
    })
    assert response.status_code == 401

def test_list_users():
    """La liste des utilisateurs doit fonctionner."""
    client.post("/register", json={
        "email": "user1@test.com",
        "password": "pass",
        "username": "user1"
    })
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json()["total"] == 1