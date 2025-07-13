from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class RegistrationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    SUSPENDED = "suspended"

class Registration(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Link to User Account
    user_id: Optional[int] = Field(foreign_key="user.id", description="ID ของ User Account ที่เชื่อมโยง")
    
    # Personal Information
    citizen_id: str = Field(index=True, unique=True, max_length=13)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(index=True, unique=True)
    phone: str = Field(max_length=20)
    date_of_birth: datetime
    
    # Address Information
    address: str = Field(max_length=500)
    province: str = Field(max_length=100, index=True)
    district: str = Field(max_length=100)
    sub_district: str = Field(max_length=100)
    postal_code: str = Field(max_length=10)
    
    # Registration Information
    status: RegistrationStatus = Field(default=RegistrationStatus.PENDING)
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    approved_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    
    # Travel Preferences
    target_provinces: str = Field(max_length=1000)  # JSON string of selected provinces
    interests: Optional[str] = Field(max_length=1000)  # JSON string of interests
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
