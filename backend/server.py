from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import uuid
from bson import ObjectId
from datetime import datetime

load_dotenv()

app = FastAPI(title="Sistema de Gestão de Consultórios", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration - FORÇADO PARA RAILWAY
print("🔍 Verificando variáveis de ambiente...")
print(f"MONGO_URL exists: {'MONGO_URL' in os.environ}")
print(f"DATABASE_URL exists: {'DATABASE_URL' in os.environ}")

# FORÇA ATLAS EM PRODUÇÃO (detecta Railway pela porta ou env)
if os.getenv("PORT") or os.getenv("RAILWAY_ENVIRONMENT"):
    print("🚂 Railway detectado - FORÇANDO Atlas connection")
    MONGO_URL = "mongodb+srv://admin:senha45195487@cluster0.8skwoca.mongodb.net/sistema_consultorio?retryWrites=true&w=majority&appName=Cluster0"
    DATABASE_NAME = "sistema_consultorio"
    print("🔥 FORÇADO: Atlas connection configurada")
else:
    # Local development
    MONGO_URL = (os.getenv("MONGO_URL") or 
                 os.getenv("DATABASE_URL") or 
                 os.getenv("MONGODB_URI") or "mongodb://localhost:27017").strip()
    DATABASE_NAME = os.getenv("DATABASE_NAME", "consultorio_db")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-tokens-consultorio")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

print(f"🔍 MONGO_URL valor final: {MONGO_URL[:50]}...")
print(f"🔍 DATABASE_NAME: {DATABASE_NAME}")
print(f"🌐 URL FINAL sendo usada: {MONGO_URL[:50]}...")

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic Models
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str = "reception"  # admin, doctor, reception

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_active: bool = True
    created_at: datetime

class PatientBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: str
    cpf: str
    birth_date: datetime
    address: Optional[str] = None
    medical_history: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: str
    created_at: datetime
    updated_at: datetime

class DoctorBase(BaseModel):
    name: str
    email: str
    phone: str
    crm: str
    specialty: str
    available_hours: List[str] = []  # ["09:00", "10:00", "14:00"]

class DoctorCreate(DoctorBase):
    pass

class Doctor(DoctorBase):
    id: str
    created_at: datetime
    is_active: bool = True

class ConsultorioBase(BaseModel):
    name: str
    description: Optional[str] = None
    capacity: int = 1
    equipment: Optional[List[str]] = []
    location: Optional[str] = None
    occupancy_type: str = "fixed"  # fixed, rotative
    fixed_schedule: Optional[dict] = None  # {"team": "ESF 1", "start": "07:00", "end": "16:00"}
    weekly_schedule: Optional[dict] = None  # {"monday": {"morning": "Cardiologia", "afternoon": "Cardiologia"}, ...}
    is_active: bool = True

class ConsultorioCreate(ConsultorioBase):
    pass

class Consultorio(ConsultorioBase):
    id: str
    created_at: datetime

class AppointmentBase(BaseModel):
    patient_id: str
    doctor_id: str
    consultorio_id: str
    appointment_date: datetime
    duration_minutes: int = 30
    notes: Optional[str] = None
    status: str = "scheduled"  # scheduled, completed, canceled

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ProcedimentoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None

class ProcedimentoCreate(ProcedimentoBase):
    pass

class Procedimento(ProcedimentoBase):
    id: str

# Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

def serialize_doc(doc):
    """Convert MongoDB document to dict with string ID"""
    if doc:
        # If document already has custom 'id' field, keep it; otherwise use _id
        if "id" not in doc:
            doc["id"] = str(doc["_id"])
        if "_id" in doc:
            del doc["_id"]
    return doc

# Initialize predefined consultorios
@app.on_event("startup")
async def startup_event():
    """Startup event - now non-blocking for better Railway deployment"""
    try:
        print("🚀 Iniciando aplicação...")
        print("🔍 Testando conexão com MongoDB...")
        
        # Test MongoDB connection (non-blocking)
        try:
            # Quick connection test with timeout
            client.admin.command('ping')
            print("✅ MongoDB conectado com sucesso!")
            
            # Create default admin user if doesn't exist
            admin_user = db.users.find_one({"username": "admin"})
            if not admin_user:
                admin_data = {
                    "id": str(uuid.uuid4()),
                    "username": "admin",
                    "email": "admin@consultorio.com",
                    "full_name": "Administrador",
                    "role": "admin",
                    "password_hash": get_password_hash("admin123"),
                    "is_active": True,
                    "created_at": datetime.utcnow()
                }
                db.users.insert_one(admin_data)
                print("✅ Default admin user created: admin/admin123")
            else:
                print("✅ Admin user already exists")
            
            # Create predefined consultorios if they don't exist  
            existing_consultorios = db.consultorios.count_documents({})
            if existing_consultorios == 0:
                print("📋 Criando consultórios padrão...")
                predefined_consultorios = [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "C1",
                        "description": "Consultório 1 - Estratégia Saúde da Família 1",
                        "capacity": 2,
                        "equipment": ["Estetoscópio", "Tensiômetro", "Balança"],
                        "location": "Térreo - Ala Oeste",
                        "occupancy_type": "fixed",
                        "is_active": True,
                        "fixed_schedule": {
                            "team": "ESF 1",
                            "start": "07:00",
                            "end": "16:00"
                        }
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "C2", 
                        "description": "Consultório 2 - Estratégia Saúde da Família 2",
                        "capacity": 2,
                        "equipment": ["Estetoscópio", "Tensiômetro", "Balança"],
                        "location": "Térreo - Ala Oeste",
                        "occupancy_type": "fixed",
                        "is_active": True,
                        "fixed_schedule": {
                            "team": "ESF 2",
                            "start": "07:00",
                            "end": "16:00"
                        }
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "C3",
                        "description": "Consultório 3 - Estratégia Saúde da Família 3",
                        "capacity": 2,
                        "equipment": ["Estetoscópio", "Tensiômetro", "Balança"],
                        "location": "Térreo - Ala Este",
                        "occupancy_type": "fixed",
                        "is_active": True,
                        "fixed_schedule": {
                            "team": "ESF 3",
                            "start": "07:00",
                            "end": "16:00"
                        }
                    }
                ]
                
                for consultorio in predefined_consultorios:
                    db.consultorios.insert_one(consultorio)
                print(f"✅ {len(predefined_consultorios)} consultórios criados")
            else:
                print(f"✅ {existing_consultorios} consultórios já existem")
                
        except Exception as mongo_error:
            print(f"⚠️ Erro de conexão MongoDB (não-crítico): {str(mongo_error)}")
            print("🔄 Aplicação continuará funcionando. Dados serão criados no primeiro acesso.")
            
    except Exception as e:
        print(f"⚠️ Erro no startup (não-crítico): {str(e)}")
        print("🔄 Aplicação continuará funcionando.")
        
    print("✅ Startup completado - aplicação pronta!")

