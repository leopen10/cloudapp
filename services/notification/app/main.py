from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import sys
sys.path.insert(0, '/app/shared')
from database import Notification, Client, get_db, init_db
import uvicorn

app = FastAPI(title="CloudApp — Service Notification", version="2.0.0")
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
from telemetry import setup_tracing
setup_tracing(app, "notification", instrument_db=True)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()

import os

import resend
from starlette.concurrency import run_in_threadpool

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "CloudApp <onboarding@resend.dev>")
resend.api_key = RESEND_API_KEY


async def send_email(to, subject, html):
    """Envoie un e-mail via Resend. Ne leve jamais d'exception : une notification
    reste enregistree en base meme si l'envoi echoue ou si aucune cle n'est configuree."""
    if not RESEND_API_KEY:
        print(f"[notification] RESEND_API_KEY absente : e-mail non envoye a {to}", flush=True)
        return False
    if not to:
        return False
    try:
        await run_in_threadpool(
            resend.Emails.send,
            {"from": FROM_EMAIL, "to": [to], "subject": subject, "html": html},
        )
        print(f"[notification] e-mail envoye a {to} : {subject}", flush=True)
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[notification] echec d'envoi a {to} : {type(exc).__name__}: {exc}", flush=True)
        return False


def _resolve_client(db, client_id):
    """Verifie que client_id existe avant d'ecrire une Notification (cle etrangere) :
    un identifiant absent ou inconnu ne doit jamais faire echouer la requete, la
    notification est alors enregistree sans client associe (et sans e-mail)."""
    if not client_id:
        return None, None
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c:
        print(f"[notification] client_id={client_id} introuvable : notification enregistree sans client", flush=True)
        return None, None
    return client_id, c.email


class WelcomeNotify(BaseModel):
    client_id: int


class ProjectCreatedNotify(BaseModel):
    client_id: Optional[int] = None
    project_id: int
    project_name: str
    budget: float = 0


class ProgressNotify(BaseModel):
    client_id: Optional[int] = None
    project_id: int
    project_name: str
    progress: int


class InvoiceNotify(BaseModel):
    client_id: Optional[int] = None
    project_id: int
    project_name: str
    amount: float
    percentage: int


@app.post("/notify/welcome")
async def notify_welcome(req: WelcomeNotify, db: Session = Depends(get_db)):
    title = "Bienvenue chez CloudApp"
    message = "Votre compte client a ete cree."
    client_id, email = _resolve_client(db, req.client_id)
    n = Notification(client_id=client_id, title=title, message=message, type="info")
    db.add(n)
    db.commit()
    await send_email(email, title, f"<p>{message}</p>")
    return {"status": "ok", "id": n.id}


@app.post("/notify/project-created")
async def notify_project_created(req: ProjectCreatedNotify, db: Session = Depends(get_db)):
    title = f"Nouveau projet \u2014 {req.project_name}"
    message = f"Le projet '{req.project_name}' a ete cree. Budget : {req.budget:.2f} EUR."
    client_id, email = _resolve_client(db, req.client_id)
    n = Notification(client_id=client_id, title=title, message=message, type="project_update")
    db.add(n)
    db.commit()
    await send_email(email, title, f"<p>{message}</p>")
    return {"status": "ok", "id": n.id}


@app.post("/notify/progress")
async def notify_progress(req: ProgressNotify, db: Session = Depends(get_db)):
    title = f"Projet mis a jour \u2014 {req.project_name}"
    message = f"L'avancement de votre projet est maintenant a {req.progress}%."
    client_id, email = _resolve_client(db, req.client_id)
    n = Notification(client_id=client_id, title=title, message=message, type="project_update")
    db.add(n)
    db.commit()
    await send_email(email, title, f"<p>{message}</p>")
    return {"status": "ok", "id": n.id}


@app.post("/notify/invoice")
async def notify_invoice(req: InvoiceNotify, db: Session = Depends(get_db)):
    title = f"Nouvelle facture \u2014 {req.project_name}"
    message = f"Une facture de {req.amount:.2f} EUR a ete generee pour l'atteinte de {req.percentage}%."
    client_id, email = _resolve_client(db, req.client_id)
    n = Notification(client_id=client_id, title=title, message=message, type="invoice")
    db.add(n)
    db.commit()
    await send_email(email, title, f"<p>{message}</p>")
    return {"status": "ok", "id": n.id}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "notification", "version": "2.0.0"}

@app.get("/notifications")
async def list_notifications(db: Session = Depends(get_db)):
    notifs = db.query(Notification).order_by(Notification.created_at.desc()).limit(20).all()
    return [{"id": n.id, "client_id": n.client_id, "title": n.title,
             "message": n.message, "type": n.type, "read": n.read,
             "created_at": str(n.created_at)} for n in notifs]

@app.put("/notifications/{notif_id}/read")
async def mark_read(notif_id: int, db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == notif_id).first()
    if n:
        n.read = True
        db.commit()
    return {"message": "Lu"}

@app.put("/notifications/read-all")
async def mark_all_read(db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.read == False).update({"read": True})
    db.commit()
    return {"message": "Toutes lues"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
