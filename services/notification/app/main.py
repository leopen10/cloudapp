from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx, uvicorn, sys
sys.path.insert(0, '/app/shared')

app = FastAPI(title="CloudApp — Gateway", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SERVICES = {
    "auth": "http://auth:8001",
    "project": "http://project:8002",
    "billing": "http://billing:8003",
    "notification": "http://notification:8004",
    "analytics": "http://analytics:8005",
}

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

# ── AUTH ─────────────────────────────────────────────────────────────────────
@app.post("/auth/login")
async def login(data: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SERVICES['auth']}/login", json=data)
        return r.json()

@app.post("/auth/register")
async def register(data: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SERVICES['auth']}/register", json=data)
        return r.json()

# ── CLIENTS ──────────────────────────────────────────────────────────────────
@app.get("/clients")
async def get_clients():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['project']}/clients")
        return r.json()

@app.post("/clients")
async def create_client(data: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SERVICES['project']}/clients", json=data)
        result = r.json()
        if "id" in result:
            try:
                await client.post(f"{SERVICES['notification']}/notify/welcome",
                    json={"client_id": result["id"]})
            except Exception as e:
                print(f"[GATEWAY] Erreur notification bienvenue: {e}")
        return result

# ── PROJECTS ─────────────────────────────────────────────────────────────────
@app.get("/projects")
async def get_projects():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['project']}/projects")
        return r.json()

@app.get("/projects/{project_id}")
async def get_project(project_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['project']}/projects/{project_id}")
        return r.json()

@app.post("/projects")
async def create_project(data: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SERVICES['project']}/projects", json=data)
        result = r.json()
        if "id" in result:
            try:
                await client.post(f"{SERVICES['notification']}/notify/project-created",
                    json={
                        "client_id": result.get("client_id"),
                        "project_id": result["id"],
                        "project_name": result.get("name"),
                        "budget": float(result.get("budget", 0))
                    })
            except Exception as e:
                print(f"[GATEWAY] Erreur notification projet créé: {e}")
        return result

@app.put("/projects/{project_id}")
async def update_project(project_id: int, data: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.put(f"{SERVICES['project']}/projects/{project_id}", json=data)
        result = r.json()
        if "progress" in data:
            try:
                await client.post(f"{SERVICES['notification']}/notify/progress",
                    json={
                        "client_id": result.get("client_id"),
                        "project_id": project_id,
                        "project_name": result.get("name"),
                        "progress": data["progress"]
                    })
            except Exception as e:
                print(f"[GATEWAY] Erreur notification avancement: {e}")
            try:
                inv_r = await client.post(
                    f"{SERVICES['billing']}/recalculate/{project_id}",
                    params={"new_progress": data["progress"]})
                inv_data = inv_r.json()
                for inv in inv_data.get("invoices", []):
                    await client.post(f"{SERVICES['notification']}/notify/invoice",
                        json={
                            "client_id": result.get("client_id"),
                            "project_id": project_id,
                            "project_name": result.get("name"),
                            "amount": inv["amount"],
                            "percentage": inv["percentage_billed"]
                        })
            except Exception as e:
                print(f"[GATEWAY] Erreur facturation/notification: {e}")
            try:
                await client.post(f"{SERVICES['analytics']}/track", json={
                    "event_type": "project_updated",
                    "project_id": project_id,
                    "data": f"progress={data['progress']}"
                })
            except Exception as e:
                print(f"[GATEWAY] Erreur analytics: {e}")
        return result

@app.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.delete(f"{SERVICES['project']}/projects/{project_id}")
        return r.json()

# ── INVOICES ─────────────────────────────────────────────────────────────────
@app.get("/invoices")
async def get_invoices():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['billing']}/invoices")
        return r.json()

@app.get("/invoices/project/{project_id}")
async def get_invoices_by_project(project_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['billing']}/invoices/project/{project_id}")
        return r.json()

@app.post("/invoices/{invoice_id}/pay")
async def pay_invoice(invoice_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{SERVICES['billing']}/invoices/{invoice_id}/pay")
        return r.json()

# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────
@app.get("/notifications")
async def get_notifications():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['notification']}/notifications")
        return r.json()

@app.put("/notifications/{notif_id}/read")
async def mark_read(notif_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.put(f"{SERVICES['notification']}/notifications/{notif_id}/read")
        return r.json()

@app.put("/notifications/read-all")
async def mark_all_read():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.put(f"{SERVICES['notification']}/notifications/read-all")
        return r.json()

# ── ANALYTICS ─────────────────────────────────────────────────────────────────
@app.get("/analytics/stats")
async def get_stats():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES['analytics']}/stats")
        return r.json()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)