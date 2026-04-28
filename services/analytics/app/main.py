from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import sys
sys.path.insert(0, '/app/shared')
from database import AnalyticsEvent, Project, Invoice, get_db, init_db
import uvicorn

app = FastAPI(title="CloudApp — Service Analytics", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def startup():
    init_db()

class TrackEvent(BaseModel):
    event_type: str
    client_id: Optional[int] = None
    project_id: Optional[int] = None
    data: Optional[str] = None

@app.get("/health")
async def health():
    return {"status": "ok", "service": "analytics", "version": "2.0.0"}

@app.post("/track")
async def track(req: TrackEvent, db: Session = Depends(get_db)):
    event = AnalyticsEvent(
        event_type=req.event_type,
        client_id=req.client_id,
        project_id=req.project_id,
        data=req.data
    )
    db.add(event)
    db.commit()
    return {"id": event.id, "event_type": event.event_type, "status": "tracked"}

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == "active").count()
    total_invoiced = db.query(func.sum(Invoice.amount)).scalar() or 0
    paid_invoiced = db.query(func.sum(Invoice.amount)).filter(Invoice.status == "paid").scalar() or 0
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_invoiced": float(total_invoiced),
        "paid_invoiced": float(paid_invoiced),
        "pending_invoiced": float(total_invoiced) - float(paid_invoiced)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)