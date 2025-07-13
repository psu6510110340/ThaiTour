from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlmodel import Session, select
from thaitour.schemas.registration_schema import (
    RegistrationCreate, 
    RegistrationUpdate, 
    RegistrationResponse, 
    RegistrationStatusUpdate
)
from thaitour.models.registration_model import Registration
from thaitour.models.user_model import User, UserRole
from thaitour.models import get_session
from thaitour.core.deps import get_current_user, require_admin, require_admin_or_moderator
from thaitour.core.security import get_password_hash
import json
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(
    registration: RegistrationCreate,
    session: Session = Depends(get_session)
):
    """
    สร้างการลงทะเบียนใหม่สำหรับระบบท่องเที่ยวคนละครึ่ง
    พร้อมสร้าง User Account สำหรับเข้าสู่ระบบ
    """
    # ตรวจสอบว่าเลขบัตรประชาชนซ้ำหรือไม่
    existing_citizen = session.exec(
        select(Registration).where(Registration.citizen_id == registration.citizen_id)
    ).first()
    
    if existing_citizen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="เลขบัตรประชาชนนี้ได้ลงทะเบียนแล้ว"
        )
    
    # ตรวจสอบว่าอีเมลซ้ำหรือไม่ (ทั้งใน Registration และ User table)
    existing_email_registration = session.exec(
        select(Registration).where(Registration.email == registration.email)
    ).first()
    
    existing_email_user = session.exec(
        select(User).where(User.email == registration.email)
    ).first()
    
    if existing_email_registration or existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="อีเมลนี้ได้ลงทะเบียนแล้ว"
        )
    
    # สร้าง User Account ก่อน
    username = registration.email  # ใช้อีเมลเป็น username
    full_name = f"{registration.first_name} {registration.last_name}"
    
    new_user = User(
        username=username,
        hashed_password=get_password_hash(registration.password),
        email=registration.email,
        full_name=full_name,
        role=UserRole.USER,  # กำหนดเป็น USER role
        is_active=True,
        is_verified=True  # อนุมัติอัตโนมัติ
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # สร้างข้อมูลการลงทะเบียนใหม่
    db_registration = Registration(
        user_id=new_user.id,  # เชื่อมกับ User Account
        citizen_id=registration.citizen_id,
        first_name=registration.first_name,
        last_name=registration.last_name,
        email=registration.email,
        phone=registration.phone,
        date_of_birth=registration.date_of_birth,
        address=registration.address,
        province=registration.province,
        district=registration.district,
        sub_district=registration.sub_district,
        postal_code=registration.postal_code,
        target_provinces=json.dumps(registration.target_provinces, ensure_ascii=False),
        interests=json.dumps(registration.interests, ensure_ascii=False) if registration.interests else None
    )
    
    session.add(db_registration)
    session.commit()
    session.refresh(db_registration)
    
    # Convert back for response
    response_data = db_registration.model_dump()
    response_data["target_provinces"] = json.loads(db_registration.target_provinces)
    response_data["interests"] = json.loads(db_registration.interests) if db_registration.interests else None
    
    return RegistrationResponse(**response_data)

@router.get("/", response_model=List[RegistrationResponse])
async def get_registrations(
    skip: int = 0, 
    limit: int = 100,
    current_admin: User = Depends(require_admin_or_moderator),
    session: Session = Depends(get_session)
):
    """
    ดูรายการการลงทะเบียนทั้งหมด (สำหรับ Admin/Moderator เท่านั้น)
    """
    registrations = session.exec(
        select(Registration).offset(skip).limit(limit)
    ).all()
    
    result = []
    for reg in registrations:
        reg_data = reg.model_dump()
        reg_data["target_provinces"] = json.loads(reg.target_provinces)
        reg_data["interests"] = json.loads(reg.interests) if reg.interests else None
        result.append(RegistrationResponse(**reg_data))
    
    return result

@router.get("/{registration_id}", response_model=RegistrationResponse)
async def get_registration(
    registration_id: int,
    session: Session = Depends(get_session)
):
    """
    ดูข้อมูลการลงทะเบียนตาม ID
    """
    registration = session.get(Registration, registration_id)
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลการลงทะเบียน"
        )
    
    reg_data = registration.model_dump()
    reg_data["target_provinces"] = json.loads(registration.target_provinces)
    reg_data["interests"] = json.loads(registration.interests) if registration.interests else None
    
    return RegistrationResponse(**reg_data)

@router.get("/citizen/{citizen_id}", response_model=RegistrationResponse)
async def get_registration_by_citizen_id(
    citizen_id: str,
    session: Session = Depends(get_session)
):
    """
    ดูข้อมูลการลงทะเบียนตามเลขบัตรประชาชน
    """
    registration = session.exec(
        select(Registration).where(Registration.citizen_id == citizen_id)
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลการลงทะเบียนสำหรับเลขบัตรประชาชนนี้"
        )
    
    reg_data = registration.model_dump()
    reg_data["target_provinces"] = json.loads(registration.target_provinces)
    reg_data["interests"] = json.loads(registration.interests) if registration.interests else None
    
    return RegistrationResponse(**reg_data)

@router.put("/{registration_id}", response_model=RegistrationResponse)
async def update_registration(
    registration_id: int, 
    registration_update: RegistrationUpdate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    แก้ไขข้อมูลการลงทะเบียน
    """
    registration = session.get(Registration, registration_id)
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลการลงทะเบียน"
        )
    
    update_data = registration_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            if field == "target_provinces":
                setattr(registration, field, json.dumps(value, ensure_ascii=False))
            elif field == "interests":
                setattr(registration, field, json.dumps(value, ensure_ascii=False) if value else None)
            else:
                setattr(registration, field, value)
    
    registration.updated_at = datetime.utcnow()
    
    session.add(registration)
    session.commit()
    session.refresh(registration)
    
    reg_data = registration.model_dump()
    reg_data["target_provinces"] = json.loads(registration.target_provinces)
    reg_data["interests"] = json.loads(registration.interests) if registration.interests else None
    
    return RegistrationResponse(**reg_data)

@router.patch("/{registration_id}/status", response_model=RegistrationResponse)
async def update_registration_status(
    registration_id: int,
    status_update: RegistrationStatusUpdate,
    current_admin: User = Depends(require_admin_or_moderator),
    session: Session = Depends(get_session)
):
    """
    อัปเดตสถานะการลงทะเบียน (สำหรับ Admin/Moderator เท่านั้น)
    """
    registration = session.get(Registration, registration_id)
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลการลงทะเบียน"
        )
    
    registration.status = status_update.status
    
    if status_update.status.value == "approved":
        registration.approved_date = datetime.utcnow()
        registration.approved_by = status_update.approved_by or current_admin.username
    
    registration.updated_at = datetime.utcnow()
    
    session.add(registration)
    session.commit()
    session.refresh(registration)
    
    reg_data = registration.model_dump()
    reg_data["target_provinces"] = json.loads(registration.target_provinces)
    reg_data["interests"] = json.loads(registration.interests) if registration.interests else None
    
    return RegistrationResponse(**reg_data)

@router.delete("/{registration_id}")
async def delete_registration(
    registration_id: int,
    current_admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    ลบการลงทะเบียน (สำหรับ Admin เท่านั้น)
    """
    registration = session.get(Registration, registration_id)
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลการลงทะเบียน"
        )
    
    session.delete(registration)
    session.commit()
    
    return {"message": "ลบข้อมูลการลงทะเบียนเรียบร้อยแล้ว"}
