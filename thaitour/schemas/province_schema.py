from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProvinceType(str, Enum):
    PRIMARY = "primary"      # จังหวัดหลัก
    SECONDARY = "secondary"  # จังหวัดรอง (ได้สิทธิลดหย่อน)

class ProvinceCreate(BaseModel):
    name_th: str = Field(..., max_length=100, description="ชื่อจังหวัด (ไทย)")
    name_en: str = Field(..., max_length=100, description="ชื่อจังหวัด (อังกฤษ)")
    code: str = Field(..., max_length=10, description="รหัสจังหวัด")
    province_type: ProvinceType = Field(..., description="ประเภทจังหวัด")
    region: str = Field(..., max_length=50, description="ภาค")
    description: Optional[str] = Field(None, max_length=2000, description="คำอธิบาย")
    famous_attractions: Optional[List[str]] = Field(None, description="สถานที่ท่องเที่ยวที่มีชื่อเสียง")
    local_specialties: Optional[List[str]] = Field(None, description="ของฝากท้องถิ่น")
    tax_reduction_percentage: float = Field(0.0, ge=0, le=100, description="เปอร์เซ็นต์ลดหย่อน")
    max_reduction_amount: float = Field(0.0, ge=0, description="จำนวนเงินลดหย่อนสูงสุด")

class ProvinceUpdate(BaseModel):
    name_th: Optional[str] = None
    name_en: Optional[str] = None
    code: Optional[str] = None
    province_type: Optional[ProvinceType] = None
    region: Optional[str] = None
    description: Optional[str] = None
    famous_attractions: Optional[List[str]] = None
    local_specialties: Optional[List[str]] = None
    tax_reduction_percentage: Optional[float] = None
    max_reduction_amount: Optional[float] = None
    is_active: Optional[bool] = None

class ProvinceResponse(BaseModel):
    id: int
    name_th: str
    name_en: str
    code: str
    province_type: ProvinceType
    region: str
    description: Optional[str]
    famous_attractions: Optional[List[str]]
    local_specialties: Optional[List[str]]
    tax_reduction_percentage: float
    max_reduction_amount: float
    is_active: bool
    created_at: datetime

class ProvinceTaxInfo(BaseModel):
    """ข้อมูลลดหย่อนภาษีของจังหวัด"""
    province_id: int
    name_th: str
    name_en: str
    province_type: ProvinceType
    tax_reduction_percentage: float
    max_reduction_amount: float
    is_secondary_province: bool = False
