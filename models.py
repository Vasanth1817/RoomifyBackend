from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    full_name = Column(String)
    phone_number = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    theme_preference = Column(String, default="SYSTEM")
    max_budget = Column(Float, default=15000.0)
class Furniture(Base):
    __tablename__ = "furniture"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(String)
    model_url = Column(String)
    thumbnail_url = Column(String)
    category = Column(String, index=True)

class SavedLayout(Base):
    __tablename__ = "saved_layouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True) # nullable for backwards compatibility
    name = Column(String, index=True, default="My Room Design")
    mode = Column(String, default="AR")
    json_data = Column(String) # Stores the raw JSON payload from Unity
    before_image = Column(String, nullable=True) # Base64 encoded screenshot when AR session starts
    after_image = Column(String, nullable=True) # Base64 encoded screenshot when saving
