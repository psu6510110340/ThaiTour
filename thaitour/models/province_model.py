from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ProvinceType(str, Enum):
    PRIMARY = "primary"      # จังหวัดหลัก
    SECONDARY = "secondary"  # จังหวัดรอง (ได้สิทธิลดหย่อน)

class Province(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic Information
    name_th: str = Field(max_length=100, unique=True, index=True)
    name_en: str = Field(max_length=100, unique=True)
    code: str = Field(max_length=10, unique=True)
    
    # Classification
    province_type: ProvinceType = Field(index=True)
    region: str = Field(max_length=50, index=True)  # ภาค (เหนือ, ใต้, อีสาน, กลาง)
    
    # Tourism Information
    description: Optional[str] = Field(max_length=2000)
    famous_attractions: Optional[str] = Field(max_length=1000)  # JSON string
    local_specialties: Optional[str] = Field(max_length=1000)   # JSON string
    
    # Tax Reduction Information
    tax_reduction_percentage: float = Field(default=0.0)  # เปอร์เซ็นต์ลดหย่อน
    max_reduction_amount: float = Field(default=0.0)      # จำนวนเงินลดหย่อนสูงสุด
    
    # Status
    is_active: bool = Field(default=True)
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
