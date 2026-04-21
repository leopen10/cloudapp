from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

# ── Application FastAPI ────────────────────────────────────────────────────
app = FastAPI(
    title="CloudApp — Service Project",
    description="Service de gestion des projets",
    version="1.0.0"
)

# ── Base de données simulée ────────────────────────────────────────────────
projects_db: dict = {}

# ── Modèles de données ─────────────────────────────────────────────────────
class CreateProjectRequest(BaseModel):
    name: str
    description: str
    owner_id: str

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    owner_id: str
    status: str
    message: str

# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Vérifie que le service est opérationnel."""
    return {
        "status": "ok",
        "service": "project",
        "version": "1.0.0"
    }

@app.post("/projects", response_model=ProjectResponse)
async def create_project(request: CreateProjectRequest):
    """Crée un nouveau projet."""
    project_id = f"proj_{len(projects_db) + 1}"

    projects_db[project_id] = {
        "id": project_id,
        "name": request.name,
        "description": request.description,
        "owner_id": request.owner_id,
        "status": "active"
    }

    return ProjectResponse(
        id=project_id,
        name=request.name,
        description=request.description,
        owner_id=request.owner_id,
        status="active",
        message="Projet créé avec succès"
    )

@app.get("/projects")
async def list_projects():
    """Liste tous les projets."""
    return {
        "total": len(projects_db),
        "projects": list(projects_db.values())
    }

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Récupère un projet par son ID."""
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Projet {project_id} introuvable"
        )
    return project

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Supprime un projet."""
    if project_id not in projects_db:
        raise HTTPException(
            status_code=404,
            detail=f"Projet {project_id} introuvable"
        )
    del projects_db[project_id]
    return {"message": f"Projet {project_id} supprimé avec succès"}

# ── Point d'entrée ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)