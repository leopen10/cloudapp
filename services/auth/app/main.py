from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import uvicorn

# ── Application FastAPI ────────────────────────────────────────────────────
app = FastAPI(
    title="CloudApp — Service Auth",
    description="Service d'authentification et d'enregistrement des utilisateurs",
    version="1.0.0"
)

# ── Base de données simulée (dictionnaire en mémoire) ─────────────────────
# En production : remplacer par PostgreSQL
users_db: dict = {}

# ── Modèles de données ─────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    message: str

# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Vérifie que le service est opérationnel."""
    return {
        "status": "ok",
        "service": "auth",
        "version": "1.0.0"
    }

@app.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest):
    """Enregistre un nouvel utilisateur."""
    # Vérifie si l'email existe déjà
    if request.email in users_db:
        raise HTTPException(
            status_code=400,
            detail="Un compte avec cet email existe déjà"
        )

    # Crée l'utilisateur
    user_id = f"user_{len(users_db) + 1}"
    users_db[request.email] = {
        "id": user_id,
        "email": request.email,
        "username": request.username,
        "password": request.password  # En prod : hasher avec bcrypt
    }

    return UserResponse(
        id=user_id,
        email=request.email,
        username=request.username,
        message="Compte créé avec succès"
    )

@app.post("/login")
async def login(request: LoginRequest):
    """Authentifie un utilisateur."""
    # Vérifie si l'utilisateur existe
    user = users_db.get(request.email)

    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )

    return {
        "message": "Connexion réussie",
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }

@app.get("/users")
async def list_users():
    """Liste tous les utilisateurs (admin uniquement en prod)."""
    return {
        "total": len(users_db),
        "users": [
            {"id": u["id"], "email": u["email"], "username": u["username"]}
            for u in users_db.values()
        ]
    }

# ── Point d'entrée ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)