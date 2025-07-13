from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaxBenefitType(str, Enum):
    PROVINCE_SPECIFIC = "province_specific"  # ลดหย่อนเฉพาะจังหวัด
    SECONDARY_PROVINCE = "secondary_province"  # ลดหย่อนจังหวัดรอง
    ACTIVITY_BASED = "activity_based"  # ลดหย่อนตามกิจกรรม

class TaxBenefitCreate(BaseModel):
    benefit_name: str = Field(..., max_length=200, description="ชื่อสิทธิประโยชน์")
    benefit_type: TaxBenefitType = Field(..., description="ประเภทสิทธิประโยชน์")
    description: str = Field(..., max_length=1000, description="คำอธิบาย")
    province_id: Optional[int] = Field(None, description="ID จังหวัด (สำหรับสิทธิเฉพาะจังหวัด)")
    applicable_provinces: Optional[List[int]] = Field(None, description="จังหวัดที่ใช้ได้")
    reduction_percentage: float = Field(0.0, ge=0, le=100, description="เปอร์เซ็นต์ลดหย่อน")
    max_reduction_amount: float = Field(0.0, ge=0, description="จำนวนเงินลดหย่อนสูงสุด")
    min_spending_amount: float = Field(0.0, ge=0, description="จำนวนเงินใช้จ่ายขั้นต่ำ")
    eligible_activities: Optional[List[str]] = Field(None, description="กิจกรรมที่มีสิทธิ์")
    required_documents: Optional[List[str]] = Field(None, description="เอกสารที่ต้องใช้")
    start_date: datetime = Field(..., description="วันที่เริ่มต้น")
    end_date: datetime = Field(..., description="วันที่สิ้นสุด")

class TaxBenefitUpdate(BaseModel):
    benefit_name: Optional[str] = None
    benefit_type: Optional[TaxBenefitType] = None
    description: Optional[str] = None
    province_id: Optional[int] = None
    applicable_provinces: Optional[List[int]] = None
    reduction_percentage: Optional[float] = None
    max_reduction_amount: Optional[float] = None
    min_spending_amount: Optional[float] = None
    eligible_activities: Optional[List[str]] = None
    required_documents: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class TaxBenefitResponse(BaseModel):
    id: int
    benefit_name: str
    benefit_type: TaxBenefitType
    description: str
    province_id: Optional[int]
    applicable_provinces: Optional[List[int]]
    reduction_percentage: float
    max_reduction_amount: float
    min_spending_amount: float
    eligible_activities: Optional[List[str]]
    required_documents: Optional[List[str]]
    start_date: datetime
    end_date: datetime
    is_active: bool
    created_at: datetime

class TaxCalculationRequest(BaseModel):
    """คำขอคำนวณลดหย่อนภาษี"""
    citizen_id: str = Field(..., description="เลขบัตรประชาชน")
    province_id: int = Field(..., description="จังหวัดที่เที่ยว")
    spending_amount: float = Field(..., ge=0, description="จำนวนเงินที่ใช้จ่าย")
    activities: List[str] = Field(..., description="กิจกรรมที่ทำ")

class TaxCalculationResponse(BaseModel):
    """ผลการคำนวณลดหย่อนภาษี"""
    citizen_id: str
    province_name: str
    spending_amount: float
    eligible_reduction_percentage: float
    calculated_reduction: float
    max_reduction_amount: float
    final_reduction_amount: float
    is_secondary_province_benefit: bool
    applicable_benefits: List[str]
