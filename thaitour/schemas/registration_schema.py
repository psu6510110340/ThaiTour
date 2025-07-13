from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RegistrationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    SUSPENDED = "suspended"

class RegistrationCreate(BaseModel):
    # Personal Information
    citizen_id: str = Field(..., min_length=13, max_length=13, description="เลขบัตรประชาชน 13 หลัก")
    first_name: str = Field(..., min_length=1, max_length=100, description="ชื่อ")
    last_name: str = Field(..., min_length=1, max_length=100, description="นามสกุล")
    email: EmailStr = Field(..., description="อีเมล")
    phone: str = Field(..., max_length=20, description="เบอร์โทรศัพท์")
    date_of_birth: datetime = Field(..., description="วันเกิด")
    
    # Authentication Information
    password: str = Field(..., min_length=6, max_length=50, description="รหัสผ่าน (อย่างน้อย 6 ตัวอักษร)")
    
    # Address Information
    address: str = Field(..., max_length=500, description="ที่อยู่")
    province: str = Field(..., max_length=100, description="จังหวัด")
    district: str = Field(..., max_length=100, description="อำเภอ")
    sub_district: str = Field(..., max_length=100, description="ตำบล")
    postal_code: str = Field(..., max_length=10, description="รหัสไปรษณีย์")
    
    # Travel Preferences
    target_provinces: List[str] = Field(..., description="จังหวัดที่ต้องการเที่ยว")
    interests: Optional[List[str]] = Field(None, description="ความสนใจ")

class RegistrationUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    sub_district: Optional[str] = None
    postal_code: Optional[str] = None
    target_provinces: Optional[List[str]] = None
    interests: Optional[List[str]] = None

class RegistrationResponse(BaseModel):
    id: int
    user_id: Optional[int]  # เพิ่ม field นี้
    citizen_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: datetime
    address: str
    province: str
    district: str
    sub_district: str
    postal_code: str
    status: RegistrationStatus
    registration_date: datetime
    approved_date: Optional[datetime]
    target_provinces: List[str]
    interests: Optional[List[str]]
    created_at: datetime

class RegistrationStatusUpdate(BaseModel):
    status: RegistrationStatus
    approved_by: Optional[str] = None
    notes: Optional[str] = None
