from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, '/app/shared')
from database import User, get_db, init_db
import uvicorn

app = FastAPI(title="CloudApp — Service Auth", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "cloudapp_jwt_secret_2026")

@app.on_event("startup")
def startup():
    init_db()
    from database import SessionLocal
    db = SessionLocal()
    if not db.query(User).filter(User.email == "leonel@cloudapp.io").first():
        db.add(User(
            email="leonel@cloudapp.io",
            password_hash=pwd_context.hash("admin123"),
            username="Leonel",
            role="admin"
        ))
        db.commit()
    db.close()

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str
    role: str = "client"

class LoginRequest(BaseModel):
    email: str
    password: str

@app.get("/health")
async def health():
    return {"status": "ok", "service": "auth", "version": "2.0.0"}

@app.post("/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    user = User(
        email=req.email,
        password_hash=pwd_context.hash(req.password),
        username=req.username,
        role=req.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "username": user.username, "message": "Compte créé avec succès"}

@app.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    token = jwt.encode({
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer", "role": user.role, "username": user.username}

@app.get("/users")
async def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"total": len(users), "users": [{"id": u.id, "email": u.email, "username": u.username, "role": u.role} for u in users]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)