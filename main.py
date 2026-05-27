from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import models
from database import SessionLocal, PostgresSessionLocal, engine_sqlite, engine_postgres

# Create the database tables for both databases
models.Base.metadata.create_all(bind=engine_sqlite)
try:
    models.Base.metadata.create_all(bind=engine_postgres)
except Exception as e:
    print(f"Skipping Postgres init locally: {e}")

app = FastAPI(title="Roomify Backend API")

# Dependency for SQLite
def get_sqlite_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for PostgreSQL
def get_postgres_db():
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schemas for data validation and API response definition
class FurnitureBase(BaseModel):
    name: str
    price: str
    model_url: str
    thumbnail_url: str
    category: str

class FurnitureCreate(FurnitureBase):
    pass

class FurnitureResponse(FurnitureBase):
    id: int

    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"message": "Welcome to the Roomify API"}

@app.get("/furniture", response_model=List[FurnitureResponse])
def get_furniture(db: Session = Depends(get_sqlite_db)):
    """Fetch all furniture items from the database."""
    items = db.query(models.Furniture).all()
    return items

@app.post("/furniture", response_model=FurnitureResponse)
def add_furniture(furniture: FurnitureCreate, db: Session = Depends(get_sqlite_db)):
    """Add a new furniture item to the database."""
    db_furniture = models.Furniture(**furniture.model_dump())
    db.add(db_furniture)
    db.commit()
    db.refresh(db_furniture)
    return db_furniture

# --- SAVED LAYOUT ENDPOINTS ---
import json
from typing import Dict, Any, Optional

class LayoutData(BaseModel):
    items: List[Dict[str, Any]]
    user_id: Optional[str] = None

@app.post("/save_layout")
def save_layout(layout: LayoutData, db: Session = Depends(get_postgres_db)):
    """Save a room layout JSON from Unity to the database."""
    json_str = json.dumps({"items": layout.items})
    db_layout = models.SavedLayout(name="My Room Design", json_data=json_str, user_id=layout.user_id)
    db.add(db_layout)
    db.commit()
    db.refresh(db_layout)
    return {"message": "Success", "id": db_layout.id}

@app.get("/get_layouts")
def get_layouts(user_id: Optional[str] = None, db: Session = Depends(get_postgres_db)):
    """Fetch saved layouts for the given user (or all if not provided)."""
    if user_id:
        layouts = db.query(models.SavedLayout).filter(models.SavedLayout.user_id == user_id).all()
    else:
        layouts = db.query(models.SavedLayout).all()
    return layouts

# --- USER AUTHENTICATION ENDPOINTS ---
import hashlib

class UserCreate(BaseModel):
    full_name: str
    phone_number: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    # A simple SHA-256 hash for demonstration (use bcrypt in deep production!)
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/api/register")
def register_user(user: UserCreate, db: Session = Depends(get_postgres_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = models.User(
        full_name=user.full_name,
        phone_number=user.phone_number,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create default settings for user
    default_settings = models.UserSettings(user_id=new_user.id)
    db.add(default_settings)
    db.commit()

    return {"message": "User registered successfully", "user_id": new_user.id}

@app.get("/api/users")
def get_all_users(db: Session = Depends(get_postgres_db)):
    """Admin endpoint to see all registered users."""
    users = db.query(models.User).all()
    # We return everything EXCEPT the password_hash for security, 
    # but since you are the admin, we can show the hash to prove it's encrypted!
    return [{"id": u.id, "name": u.full_name, "email": u.email, "phone": u.phone_number, "password_hash": u.password_hash} for u in users]

@app.post("/api/login")
def login_user(user: UserLogin, db: Session = Depends(get_postgres_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if db_user.password_hash != hash_password(user.password):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "full_name": db_user.full_name,
        "email": db_user.email
    }
