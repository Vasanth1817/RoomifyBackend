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
from typing import Dict, Any

class LayoutData(BaseModel):
    items: List[Dict[str, Any]]

@app.post("/save_layout")
def save_layout(layout: LayoutData, db: Session = Depends(get_postgres_db)):
    """Save a room layout JSON from Unity to the database."""
    json_str = json.dumps({"items": layout.items})
    db_layout = models.SavedLayout(name="My Room Design", json_data=json_str)
    db.add(db_layout)
    db.commit()
    db.refresh(db_layout)
    return {"message": "Success", "id": db_layout.id}

@app.get("/get_layouts")
def get_layouts(db: Session = Depends(get_postgres_db)):
    """Fetch all saved layouts for the Android Home Screen."""
    layouts = db.query(models.SavedLayout).all()
    return layouts
