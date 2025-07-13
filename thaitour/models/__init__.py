from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./thaitour.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """สร้างตารางฐานข้อมูลทั้งหมด"""
    # Import models เพื่อให้ SQLModel รู้จักตาราง
    from thaitour.models.province_model import Province
    from thaitour.models.registration_model import Registration
    from thaitour.models.tax_model import TaxBenefit
    from thaitour.models.user_model import User
    
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """สร้าง database session"""
    with Session(engine) as session:
        yield session
