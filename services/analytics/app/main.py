from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# ── Application FastAPI ────────────────────────────────────────────────────
app = FastAPI(
    title="CloudApp — Service Analytics",
    description="Service de suivi analytique",
    version="1.0.0"
)

# ── Base de données simulée ────────────────────────────────────────────────
events_db: dict = {}
stats_db: dict = {
    "total_projects": 0,
    "total_invoices": 0,
    "total_notifications": 0,
    "total_users": 0
}

# ── Modèles de données ─────────────────────────────────────────────────────
class TrackEventRequest(BaseModel):
    event_type: str
    user_id: str
    data: dict

class EventResponse(BaseModel):
    id: str
    event_type: str
    user_id: str
    data: dict
    status: str

# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Vérifie que le service est opérationnel."""
    return {
        "status": "ok",
        "service": "analytics",
        "version": "1.0.0"
    }

@app.post("/track", response_model=EventResponse)
async def track_event(request: TrackEventRequest):
    """Enregistre un événement analytique."""
    event_id = f"evt_{len(events_db) + 1}"

    events_db[event_id] = {
        "id": event_id,
        "event_type": request.event_type,
        "user_id": request.user_id,
        "data": request.data,
        "status": "tracked"
    }

    # Met à jour les statistiques
    if request.event_type == "project_created":
        stats_db["total_projects"] += 1
    elif request.event_type == "invoice_created":
        stats_db["total_invoices"] += 1
    elif request.event_type == "notification_sent":
        stats_db["total_notifications"] += 1
    elif request.event_type == "user_registered":
        stats_db["total_users"] += 1

    return EventResponse(
        id=event_id,
        event_type=request.event_type,
        user_id=request.user_id,
        data=request.data,
        status="tracked"
    )

@app.get("/events")
async def list_events():
    """Liste tous les événements enregistrés."""
    return {
        "total": len(events_db),
        "events": list(events_db.values())
    }

@app.get("/stats")
async def get_stats():
    """Retourne les statistiques globales."""
    return {
        "stats": stats_db,
        "total_events": len(events_db)
    }

@app.get("/events/{event_id}")
async def get_event(event_id: str):
    """Récupère un événement par son ID."""
    event = events_db.get(event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail=f"Événement {event_id} introuvable"
        )
    return event

# ── Point d'entrée ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)