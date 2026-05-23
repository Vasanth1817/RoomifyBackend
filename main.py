from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import models
from database import SessionLocal, engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Roomify Backend API")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
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
    return {"message": "Welcome to Roomify API"}

@app.get("/furniture", response_model=List[FurnitureResponse])
def get_furniture(db: Session = Depends(get_db)):
    """Fetch all furniture items from the database."""
    items = db.query(models.Furniture).all()
    return items

@app.post("/furniture", response_model=FurnitureResponse)
def add_furniture(furniture: FurnitureCreate, db: Session = Depends(get_db)):
    """Add a new furniture item to the database."""
    db_furniture = models.Furniture(**furniture.model_dump())
    db.add(db_furniture)
    db.commit()
    db.refresh(db_furniture)
    return db_furniture
