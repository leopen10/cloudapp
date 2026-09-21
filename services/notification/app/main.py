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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()

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