from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# SQLite Engine (For Furniture Catalog)
SQLITE_DATABASE_URL = "sqlite:///./furniture.db"
engine_sqlite = create_engine(SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_sqlite)

# PostgreSQL Engine (For Saved Designs)
# Swap 'postgres://' with 'postgresql://' just in case, and use psycopg2
POSTGRES_URL = "postgresql+psycopg2://roomify_designs_db_user:Li3Gy94sj2U5NjODLU0ZgzplebjB1pxq@dpg-d8b9br9akrks73dg7pfg-a/roomify_designs_db"

# NOTE: Render Internal URLs don't work from our local machine!
# Wait, dpg-... is the Internal URL. Let's try it. If it fails locally, it will still work on Render!
engine_postgres = create_engine(POSTGRES_URL)
PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_postgres)

Base = declarative_base()