# Auth Routes
@app.post("/api/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    user = db.users.find_one({"username": login_request.username})
    if not user or not verify_password(login_request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return serialize_doc(current_user)

# User Routes
@app.post("/api/users", response_model=User)
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    # Check if username already exists
    if db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_data = {
        "id": str(uuid.uuid4()),
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "password_hash": get_password_hash(user.password),
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    result = db.users.insert_one(user_data)
    created_user = db.users.find_one({"_id": result.inserted_id})
    return serialize_doc(created_user)

@app.get("/api/users", response_model=List[User])
async def get_users(current_user: dict = Depends(get_current_user)):
    users = list(db.users.find({}))
    return [serialize_doc(user) for user in users]

@app.get("/api/users", response_model=List[User])
async def get_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can list users")
    
    users = list(db.users.find({}))
    return [serialize_doc(user) for user in users]

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view users")
    
    user = db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_doc(user)

@app.put("/api/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update users")
    
    # Check if user exists
    existing_user = db.users.find_one({"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {
        "email": user_update.email,
        "full_name": user_update.full_name,
        "role": user_update.role,
        "updated_at": datetime.utcnow()
    }
    
    # Only update password if provided
    if user_update.password:
        update_data["password_hash"] = get_password_hash(user_update.password)
    
    result = db.users.update_one({"id": user_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = db.users.find_one({"id": user_id})
    return serialize_doc(updated_user)

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    # Prevent deletion of admin users
    user_to_delete = db.users.find_one({"id": user_id})
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_to_delete["role"] == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    # Prevent self-deletion
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    result = db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Patient Routes
@app.post("/api/patients", response_model=Patient)
async def create_patient(patient: PatientCreate, current_user: dict = Depends(get_current_user)):
    patient_data = {
        "id": str(uuid.uuid4()),
        **patient.dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.patients.insert_one(patient_data)
    created_patient = db.patients.find_one({"_id": result.inserted_id})
    return serialize_doc(created_patient)

@app.get("/api/patients", response_model=List[Patient])
async def get_patients(current_user: dict = Depends(get_current_user)):
    patients = list(db.patients.find({}))
    return [serialize_doc(patient) for patient in patients]

@app.get("/api/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str, current_user: dict = Depends(get_current_user)):
    patient = db.patients.find_one({"id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return serialize_doc(patient)

@app.put("/api/patients/{patient_id}", response_model=Patient)
async def update_patient(patient_id: str, patient_update: PatientCreate, current_user: dict = Depends(get_current_user)):
    update_data = {
        **patient_update.dict(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.patients.update_one({"id": patient_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    updated_patient = db.patients.find_one({"id": patient_id})
    return serialize_doc(updated_patient)

@app.delete("/api/patients/{patient_id}")
async def delete_patient(patient_id: str, current_user: dict = Depends(get_current_user)):
    result = db.patients.delete_one({"id": patient_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

# Doctor Routes
@app.post("/api/doctors", response_model=Doctor)
async def create_doctor(doctor: DoctorCreate, current_user: dict = Depends(get_current_user)):
    doctor_data = {
        "id": str(uuid.uuid4()),
        **doctor.dict(),
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = db.doctors.insert_one(doctor_data)
    created_doctor = db.doctors.find_one({"_id": result.inserted_id})
    return serialize_doc(created_doctor)

@app.get("/api/doctors", response_model=List[Doctor])
async def get_doctors(current_user: dict = Depends(get_current_user)):
    doctors = list(db.doctors.find({"is_active": True}))
    return [serialize_doc(doctor) for doctor in doctors]

@app.get("/api/doctors/{doctor_id}", response_model=Doctor)
async def get_doctor(doctor_id: str, current_user: dict = Depends(get_current_user)):
    doctor = db.doctors.find_one({"id": doctor_id})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return serialize_doc(doctor)

@app.put("/api/doctors/{doctor_id}", response_model=Doctor)
async def update_doctor(doctor_id: str, doctor_update: DoctorCreate, current_user: dict = Depends(get_current_user)):
    update_data = {
        **doctor_update.dict(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.doctors.update_one({"id": doctor_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    updated_doctor = db.doctors.find_one({"id": doctor_id})
    return serialize_doc(updated_doctor)

@app.delete("/api/doctors/{doctor_id}")
async def delete_doctor(doctor_id: str, current_user: dict = Depends(get_current_user)):
    result = db.doctors.delete_one({"id": doctor_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"message": "Doctor deleted successfully"}

# Consultorio Routes
@app.post("/api/consultorios", response_model=Consultorio)
async def create_consultorio(consultorio: ConsultorioCreate, current_user: dict = Depends(get_current_user)):
    consultorio_data = {
        "id": str(uuid.uuid4()),
        **consultorio.dict(),
        "created_at": datetime.utcnow()
    }
    
    result = db.consultorios.insert_one(consultorio_data)
    created_consultorio = db.consultorios.find_one({"_id": result.inserted_id})
    return serialize_doc(created_consultorio)

@app.get("/api/consultorios", response_model=List[Consultorio])
async def get_consultorios(current_user: dict = Depends(get_current_user)):
    consultorios = list(db.consultorios.find({"is_active": True}))
    return [serialize_doc(consultorio) for consultorio in consultorios]

# Get consultorio availability for a specific day
@app.get("/api/consultorios/availability/{day_of_week}")
async def get_consultorio_availability(day_of_week: str, current_user: dict = Depends(get_current_user)):
    """
    Get availability of all consultorios for a specific day of week
    day_of_week: monday, tuesday, wednesday, thursday, friday
    """
    consultorios = list(db.consultorios.find({"is_active": True}))
    availability = []
    
    for consultorio in consultorios:
        consultorio_data = serialize_doc(consultorio)
        
        if consultorio["occupancy_type"] == "fixed":
            # Fixed schedule - ESF teams
            schedule_info = consultorio.get("fixed_schedule", {})
            availability.append({
                **consultorio_data,
                "day_schedule": {
                    "team": schedule_info.get("team", "N/A"),
                    "start_time": schedule_info.get("start", "N/A"),
                    "end_time": schedule_info.get("end", "N/A"),
                    "type": "fixed"
                }
            })
        else:
            # Rotative schedule - check weekly schedule
            weekly_schedule = consultorio.get("weekly_schedule", {})
            day_schedule = weekly_schedule.get(day_of_week.lower(), {})
            
            availability.append({
                **consultorio_data,
                "day_schedule": {
                    "morning": day_schedule.get("morning", "Livre"),
                    "afternoon": day_schedule.get("afternoon", "Livre"),
                    "type": "rotative"
                }
            })
    
    return availability

# TEMPORARY SETUP ENDPOINT FOR RAILWAY (REMOVE AFTER USE)
@app.post("/api/setup-system")
async def setup_system():
    """Temporary endpoint to initialize system data for Railway deployment"""
    try:
        # Create admin user if doesn't exist
        existing_admin = db.users.find_one({"username": "admin"})
        if not existing_admin:
            admin_data = {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "email": "admin@consultorio.com",
                "full_name": "Administrador",
                "role": "admin",
                "password_hash": get_password_hash("admin123"),
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            db.users.insert_one(admin_data)
            
        # Create basic users
        users_data = [
            {
                "id": str(uuid.uuid4()),
                "username": "recepcao",
                "email": "recepcao@consultorio.com", 
                "full_name": "Recepção",
                "role": "reception",
                "password_hash": get_password_hash("recepcao123"),
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        ]
        
        for user_data in users_data:
            existing = db.users.find_one({"username": user_data["username"]})
            if not existing:
                db.users.insert_one(user_data)
        
        # Create consultorios if they don't exist
        existing_consultorios = db.consultorios.count_documents({})
        if existing_consultorios == 0:
            predefined_consultorios = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "C1",
                    "description": "Consultório 1 - ESF 1",
                    "capacity": 2,
                    "equipment": ["Estetoscópio", "Tensiômetro", "Balança"],
                    "location": "Térreo - Ala Oeste",
                    "occupancy_type": "fixed",
                    "is_active": True,
                    "fixed_schedule": {
                        "team": "ESF 1",
                        "start": "07:00",
                        "end": "16:00"
                    }
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "C2", 
                    "description": "Consultório 2 - ESF 2",
                    "capacity": 2,
                    "equipment": ["Estetoscópio", "Tensiômetro", "Balança"],
                    "location": "Térreo - Ala Oeste",
                    "occupancy_type": "fixed",
                    "is_active": True,
                    "fixed_schedule": {
                        "team": "ESF 2", 
                        "start": "07:00",
                        "end": "16:00"
                    }
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "C3",
                    "description": "Consultório 3 - ESF 3", 
                    "capacity": 2,
                    "equipment": ["Estetoscópio", "Tensiômetro", "Balança"],
                    "location": "Térreo - Ala Este",
                    "occupancy_type": "fixed",
                    "is_active": True,
                    "fixed_schedule": {
                        "team": "ESF 3",
                        "start": "07:00", 
                        "end": "16:00"
                    }
                }
            ]
            
            for consultorio in predefined_consultorios:
                db.consultorios.insert_one(consultorio)
        
        return {
            "message": "System initialized successfully",
            "users_created": db.users.count_documents({}),
            "consultorios_created": db.consultorios.count_documents({}),
            "admin_credentials": {
                "username": "admin",
                "password": "admin123"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

# Get weekly schedule overview
@app.get("/api/consultorios/weekly-schedule")
async def get_weekly_schedule(current_user: dict = Depends(get_current_user)):
    """Get complete weekly schedule for all consultorios"""
    consultorios = list(db.consultorios.find({"is_active": True}))
    
    weekly_data = {
        "fixed_consultorios": [],
        "rotative_consultorios": [],
        "schedule_grid": {}
    }
    
    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    day_names = {
        "monday": "Segunda",
        "tuesday": "Terça", 
        "wednesday": "Quarta",
        "thursday": "Quinta",
        "friday": "Sexta",
        
    }
    
    for consultorio in consultorios:
        consultorio_data = serialize_doc(consultorio)
        
        if consultorio["occupancy_type"] == "fixed":
            schedule_info = consultorio.get("fixed_schedule", {})
            weekly_data["fixed_consultorios"].append({
                **consultorio_data,
                "team": schedule_info.get("team", "N/A"),
                "schedule": f"{schedule_info.get('start', 'N/A')} - {schedule_info.get('end', 'N/A')}"
            })
        else:
            weekly_data["rotative_consultorios"].append(consultorio_data)
            
            # Build schedule grid for rotative consultorios
            if consultorio["name"] not in weekly_data["schedule_grid"]:
                weekly_data["schedule_grid"][consultorio["name"]] = {}
            
            weekly_schedule = consultorio.get("weekly_schedule", {})
            for day in days:
                day_schedule = weekly_schedule.get(day, {})
                weekly_data["schedule_grid"][consultorio["name"]][day_names[day]] = {
                    "morning": day_schedule.get("morning", "Livre"),
                    "afternoon": day_schedule.get("afternoon", "Livre")
                }
    
    return weekly_data

@app.get("/api/consultorios/{consultorio_id}", response_model=Consultorio)
async def get_consultorio(consultorio_id: str, current_user: dict = Depends(get_current_user)):
    consultorio = db.consultorios.find_one({"id": consultorio_id})
    if not consultorio:
        raise HTTPException(status_code=404, detail="Consultório not found")
    return serialize_doc(consultorio)

@app.put("/api/consultorios/{consultorio_id}", response_model=Consultorio)
async def update_consultorio(consultorio_id: str, consultorio_update: ConsultorioCreate, current_user: dict = Depends(get_current_user)):
    update_data = {
        **consultorio_update.dict(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.consultorios.update_one({"id": consultorio_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Consultório not found")
    
    updated_consultorio = db.consultorios.find_one({"id": consultorio_id})
    return serialize_doc(updated_consultorio)

@app.delete("/api/consultorios/{consultorio_id}")
async def delete_consultorio(consultorio_id: str, current_user: dict = Depends(get_current_user)):
    result = db.consultorios.update_one({"id": consultorio_id}, {"$set": {"is_active": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Consultório not found")
    return {"message": "Consultório deleted successfully"}


# Rotas CRUD para procedimentos
@app.post("/api/procedimentos", response_model=Procedimento)
async def create_procedimento(procedimento: ProcedimentoCreate, current_user: dict = Depends(get_current_user)):
    procedimento_data = {
        "id": str(uuid.uuid4()),
        "nome": procedimento.nome,
        "descricao": procedimento.descricao
    }
    db.procedimentos.insert_one(procedimento_data)
    return procedimento_data

@app.get("/api/procedimentos", response_model=List[Procedimento])
async def get_procedimentos(current_user: dict = Depends(get_current_user)):
    procedimentos = list(db.procedimentos.find({}))
    return [serialize_doc(p) for p in procedimentos]

@app.put("/api/procedimentos/{procedimento_id}", response_model=Procedimento)
async def update_procedimento(procedimento_id: str, procedimento: ProcedimentoCreate, current_user: dict = Depends(get_current_user)):
    db.procedimentos.update_one({"id": procedimento_id}, {"$set": procedimento.dict()})
    updated = db.procedimentos.find_one({"id": procedimento_id})
    return serialize_doc(updated)

@app.delete("/api/procedimentos/{procedimento_id}")
async def delete_procedimento(procedimento_id: str, current_user: dict = Depends(get_current_user)):
    db.procedimentos.delete_one({"id": procedimento_id})
    return {"message": "Procedimento excluído com sucesso"}

# Initialize predefined consultorios
@app.post("/api/appointments", response_model=Appointment)
async def create_appointment(appointment: AppointmentCreate, current_user: dict = Depends(get_current_user)):
    # Check if patient exists
    patient = db.patients.find_one({"id": appointment.patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Convert appointment date to UTC naive datetime for comparison
    if appointment.appointment_date.tzinfo is not None:
        appointment_utc = appointment.appointment_date.replace(tzinfo=None)
    else:
        appointment_utc = appointment.appointment_date
    
    if appointment_utc < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Não é possível agendar para um horário que já passou.")
    
    # Check if doctor exists
    doctor = db.doctors.find_one({"id": appointment.doctor_id})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check if consultorio exists
    consultorio = db.consultorios.find_one({"id": appointment.consultorio_id, "is_active": True})
    if not consultorio:
        raise HTTPException(status_code=404, detail="Consultório not found")
    
    # Check for conflicts (same consultorio at same time)
    start_time = appointment.appointment_date
    end_time = start_time + timedelta(minutes=appointment.duration_minutes)
    
    # Convert to naive datetime if needed for comparison
    if start_time.tzinfo is not None:
        start_time = start_time.replace(tzinfo=None)
    if end_time.tzinfo is not None:
        end_time = end_time.replace(tzinfo=None)
    
    # Find any existing appointments that overlap with this time slot
    existing_appointments = list(db.appointments.find({
        "consultorio_id": appointment.consultorio_id,
        "status": {"$ne": "canceled"}
    }))
    
    for existing in existing_appointments:
        existing_start = existing["appointment_date"]
        if hasattr(existing_start, 'tzinfo') and existing_start.tzinfo is not None:
            existing_start = existing_start.replace(tzinfo=None)
        
        existing_end = existing_start + timedelta(minutes=existing.get("duration_minutes", 30))
        
        # Check if there's any overlap
        # Two appointments overlap if: start1 < end2 AND start2 < end1
        if start_time < existing_end and existing_start < end_time:
            raise HTTPException(status_code=409, detail="Consultório já ocupado neste horário")
    
    
    appointment_data = {
        "id": str(uuid.uuid4()),
        **appointment.dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.appointments.insert_one(appointment_data)
    created_appointment = db.appointments.find_one({"_id": result.inserted_id})
    return serialize_doc(created_appointment)

@app.get("/api/appointments", response_model=List[Appointment])
async def get_appointments(current_user: dict = Depends(get_current_user)):
    try:
        appointments = list(db.appointments.find({}))
        result = []
        for appointment in appointments:
            # Busca o nome do paciente
            patient = db.patients.find_one({"id": appointment.get("patient_id", "")})
            patient_name = patient["name"] if patient else "Desconhecido"

            # Busca o nome do médico
            doctor = db.doctors.find_one({"id": appointment.get("doctor_id", "")})
            doctor_name = doctor["name"] if doctor else "Desconhecido"

            # Busca o nome do consultório (opcional)
            consultorio = db.consultorios.find_one({"id": appointment.get("consultorio_id", "")})
            consultorio_name = consultorio["name"] if consultorio else "N/A"

            appointment_data = {
                "id": appointment.get("id", str(appointment.get("_id", ""))),
                "patient_id": appointment.get("patient_id", ""),
                "patient_name": patient_name,
                "doctor_id": appointment.get("doctor_id", ""),
                "doctor_name": doctor_name,
                "consultorio_id": appointment.get("consultorio_id", ""),
                "consultorio_name": consultorio_name,
                "appointment_date": appointment.get("appointment_date", datetime.utcnow()),
                "duration_minutes": appointment.get("duration_minutes", 30),
                "notes": appointment.get("notes", ""),
                "status": appointment.get("status", "scheduled"),
                "created_at": appointment.get("created_at", datetime.utcnow()),
                "updated_at": appointment.get("updated_at", datetime.utcnow())
            }
            result.append(appointment_data)
        return result
    except Exception as e:
        print(f"Error in get_appointments: {str(e)}")
        return []

@app.get("/api/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str, current_user: dict = Depends(get_current_user)):
    appointment = db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return serialize_doc(appointment)

@app.put("/api/appointments/{appointment_id}/cancel", response_model=Appointment)
async def cancel_appointment(appointment_id: str, current_user: dict = Depends(get_current_user)):
    result = db.appointments.update_one(
        {"id": appointment_id},
        {"$set": {"status": "canceled", "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    updated_appointment = db.appointments.find_one({"id": appointment_id})
    return serialize_doc(updated_appointment)

# Dashboard Routes
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    # Get today's date range
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    # Count statistics
    total_patients = db.patients.count_documents({})
    total_doctors = db.doctors.count_documents({"is_active": True})
    total_consultorios = db.consultorios.count_documents({"is_active": True})
    total_appointments = db.appointments.count_documents({})
    
    # Today's appointments
    today_appointments = db.appointments.count_documents({
        "appointment_date": {
            "$gte": today,
            "$lt": tomorrow
        },
        "status": {"$ne": "canceled"}
    })
    
    # Recent appointments with patient, doctor and consultorio names
    recent_appointments = list(db.appointments.find({}).sort("created_at", -1).limit(5))
    for appointment in recent_appointments:
        patient = db.patients.find_one({"id": appointment.get("patient_id", "")})
        doctor = db.doctors.find_one({"id": appointment.get("doctor_id", "")})
        consultorio = db.consultorios.find_one({"id": appointment.get("consultorio_id", "")})
        appointment["patient_name"] = patient["name"] if patient else "Unknown"
        appointment["doctor_name"] = doctor["name"] if doctor else "Unknown"  
        appointment["consultorio_name"] = consultorio["name"] if consultorio else "N/A"
    
    # Consultorio occupancy today
    consultorio_stats = []
    consultorios = list(db.consultorios.find({"is_active": True}))
    for consultorio in consultorios:
        occupied_slots = db.appointments.count_documents({
            "consultorio_id": consultorio["id"],
            "appointment_date": {
                "$gte": today,
                "$lt": tomorrow
            },
            "status": {"$ne": "canceled"}
        })
        consultorio_stats.append({
            "name": consultorio["name"],
            "occupied_slots": occupied_slots,
            "id": consultorio["id"]
        })
    
    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_consultorios": total_consultorios,
        "total_appointments": total_appointments,
        "today_appointments": today_appointments,
        "recent_appointments": [serialize_doc(app) for app in recent_appointments],
        "consultorio_stats": consultorio_stats
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/debug-config")
async def debug_config():
    """Endpoint para debug das configurações (REMOVER EM PRODUÇÃO)"""
    return {
        "mongo_url_configured": bool(os.getenv("MONGO_URL")),
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
        "mongodb_uri_configured": bool(os.getenv("MONGODB_URI")),
        "database_name": DATABASE_NAME,
        "mongo_url_prefix": MONGO_URL[:20] if MONGO_URL else "NONE",
        "available_env_vars": [k for k in os.environ.keys() if 'MONGO' in k.upper() or 'DATABASE' in k.upper()]
    }

@app.get("/api/init-railway")
async def init_railway():
    """Initialize system for Railway - GET endpoint version"""
    try:
        # Check if admin already exists
        existing_admin = db.users.find_one({"username": "admin"})
        if existing_admin:
            return {
                "message": "System already initialized",
                "admin_exists": True,
                "users_count": db.users.count_documents({}),
                "consultorios_count": db.consultorios.count_documents({})
            }
        
        # Create admin user
        admin_data = {
            "id": str(uuid.uuid4()),
            "username": "admin", 
            "email": "admin@consultorio.com",
            "full_name": "Administrador",
            "role": "admin",
            "password_hash": get_password_hash("admin123"),
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        db.users.insert_one(admin_data)
        
        # Create basic consultorio if none exist
        existing_consultorios = db.consultorios.count_documents({})
        if existing_consultorios == 0:
            consultorio_data = {
                "id": str(uuid.uuid4()),
                "name": "C1",
                "description": "Consultório 1 - ESF 1", 
                "capacity": 2,
                "equipment": ["Estetoscópio", "Tensiômetro"],
                "location": "Térreo",
                "occupancy_type": "fixed",
                "is_active": True,
                "fixed_schedule": {
                    "team": "ESF 1",
                    "start": "07:00",
                    "end": "16:00"
                }
            }
            db.consultorios.insert_one(consultorio_data)
        
        return {
            "message": "Railway system initialized successfully!",
            "admin_created": True,
            "credentials": {
                "username": "admin",
                "password": "admin123"
            },
            "users_count": db.users.count_documents({}),
            "consultorios_count": db.consultorios.count_documents({})
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to initialize system"
        }

if __name__ == "__main__":
    import uvicorn
    import os
    # Use Railway's PORT environment variable or fallback to 8001 for local
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)