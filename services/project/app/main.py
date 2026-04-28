from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import sys
sys.path.insert(0, '/app/shared')
from database import Project, Client, Notification, get_db, init_db
import uvicorn

app = FastAPI(title="CloudApp — Service Project", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
@app.on_event("startup")
def startup():
    init_db()

class ProjectCreate(BaseModel):
    client_id: int
    name: str
    description: Optional[str] = None
    budget: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ProjectUpdate(BaseModel):
    progress: Optional[int] = None
    status: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None

class ClientCreate(BaseModel):
    company_name: str
    email: str
    phone: Optional[str] = None

@app.get("/health")
async def health():
    return {"status": "ok", "service": "project", "version": "2.0.0"}

@app.get("/clients")
async def list_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return [{"id": c.id, "company_name": c.company_name, "email": c.email, "phone": c.phone} for c in clients]

@app.post("/clients")
async def create_client(req: ClientCreate, db: Session = Depends(get_db)):
    c = Client(company_name=req.company_name, email=req.email, phone=req.phone)
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "company_name": c.company_name, "email": c.email, "message": "Client créé"}

@app.get("/projects")
async def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    result = []
    for p in projects:
        client = db.query(Client).filter(Client.id == p.client_id).first()
        result.append({
            "id": p.id, "name": p.name, "description": p.description,
            "budget": float(p.budget), "progress": p.progress,
            "status": p.status, "client_id": p.client_id,
            "client_name": client.company_name if client else "",
            "start_date": str(p.start_date) if p.start_date else None,
            "end_date": str(p.end_date) if p.end_date else None
        })
    return result

@app.get("/projects/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    client = db.query(Client).filter(Client.id == p.client_id).first()
    return {
        "id": p.id, "name": p.name, "description": p.description,
        "budget": float(p.budget), "progress": p.progress,
        "status": p.status, "client_id": p.client_id,
        "client_name": client.company_name if client else "",
        "start_date": str(p.start_date) if p.start_date else None,
        "end_date": str(p.end_date) if p.end_date else None
    }

@app.post("/projects")
async def create_project(req: ProjectCreate, db: Session = Depends(get_db)):
    p = Project(
        client_id=req.client_id, name=req.name,
        description=req.description, budget=req.budget,
        start_date=req.start_date, end_date=req.end_date
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    notif = Notification(
        client_id=req.client_id,
        title=f"Nouveau projet — {req.name}",
        message=f"Le projet '{req.name}' a été créé. Budget : {req.budget}€.",
        type="project_update"
    )
    db.add(notif)
    db.commit()
    return {"id": p.id, "name": p.name, "budget": float(p.budget), "status": p.status, "message": "Projet créé"}

@app.put("/projects/{project_id}")
async def update_project(project_id: int, req: ProjectUpdate, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    old_progress = p.progress
    if req.progress is not None: p.progress = req.progress
    if req.status is not None: p.status = req.status
    if req.name is not None: p.name = req.name
    if req.description is not None: p.description = req.description
    db.commit()
    db.refresh(p)
    if req.progress is not None and req.progress != old_progress:
        notif = Notification(
            client_id=p.client_id,
            title=f"Projet mis à jour — {p.name}",
            message=f"L'avancement de votre projet est maintenant à {req.progress}%.",
            type="project_update"
        )
        db.add(notif)
        db.commit()
    return {"id": p.id, "progress": p.progress, "status": p.status, "message": "Projet mis à jour"}

@app.delete("/projects/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    db.delete(p)
    db.commit()
    return {"message": "Projet supprimé"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)