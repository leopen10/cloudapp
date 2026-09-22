from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx, uvicorn

app = FastAPI(title="CloudApp — Gateway", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
import sys
sys.path.insert(0, "/app/shared")
from telemetry import setup_tracing
setup_tracing(app, "gateway", instrument_db=False)

SERVICES = {
    "auth":         "http://auth:8001",
    "project":      "http://project:8002",
    "billing":      "http://billing:8003",
    "notification": "http://notification:8004",
    "analytics":    "http://analytics:8005",
}

def _json_or_raise(r: httpx.Response):
    """Relaie le code de statut du service appele : le Gateway ne doit jamais
    transformer une erreur d'un service (422, 404, 500...) en reponse 200."""
    if r.status_code >= 400:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise HTTPException(status_code=r.status_code, detail=detail)
    return r.json()

@app.get("/")
async def root():
    return {"message": "Bienvenue sur CloudApp Gateway", "version": "2.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway", "version": "2.0.0"}

@app.get("/status")
async def status():
    results = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in SERVICES.items():
            try:
                r = await client.get(f"{url}/health")
                results[name] = {"status": "ok" if r.status_code == 200 else "error"}
            except:
                results[name] = {"status": "unreachable"}
    return {"gateway": "ok", "services": results}

# ── AUTH ──────────────────────────────────────────────────────────────────────
@app.post("/auth/login")
async def login(data: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SERVICES['auth']}/login", json=data)
        return _json_or_raise(r)

@app.post("/auth/register")
async def register(data: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SERVICES['auth']}/register", json=data)
        return _json_or_raise(r)

# ── CLIENTS ───────────────────────────────────────────────────────────────────
@app.get("/clients")
async def get_clients():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['project']}/clients")
        return _json_or_raise(r)

@app.post("/clients")
async def create_client(data: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SERVICES['project']}/clients", json=data)
        return _json_or_raise(r)

# ── PROJECTS ──────────────────────────────────────────────────────────────────
@app.get("/projects")
async def get_projects():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['project']}/projects")
        return _json_or_raise(r)

@app.get("/projects/{project_id}")
async def get_project(project_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['project']}/projects/{project_id}")
        return _json_or_raise(r)

@app.post("/projects")
async def create_project(data: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SERVICES['project']}/projects", json=data)
        result = _json_or_raise(r)
        if "id" in result:
            try:
                await client.post(f"{SERVICES['notification']}/notify/project-created", json={
                    "client_id": result.get("client_id"),
                    "project_id": result["id"],
                    "project_name": result.get("name"),
                    "budget": float(result.get("budget", 0)),
                })
            except Exception as e:
                print(f"[GATEWAY] Erreur notification projet cree: {e}")
        return result

@app.put("/projects/{project_id}")
async def update_project(project_id: int, data: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.put(f"{SERVICES['project']}/projects/{project_id}", json=data)
        result = _json_or_raise(r)
        if "progress" in data:
            try:
                await client.post(f"{SERVICES['notification']}/notify/progress", json={
                    "client_id": result.get("client_id"),
                    "project_id": project_id,
                    "project_name": result.get("name"),
                    "progress": data["progress"],
                })
            except Exception as e:
                print(f"[GATEWAY] Erreur notification avancement: {e}")
            try:
                inv_r = await client.post(
                    f"{SERVICES['billing']}/recalculate/{project_id}",
                    params={"new_progress": data["progress"]}
                )
                for inv in inv_r.json().get("invoices", []):
                    await client.post(f"{SERVICES['notification']}/notify/invoice", json={
                        "client_id": result.get("client_id"),
                        "project_id": project_id,
                        "project_name": result.get("name"),
                        "amount": inv["amount"],
                        "percentage": inv["percentage_billed"],
                    })
            except Exception as e:
                print(f"[GATEWAY] Erreur facturation/notification: {e}")
            await client.post(f"{SERVICES['analytics']}/track", json={
                "event_type": "project_updated",
                "project_id": project_id,
                "data": f"progress={data['progress']}"
            })
        return result

@app.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.delete(f"{SERVICES['project']}/projects/{project_id}")
        return _json_or_raise(r)

# ── INVOICES ──────────────────────────────────────────────────────────────────
@app.get("/invoices")
async def get_invoices():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['billing']}/invoices")
        return _json_or_raise(r)

@app.get("/invoices/project/{project_id}")
async def get_invoices_by_project(project_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['billing']}/invoices/project/{project_id}")
        return _json_or_raise(r)

@app.post("/invoices/{invoice_id}/pay")
async def pay_invoice(invoice_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SERVICES['billing']}/invoices/{invoice_id}/pay")
        return _json_or_raise(r)

# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────
@app.get("/notifications")
async def get_notifications():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['notification']}/notifications")
        return _json_or_raise(r)

@app.put("/notifications/{notif_id}/read")
async def mark_read(notif_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.put(f"{SERVICES['notification']}/notifications/{notif_id}/read")
        return _json_or_raise(r)

# ── ANALYTICS ─────────────────────────────────────────────────────────────────
@app.get("/analytics/stats")
async def get_stats():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['analytics']}/stats")
        return _json_or_raise(r)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)