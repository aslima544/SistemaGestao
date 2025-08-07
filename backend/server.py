from fastapi import FastAPI, HTTPException, Depends, status, Query
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

# Database Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "consultorio_db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-tokens-consultorio")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

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
        print("Default admin user created: admin/admin123")
    
    # Create predefined consultorios if they don't exist
    existing_consultorios = db.consultorios.count_documents({})
    if existing_consultorios == 0:
        predefined_consultorios = [
            {
                "id": str(uuid.uuid4()),
                "name": "C1",
                "description": "Consultório 1 - Estratégia Saúde da Família 1",
                "capacity": 2,
                "equipment": ["Estetoscópio", "Tensiômetro", "Balança", "Mesa ginecológica"],
                "location": "Térreo - Ala Oeste",
                "occupancy_type": "fixed",
                "fixed_schedule": {
                    "team": "ESF 1",
                    "start": "07:00",
                    "end": "16:00"
                },
                "weekly_schedule": None,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "C2",
                "description": "Consultório 2 - Estratégia Saúde da Família 2",
                "capacity": 2,
                "equipment": ["Estetoscópio", "Tensiômetro", "Balança", "Mesa ginecológica"],
                "location": "Térreo - Ala Oeste",
                "occupancy_type": "fixed",
                "fixed_schedule": {
                    "team": "ESF 2",
                    "start": "07:00",
                    "end": "16:00"
                },
                "weekly_schedule": None,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "C3",
                "description": "Consultório 3 - Estratégia Saúde da Família 3",
                "capacity": 2,
                "equipment": ["Estetoscópio", "Tensiômetro", "Balança", "Mesa ginecológica"],
                "location": "Térreo - Ala Leste",
                "occupancy_type": "fixed",
                "fixed_schedule": {
                    "team": "ESF 3",
                    "start": "08:00",
                    "end": "17:00"
                },
                "weekly_schedule": None,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "C4",
                "description": "Consultório 4 - Estratégia Saúde da Família 4",
                "capacity": 2,
                "equipment": ["Estetoscópio", "Tensiômetro", "Balança", "Mesa ginecológica"],
                "location": "Térreo - Ala Leste",
                "occupancy_type": "fixed",
                "fixed_schedule": {
                    "team": "ESF 4",
                    "start": "10:00",
                    "end": "19:00"
                },
                "weekly_schedule": None,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "C5",
                "description": "Consultório 5 - Estratégia Saúde da Família 5",
                "capacity": 2,
                "equipment": ["Estetoscópio", "Tensiômetro", "Balança", "Mesa ginecológica"],
                "location": "1º Andar - Ala Central",
                "occupancy_type": "fixed",
                "fixed_schedule": {
                    "team": "ESF 5",
                    "start": "12:00",
                    "end": "21:00"
                },
                "weekly_schedule": None,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "C6",
                "description": "Consultório 6 - Uso Rotativo (Especialistas)",
                "capacity": 2,
                "equipment": ["Estetoscópio", "Tensiômetro", "Eletrocardiógrafo", "Maca"],
                "location": "1º Andar - Ala Norte",
                "occupancy_type": "rotative",
                "fixed_schedule": None,
                "weekly_schedule": {
                    "monday": {"morning": "Cardiologia", "afternoon": "Cardiologia"},
                    "tuesday": {"morning": "Acupuntura", "afternoon": "Acupuntura"},
                    "wednesday": {"morning": "Cardiologia", "afternoon": "Cardiologia"},
                    "thursday": {"morning": "Cardiologia", "afternoon": "Ginecologista"},
                    "friday": {"morning": "Acupuntura", "afternoon": "Acupuntura"},
                    "saturday": {"morning": "Livre", "afternoon": "Livre"},
                    "sunday": {"morning": "Livre", "afternoon": "Livre"}
                },
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "C7",
                "description": "Consultório 7 - Uso Rotativo (Médico Apoio/Especialistas)",
                "capacity": 2,
                "equipment": ["Estetoscópio", "Tensiômetro", "Otoscópio", "Oftalmoscópio"],
                "location": "1º Andar - Ala Norte",
                "occupancy_type": "rotative",
                "fixed_schedule": None,
                "weekly_schedule": {
                    "monday": {"morning": "Médico Apoio", "afternoon": "Médico Apoio"},
                    "tuesday": {"morning": "Livre", "afternoon": "Cardiologia"},
                    "wednesday": {"morning": "Pediatria", "afternoon": "Acupuntura"},
                    "thursday": {"morning": "Pediatria", "afternoon": "Acupuntura"},
                    "friday": {"morning": "Médico Apoio", "afternoon": "Médico Apoio"},
                    "saturday": {"morning": "Livre", "afternoon": "Livre"},
                    "sunday": {"morning": "Livre", "afternoon": "Livre"}
                },
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "C8",
                "description": "Consultório 8 - Coringa (E-Multi/Apoio/Reserva)",
                "capacity": 3,
                "equipment": ["Estetoscópio", "Tensiômetro", "Balança", "Mesa auxiliar"],
                "location": "1º Andar - Ala Sul",
                "occupancy_type": "rotative",
                "fixed_schedule": None,
                "weekly_schedule": {
                    "monday": {"morning": "E-MULTI", "afternoon": "E-MULTI"},
                    "tuesday": {"morning": "Médico Apoio", "afternoon": "Médico Apoio"},
                    "wednesday": {"morning": "E-MULTI", "afternoon": "E-MULTI"},
                    "thursday": {"morning": "Médico Apoio", "afternoon": "Médico Apoio"},
                    "friday": {"morning": "Apoio/Reserva", "afternoon": "Apoio/Reserva"},
                    "saturday": {"morning": "Livre", "afternoon": "Livre"},
                    "sunday": {"morning": "Livre", "afternoon": "Livre"}
                },
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        ]
        
        db.consultorios.insert_many(predefined_consultorios)
        print("Predefined consultorios created successfully!")

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

@app.put("/api/consultorios/{consultorio_id}/horario")
async def update_consultorio_hours(
    consultorio_id: str,
    horario_inicio: str = Query(..., description="Horário de início (HH:MM)"),
    horario_fim: str = Query(..., description="Horário de fim (HH:MM)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Update consultorio operating hours.
    Only admins can modify consultorio schedules.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can modify consultorio schedules")
    
    # Validate time format
    import re
    time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    if not re.match(time_pattern, horario_inicio) or not re.match(time_pattern, horario_fim):
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
    
    # Validate that end time is after start time
    start_minutes = int(horario_inicio[:2]) * 60 + int(horario_inicio[3:])
    end_minutes = int(horario_fim[:2]) * 60 + int(horario_fim[3:])
    
    if end_minutes <= start_minutes:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    # Find consultorio
    consultorio = db.consultorios.find_one({"id": consultorio_id})
    if not consultorio:
        raise HTTPException(status_code=404, detail="Consultório not found")
    
    # Update fixed_schedule with new hours
    update_data = {}
    if consultorio.get("fixed_schedule"):
        update_data["fixed_schedule.start"] = horario_inicio
        update_data["fixed_schedule.end"] = horario_fim
    else:
        # Create fixed_schedule if it doesn't exist
        update_data["fixed_schedule"] = {
            "start": horario_inicio,
            "end": horario_fim,
            "team": consultorio.get("name", "Unknown")
        }
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update in database
    result = db.consultorios.update_one(
        {"id": consultorio_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Consultório not found")
    
    # Return updated consultorio
    updated_consultorio = db.consultorios.find_one({"id": consultorio_id})
    return {
        "id": updated_consultorio["id"],
        "name": updated_consultorio["name"], 
        "horario_inicio": horario_inicio,
        "horario_fim": horario_fim,
        "updated_at": updated_consultorio["updated_at"].isoformat()
    }


@app.get("/api/consultorios/{consultorio_id}/slots")
async def get_consultorio_slots(
    consultorio_id: str, 
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get processed slots for a consultorio on a specific date.
    Returns ready-to-render slot data with occupancy status.
    """
    try:
        # Get consultorio info
        consultorio = db.consultorios.find_one({"id": consultorio_id})
        if not consultorio:
            raise HTTPException(status_code=404, detail="Consultorio not found")
            
        # Get operating hours from consultorio data (dynamic)
        horario_info = None
        consultorio_name = consultorio.get("name", "C1")  # Define sempre
        
        # Check if consultorio has fixed_schedule with valid data
        if (consultorio.get("fixed_schedule") and 
            consultorio["fixed_schedule"].get("start") and 
            consultorio["fixed_schedule"].get("end") and
            isinstance(consultorio["fixed_schedule"]["start"], str) and
            isinstance(consultorio["fixed_schedule"]["end"], str)):
            
            horario_info = {
                "inicio": consultorio["fixed_schedule"]["start"],
                "fim": consultorio["fixed_schedule"]["end"]
            }
        else:
            # Fallback to default hours
            default_hours = {
                "C1": {"inicio": "07:00", "fim": "16:00"},
                "C2": {"inicio": "07:00", "fim": "16:00"},
                "C3": {"inicio": "08:00", "fim": "17:00"},
                "C4": {"inicio": "10:00", "fim": "19:00"},
                "C5": {"inicio": "12:00", "fim": "21:00"},
                "C6": {"inicio": "07:00", "fim": "19:00"},
                "C7": {"inicio": "07:00", "fim": "19:00"},
                "C8": {"inicio": "07:00", "fim": "19:00"}
            }
            horario_info = default_hours.get(consultorio_name, {"inicio": "08:00", "fim": "17:00"})
        
        # Validate horario_info structure
        if not horario_info or not horario_info.get("inicio") or not horario_info.get("fim"):
            raise HTTPException(status_code=500, detail=f"Invalid operating hours configuration for {consultorio.get('name', 'unknown')}")
        
        # Generate all 15-minute slots
        try:
            inicio_parts = horario_info["inicio"].split(":")
            fim_parts = horario_info["fim"].split(":")
            
            inicio_minutos = int(inicio_parts[0]) * 60 + int(inicio_parts[1])
            fim_minutos = int(fim_parts[0]) * 60 + int(fim_parts[1])
        except (ValueError, IndexError, AttributeError) as e:
            raise HTTPException(status_code=500, detail=f"Invalid time format in operating hours: {e}")
        
        slots = []
        for minutos in range(inicio_minutos, fim_minutos, 15):
            horas = minutos // 60
            mins = minutos % 60
            horario = f"{horas:02d}:{mins:02d}"
            slots.append(horario)
        
        # Get all appointments for this consultorio on this date
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)
        
        appointments = list(db.appointments.find({
            "consultorio_id": consultorio_id,
            "appointment_date": {
                "$gte": start_date,
                "$lt": end_date
            }
        }))
        
        # Build occupancy map
        ocupacao_map = {}
        for appointment in appointments:
            if appointment.get("status") == "canceled":
                continue
                
            apt_datetime = appointment["appointment_date"]
            duracao = appointment.get("duration_minutes", 30)
            
            # Convert UTC appointment time to local time (GMT-3) for slot mapping
            local_datetime = apt_datetime + timedelta(hours=-3)
            
            # Mark all 15-minute slots occupied by this appointment
            inicio_minutos_apt = local_datetime.hour * 60 + local_datetime.minute
            fim_minutos_apt = inicio_minutos_apt + duracao
            
            for m in range(inicio_minutos_apt, fim_minutos_apt, 15):
                h = m // 60
                mins = m % 60
                slot = f"{h:02d}:{mins:02d}"
                ocupacao_map[slot] = {
                    "appointment_id": appointment.get("id"),
                    "patient_name": appointment.get("patient_name", ""),
                    "doctor_name": appointment.get("doctor_name", ""),
                    "status": appointment.get("status", "scheduled"),
                    "duration": duracao
                }
        
        # Build final response - CORRECT TIMEZONE LOGIC
        # Get current time in Brazil timezone (UTC-3)
        current_utc = datetime.utcnow()
        brazil_offset = timedelta(hours=-3)  # GMT-3 (Brasília)
        current_local = current_utc + brazil_offset
        
        selected_date = start_date.date()
        
        processed_slots = []
        for slot in slots:
            slot_parts = slot.split(":")
            slot_hour = int(slot_parts[0])
            slot_minute = int(slot_parts[1])
            
            # Check if slot is in the past (only for today)
            is_past = False
            if selected_date == current_local.date():  # Only check for today
                current_hour_minute = current_local.hour * 60 + current_local.minute
                slot_hour_minute = slot_hour * 60 + slot_minute
                is_past = slot_hour_minute < current_hour_minute
            
            is_occupied = slot in ocupacao_map
            
            slot_data = {
                "time": slot,
                "is_occupied": is_occupied,
                "is_past": is_past,
                "is_available": not is_occupied and not is_past,
                "occupancy_info": ocupacao_map.get(slot, None)
            }
            
            processed_slots.append(slot_data)
        
        return {
            "consultorio_id": consultorio_id,
            "consultorio_name": consultorio_name,
            "date": date,
            "slots": processed_slots
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing slots: {str(e)}")


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
    
    # Validate appointment is within consultorio operating hours
    # Get operating hours from consultorio data (not hardcoded)
    horario_info = None
    
    # Check if consultorio has fixed_schedule
    if consultorio.get("fixed_schedule") and consultorio["fixed_schedule"].get("start") and consultorio["fixed_schedule"].get("end"):
        horario_info = {
            "inicio": consultorio["fixed_schedule"]["start"],
            "fim": consultorio["fixed_schedule"]["end"]
        }
    else:
        # Fallback to default hours or add custom hours field
        consultorio_name = consultorio.get("name", "C1")
        default_hours = {
            "C1": {"inicio": "07:00", "fim": "16:00"},
            "C2": {"inicio": "07:00", "fim": "16:00"},
            "C3": {"inicio": "08:00", "fim": "17:00"},
            "C4": {"inicio": "10:00", "fim": "19:00"},
            "C5": {"inicio": "12:00", "fim": "21:00"},
            "C6": {"inicio": "07:00", "fim": "19:00"},
            "C7": {"inicio": "07:00", "fim": "19:00"},
            "C8": {"inicio": "07:00", "fim": "19:00"}
        }
        horario_info = default_hours.get(consultorio_name, {"inicio": "08:00", "fim": "17:00"})
    
    # Convert UTC appointment time to local time (GMT-3) for validation
    utc_dt = appointment.appointment_date
    if utc_dt.tzinfo is not None:
        utc_dt = utc_dt.replace(tzinfo=None)
    
    # Convert to local time (GMT-3)
    local_dt = utc_dt + timedelta(hours=-3)
    apt_hour = local_dt.hour
    apt_minute = local_dt.minute
    apt_time_minutes = apt_hour * 60 + apt_minute
    
    # Get consultorio operating hours
    inicio_parts = horario_info["inicio"].split(":")
    fim_parts = horario_info["fim"].split(":")
    inicio_minutes = int(inicio_parts[0]) * 60 + int(inicio_parts[1])
    fim_minutes = int(fim_parts[0]) * 60 + int(fim_parts[1])
    
    # Check if appointment is within operating hours
    if apt_time_minutes < inicio_minutes or apt_time_minutes >= fim_minutes:
        raise HTTPException(
            status_code=400, 
            detail=f"Horário fora do funcionamento do {consultorio_name}. Funcionamento: {horario_info['inicio']}-{horario_info['fim']} (horário local: {local_dt.strftime('%H:%M')})"
        )
    
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

@app.get("/api/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")  
async def health_check_root():
    """Health check endpoint at root level"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)