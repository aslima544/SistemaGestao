#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    print("⚠️ Static directory not found")

# CONFIGURAÇÃO FIXA - SEMPRE ATLAS EM PRODUÇÃO
if os.getenv("PORT"):  # Railway sempre tem PORT
    print("🚂 RAILWAY DETECTADO - Usando Atlas")
    MONGO_URL = "mongodb+srv://admin:senha45195487@cluster0.8skwoca.mongodb.net/sistema_consultorio?retryWrites=true&w=majority&appName=Cluster0"
    DB_NAME = "sistema_consultorio"
else:
    print("💻 LOCAL - Usando localhost")
    MONGO_URL = "mongodb://localhost:27017"
    DB_NAME = "consultorio_db"

print(f"🌐 MONGO: {MONGO_URL[:50]}...")
print(f"🗄️ DATABASE: {DB_NAME}")

SECRET_KEY = "secret-consultorio-2025"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database (lazy init)
client = None
db = None

def init_db():
    global client, db
    if client is None:
        try:
            print(f"🔌 Conectando: {MONGO_URL[:50]}...")
            client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            db = client[DB_NAME]
            print("✅ MongoDB conectado!")
            
            # Create admin if not exists
            if not db.users.find_one({"username": "admin"}):
                admin_data = {
                    "id": str(uuid.uuid4()),
                    "username": "admin",
                    "password_hash": pwd_context.hash("admin123"),
                    "role": "admin",
                    "email": "admin@consultorio.com",
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
    """Redirect to login page if it exists, otherwise show API info"""
    try:
        return FileResponse("static/index.html")
    except:
        return {
            "message": "Sistema de Consultórios", 
            "status": "running",
            "database": DB_NAME,
            "mongo_type": "Atlas" if "mongodb+srv" in MONGO_URL else "Local",
            "endpoints": {
                "health": "/api/health",
                "login": "/api/auth/login",
                "web_login": "/login (se disponível)"
            }
        }

@app.get("/login")
def login_page():
    """Serve login page"""
    try:
        return FileResponse("static/index.html")
    except:
        raise HTTPException(404, "Login page not found")

@app.get("/api/health")
def health():
    db_ok = init_db()
    return {
        "status": "healthy", 
        "database_connected": db_ok, 
        "database_name": DB_NAME,
        "mongo_url": MONGO_URL[:50] + "...",
        "time": datetime.utcnow()
    }

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