#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
import uuid

app = FastAPI(title="Sistema Consultório")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://admin:senha45195487@cluster0.8skwoca.mongodb.net/sistema_consultorio?retryWrites=true&w=majority&appName=Cluster0")
SECRET_KEY = os.getenv("SECRET_KEY", "secret-key-consultorio")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database (lazy init)
client = None
db = None

def init_db():
    global client, db
    if client is None:
        try:
            client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            db = client["sistema_consultorio"]
            
            # Create admin if not exists
            if not db.users.find_one({"username": "admin"}):
                admin_data = {
                    "id": str(uuid.uuid4()),
                    "username": "admin",
                    "password_hash": pwd_context.hash("admin123"),
                    "role": "admin",
                    "created_at": datetime.utcnow()
                }
                db.users.insert_one(admin_data)
                print("✅ Admin created: admin/admin123")
            return True
        except Exception as e:
            print(f"❌ DB Error: {e}")
            return False
    return True

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
def root():
    return {"message": "Sistema de Consultórios", "status": "running"}

@app.get("/api/health")
def health():
    db_ok = init_db()
    return {"status": "healthy", "database": db_ok, "time": datetime.utcnow()}

@app.post("/api/auth/login")
def login(req: LoginRequest):
    if not init_db():
        raise HTTPException(500, "Database error")
    
    user = db.users.find_one({"username": req.username})
    if user and pwd_context.verify(req.password, user["password_hash"]):
        token = jwt.encode({"sub": user["username"], "exp": datetime.utcnow() + timedelta(hours=24)}, SECRET_KEY)
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(401, "Invalid credentials")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)