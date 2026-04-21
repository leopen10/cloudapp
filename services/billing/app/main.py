from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# ── Application FastAPI ────────────────────────────────────────────────────
app = FastAPI(
    title="CloudApp — Service Billing",
    description="Service de facturation",
    version="1.0.0"
)

# ── Base de données simulée ────────────────────────────────────────────────
invoices_db: dict = {}

# ── Modèles de données ─────────────────────────────────────────────────────
class CreateInvoiceRequest(BaseModel):
    project_id: str
    owner_id: str
    amount: float
    description: str

class InvoiceResponse(BaseModel):
    id: str
    project_id: str
    owner_id: str
    amount: float
    description: str
    status: str
    message: str

# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Vérifie que le service est opérationnel."""
    return {
        "status": "ok",
        "service": "billing",
        "version": "1.0.0"
    }

@app.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(request: CreateInvoiceRequest):
    """Crée une nouvelle facture."""
    invoice_id = f"inv_{len(invoices_db) + 1}"

    invoices_db[invoice_id] = {
        "id": invoice_id,
        "project_id": request.project_id,
        "owner_id": request.owner_id,
        "amount": request.amount,
        "description": request.description,
        "status": "pending"
    }

    return InvoiceResponse(
        id=invoice_id,
        project_id=request.project_id,
        owner_id=request.owner_id,
        amount=request.amount,
        description=request.description,
        status="pending",
        message="Facture créée avec succès"
    )

@app.get("/invoices")
async def list_invoices():
    """Liste toutes les factures."""
    return {
        "total": len(invoices_db),
        "invoices": list(invoices_db.values())
    }

@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Récupère une facture par son ID."""
    invoice = invoices_db.get(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Facture {invoice_id} introuvable"
        )
    return invoice

@app.put("/invoices/{invoice_id}/pay")
async def pay_invoice(invoice_id: str):
    """Marque une facture comme payée."""
    invoice = invoices_db.get(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Facture {invoice_id} introuvable"
        )
    invoices_db[invoice_id]["status"] = "paid"
    return {
        "message": f"Facture {invoice_id} payée avec succès",
        "invoice": invoices_db[invoice_id]
    }

# ── Point d'entrée ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)