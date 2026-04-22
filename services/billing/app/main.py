from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/app/shared')
from database import Invoice, Project, Notification, get_db, init_db
import uvicorn

app = FastAPI(title="CloudApp — Service Billing", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "billing", "version": "2.0.0"}

@app.get("/invoices")
async def list_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    return [{"id": i.id, "project_id": i.project_id, "client_id": i.client_id,
             "amount": float(i.amount), "percentage_billed": i.percentage_billed,
             "status": i.status, "due_date": str(i.due_date) if i.due_date else None,
             "description": i.description, "created_at": str(i.created_at)} for i in invoices]

@app.get("/invoices/project/{project_id}")
async def invoices_by_project(project_id: int, db: Session = Depends(get_db)):
    invoices = db.query(Invoice).filter(Invoice.project_id == project_id).all()
    return [{"id": i.id, "amount": float(i.amount), "percentage_billed": i.percentage_billed,
             "status": i.status, "due_date": str(i.due_date) if i.due_date else None} for i in invoices]

@app.post("/recalculate/{project_id}")
async def recalculate(project_id: int, new_progress: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    paliers = [25, 50, 75, 100]
    existing = [i.percentage_billed for i in db.query(Invoice).filter(Invoice.project_id == project_id).all()]
    new_invoices = []
    for palier in paliers:
        if new_progress >= palier and palier not in existing:
            amount = round(float(project.budget) * 0.25, 2)
            invoice = Invoice(
                project_id=project_id, client_id=project.client_id,
                amount=amount, percentage_billed=palier, status="pending",
                due_date=(datetime.now() + timedelta(days=30)).date(),
                description=f"Facturation automatique — {palier}% du projet '{project.name}'"
            )
            db.add(invoice)
            db.commit()
            db.refresh(invoice)
            new_invoices.append({"id": invoice.id, "amount": amount, "percentage_billed": palier})
            notif = Notification(
                client_id=project.client_id,
                title=f"Nouvelle facture — {project.name}",
                message=f"Une facture de {amount}€ a été générée pour l'atteinte de {palier}%.",
                type="invoice"
            )
            db.add(notif)
            db.commit()
    return {"new_invoices": len(new_invoices), "invoices": new_invoices}

@app.post("/invoices/{invoice_id}/pay")
async def pay_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    if inv.status == "paid":
        raise HTTPException(status_code=400, detail="Déjà payée")
    inv.status = "paid"
    inv.paid_at = datetime.now()
    db.commit()
    return {"message": "Paiement enregistré", "invoice_id": invoice_id, "amount": float(inv.amount)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)