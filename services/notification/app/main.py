from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# ── Application FastAPI ────────────────────────────────────────────────────
app = FastAPI(
    title="CloudApp — Service Notification",
    description="Service d'envoi de notifications",
    version="1.0.0"
)

# ── Base de données simulée ────────────────────────────────────────────────
notifications_db: dict = {}

# ── Modèles de données ─────────────────────────────────────────────────────
class SendNotificationRequest(BaseModel):
    user_id: str
    email: str
    subject: str
    message: str

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    email: str
    subject: str
    message: str
    status: str

# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Vérifie que le service est opérationnel."""
    return {
        "status": "ok",
        "service": "notification",
        "version": "1.0.0"
    }

@app.post("/send", response_model=NotificationResponse)
async def send_notification(request: SendNotificationRequest):
    """Envoie une notification à un utilisateur."""
    notif_id = f"notif_{len(notifications_db) + 1}"

    notifications_db[notif_id] = {
        "id": notif_id,
        "user_id": request.user_id,
        "email": request.email,
        "subject": request.subject,
        "message": request.message,
        "status": "sent"
    }

    # Simulation d'envoi email (en prod : utiliser SendGrid, SES, etc.)
    print(f"[EMAIL] Envoi à {request.email} — Sujet: {request.subject}")

    return NotificationResponse(
        id=notif_id,
        user_id=request.user_id,
        email=request.email,
        subject=request.subject,
        message=request.message,
        status="sent"
    )

@app.get("/notifications")
async def list_notifications():
    """Liste toutes les notifications envoyées."""
    return {
        "total": len(notifications_db),
        "notifications": list(notifications_db.values())
    }

@app.get("/notifications/{notif_id}")
async def get_notification(notif_id: str):
    """Récupère une notification par son ID."""
    notif = notifications_db.get(notif_id)
    if not notif:
        raise HTTPException(
            status_code=404,
            detail=f"Notification {notif_id} introuvable"
        )
    return notif

@app.get("/sent")
async def get_sent_notifications():
    """Retourne toutes les notifications avec statut 'sent'."""
    sent = [n for n in notifications_db.values() if n["status"] == "sent"]
    return {
        "total": len(sent),
        "notifications": sent
    }

# ── Point d'entrée ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)