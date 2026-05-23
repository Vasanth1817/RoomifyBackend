from sqlalchemy import Column, Integer, String
from database import Base

class Furniture(Base):
    __tablename__ = "furniture"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(String)
    model_url = Column(String)
    thumbnail_url = Column(String)
    category = Column(String, index=True)
