from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn

# ── Application FastAPI ────────────────────────────────────────────────────
app = FastAPI(
    title="CloudApp — Service Gateway",
    description="Point d'entrée unique vers tous les microservices",
    version="1.0.0"
)

# ── URLs des services internes ─────────────────────────────────────────────
SERVICES = {
    "auth":         "http://auth:8001",
    "project":      "http://project:8002",
    "billing":      "http://billing:8003",
    "notification": "http://notification:8004",
    "analytics":    "http://analytics:8005",
}

# ── Modèles de données ─────────────────────────────────────────────────────
class WorkflowRequest(BaseModel):
    email: str
    password: str
    username: str
    project_name: str
    project_description: str

# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Route principale du Gateway."""
    return {
        "message": "Bienvenue sur CloudApp Gateway",
        "author": "Leonel-Magloire PENGOU",
        "version": "1.0.0",
        "services": list(SERVICES.keys())
    }

@app.get("/health")
async def health_check():
    """Vérifie que le Gateway est opérationnel."""
    return {
        "status": "ok",
        "service": "gateway",
        "version": "1.0.0"
    }

@app.get("/status")
async def services_status():
    """Vérifie l'état de tous les microservices."""
    results = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health")
                results[service_name] = {
                    "status": "ok" if response.status_code == 200 else "error",
                    "code": response.status_code
                }
            except Exception as e:
                results[service_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }
    return {
        "gateway": "ok",
        "services": results
    }

@app.post("/workflow")
async def create_project_workflow(request: WorkflowRequest):
    """
    Workflow complet de création de projet :
    1. Enregistre l'utilisateur (Auth)
    2. Crée le projet (Project)
    3. Crée une facture (Billing)
    4. Envoie une notification (Notification)
    5. Enregistre l'événement (Analytics)
    """
    results = {}

    async with httpx.AsyncClient(timeout=10.0) as client:

        # Étape 1 — Enregistrement utilisateur
        try:
            r1 = await client.post(f"{SERVICES['auth']}/register", json={
                "email": request.email,
                "password": request.password,
                "username": request.username
            })
            results["auth"] = r1.json()
            user_id = results["auth"].get("id", "user_unknown")
        except Exception as e:
            results["auth"] = {"error": str(e)}
            user_id = "user_unknown"

        # Étape 2 — Création du projet
        try:
            r2 = await client.post(f"{SERVICES['project']}/projects", json={
                "name": request.project_name,
                "description": request.project_description,
                "owner_id": user_id
            })
            results["project"] = r2.json()
            project_id = results["project"].get("id", "proj_unknown")
        except Exception as e:
            results["project"] = {"error": str(e)}
            project_id = "proj_unknown"

        # Étape 3 — Création facture
        try:
            r3 = await client.post(f"{SERVICES['billing']}/invoices", json={
                "project_id": project_id,
                "owner_id": user_id,
                "amount": 9.99,
                "description": f"Abonnement CloudApp — {request.project_name}"
            })
            results["billing"] = r3.json()
        except Exception as e:
            results["billing"] = {"error": str(e)}

        # Étape 4 — Notification
        try:
            r4 = await client.post(f"{SERVICES['notification']}/send", json={
                "user_id": user_id,
                "email": request.email,
                "subject": "Votre projet CloudApp est prêt !",
                "message": f"Bonjour {request.username}, votre projet '{request.project_name}' a été créé avec succès."
            })
            results["notification"] = r4.json()
        except Exception as e:
            results["notification"] = {"error": str(e)}

        # Étape 5 — Analytics
        try:
            r5 = await client.post(f"{SERVICES['analytics']}/track", json={
                "event_type": "project_created",
                "user_id": user_id,
                "data": {
                    "project_id": project_id,
                    "project_name": request.project_name
                }
            })
            results["analytics"] = r5.json()
        except Exception as e:
            results["analytics"] = {"error": str(e)}

    return {
        "message": "Workflow exécuté avec succès",
        "results": results
    }

# ── Point d'entrée ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)