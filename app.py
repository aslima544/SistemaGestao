#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

# Static files mounting removed - using inline HTML instead

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
    """Serve HTML login page directly"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Gestão - Login</title>
        <meta charset="utf-8">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 400px; 
                margin: 50px auto; 
                background: #f0f2f5;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #1877f2; text-align: center; margin-bottom: 30px; }
            input { 
                width: 100%; 
                padding: 12px; 
                margin: 8px 0; 
                border: 1px solid #ddd; 
                border-radius: 4px;
                font-size: 14px;
                box-sizing: border-box;
            }
            button { 
                width: 100%; 
                padding: 12px; 
                background: #1877f2; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer;
                font-size: 16px;
                margin-top: 10px;
            }
            button:hover { background: #166fe5; }
            .result { 
                margin-top: 20px; 
                padding: 15px; 
                border-radius: 4px;
                display: none;
            }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 Sistema de Gestão</h1>
            
            <div class="info">
                <strong>Credenciais de teste:</strong><br>
                Usuário: <strong>admin</strong><br>
                Senha: <strong>admin123</strong>
            </div>
            
            <form onsubmit="return login(event)">
                <input type="text" id="username" placeholder="Nome de usuário" value="admin" required>
                <input type="password" id="password" placeholder="Senha" value="admin123" required>
                <button type="submit">🔐 Entrar no Sistema</button>
            </form>
            
            <div id="result" class="result"></div>
        </div>

        <script>
            async function login(event) {
                event.preventDefault();
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const resultDiv = document.getElementById('result');
                
                resultDiv.style.display = 'block';
                resultDiv.className = 'result info';
                resultDiv.innerHTML = '⏳ Fazendo login...';
                
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ username, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <strong>✅ Login realizado com sucesso!</strong><br><br>
                            👤 Usuário: <strong>${username}</strong><br>
                            🔑 Token gerado: <code>${data.access_token.substring(0, 30)}...</code><br><br>
                            <em>Sistema funcionando perfeitamente!</em>
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `❌ <strong>Erro:</strong> ${data.detail || 'Credenciais inválidas'}`;
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `❌ <strong>Erro de conexão:</strong> ${error.message}`;
                }
                
                return false;
            }
        </script>
    </body>
    </html>
    """
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)

@app.get("/login")
def login_page():
    """Redirect to main page since we serve HTML directly"""
    return {"message": "Use the root endpoint / for login page"}

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