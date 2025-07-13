from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TaxBenefitType(str, Enum):
    PROVINCE_SPECIFIC = "province_specific"  # ลดหย่อนเฉพาะจังหวัด
    SECONDARY_PROVINCE = "secondary_province"  # ลดหย่อนจังหวัดรอง
    ACTIVITY_BASED = "activity_based"  # ลดหย่อนตามกิจกรรม

class TaxBenefit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Benefit Information
    benefit_name: str = Field(max_length=200)
    benefit_type: TaxBenefitType = Field(index=True)
    description: str = Field(max_length=1000)
    
    # Province Information
    province_id: Optional[int] = Field(foreign_key="province.id")
    applicable_provinces: Optional[str] = Field(max_length=1000)  # JSON list of province IDs
    
    # Financial Information
    reduction_percentage: float = Field(default=0.0)  # เปอร์เซ็นต์ลดหย่อน
    max_reduction_amount: float = Field(default=0.0)  # จำนวนเงินลดหย่อนสูงสุด
    min_spending_amount: float = Field(default=0.0)   # จำนวนเงินใช้จ่ายขั้นต่ำ
    
    # Eligibility Criteria
    eligible_activities: Optional[str] = Field(max_length=1000)  # JSON list
    required_documents: Optional[str] = Field(max_length=1000)   # JSON list
    
    # Validity Period
    start_date: datetime
    end_date: datetime
    
    # Status
    is_active: bool = Field(default=True)
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
