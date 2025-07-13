from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlmodel import Session, select
from thaitour.schemas.province_schema import (
    ProvinceCreate, 
    ProvinceUpdate, 
    ProvinceResponse, 
    ProvinceTaxInfo,
    ProvinceType
)
from thaitour.models.province_model import Province
from thaitour.models.user_model import User
from thaitour.models import get_session
from thaitour.core.deps import get_current_user, require_admin, require_admin_or_moderator
from datetime import datetime
import json

router = APIRouter()

@router.post("/", response_model=ProvinceResponse, status_code=status.HTTP_201_CREATED)
async def create_province(
    province: ProvinceCreate,
    current_admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    เพิ่มจังหวัดใหม่ (สำหรับ Admin เท่านั้น)
    """
    # ตรวจสอบว่าชื่อจังหวัดซ้ำหรือไม่
    existing_province = session.exec(
        select(Province).where(
            (Province.name_th == province.name_th) | 
            (Province.code == province.code)
        )
    ).first()
    
    if existing_province:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ชื่อจังหวัดหรือรหัสจังหวัดนี้มีอยู่แล้ว"
        )
    
    # แปลง list เป็น JSON string
    famous_attractions_json = json.dumps(province.famous_attractions, ensure_ascii=False) if province.famous_attractions else None
    local_specialties_json = json.dumps(province.local_specialties, ensure_ascii=False) if province.local_specialties else None
    
    db_province = Province(
        name_th=province.name_th,
        name_en=province.name_en,
        code=province.code,
        province_type=province.province_type,
        region=province.region,
        description=province.description,
        famous_attractions=famous_attractions_json,
        local_specialties=local_specialties_json,
        tax_reduction_percentage=province.tax_reduction_percentage,
        max_reduction_amount=province.max_reduction_amount,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    session.add(db_province)
    session.commit()
    session.refresh(db_province)
    
    # แปลง JSON string กลับเป็น list สำหรับ response
    response_data = db_province.model_dump()
    if db_province.famous_attractions:
        response_data["famous_attractions"] = json.loads(db_province.famous_attractions)
    if db_province.local_specialties:
        response_data["local_specialties"] = json.loads(db_province.local_specialties)
    
    return ProvinceResponse(**response_data)

@router.get("/", response_model=List[ProvinceResponse])
async def get_provinces(
    skip: int = 0,
    limit: int = 100,
    province_type: Optional[ProvinceType] = Query(None, description="ประเภทจังหวัด"),
    region: Optional[str] = Query(None, description="ภาค"),
    is_active: Optional[bool] = Query(True, description="สถานะ"),
    session: Session = Depends(get_session)
):
    """
    ดูรายการจังหวัดทั้งหมด
    """
    statement = select(Province)
    
    # Filter by province_type
    if province_type:
        statement = statement.where(Province.province_type == province_type)
    
    # Filter by region
    if region:
        statement = statement.where(Province.region == region)
    
    # Filter by is_active
    if is_active is not None:
        statement = statement.where(Province.is_active == is_active)
    
    # Add pagination
    statement = statement.offset(skip).limit(limit)
    
    provinces = session.exec(statement).all()
    
    # แปลง JSON string กลับเป็น list สำหรับ response
    result = []
    for province in provinces:
        province_data = province.model_dump()
        if province.famous_attractions:
            province_data["famous_attractions"] = json.loads(province.famous_attractions)
        if province.local_specialties:
            province_data["local_specialties"] = json.loads(province.local_specialties)
        result.append(ProvinceResponse(**province_data))
    
    return result

@router.get("/secondary", response_model=List[ProvinceTaxInfo])
async def get_secondary_provinces(session: Session = Depends(get_session)):
    """
    ดูรายการจังหวัดรองที่มีสิทธิลดหย่อนภาษี
    """
    secondary_provinces = session.exec(
        select(Province).where(
            (Province.province_type == ProvinceType.SECONDARY) & 
            (Province.is_active == True)
        )
    ).all()
    
    result = []
    for province in secondary_provinces:
        result.append(ProvinceTaxInfo(
            province_id=province.id,
            name_th=province.name_th,
            name_en=province.name_en,
            province_type=province.province_type,
            tax_reduction_percentage=province.tax_reduction_percentage,
            max_reduction_amount=province.max_reduction_amount,
            is_secondary_province=True
        ))
    
    return result

@router.get("/{province_id}", response_model=ProvinceResponse)
async def get_province(province_id: int, session: Session = Depends(get_session)):
    """
    ดูข้อมูลจังหวัดตาม ID
    """
    province = session.get(Province, province_id)
    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลจังหวัด"
        )
    
    # แปลง JSON string กลับเป็น list สำหรับ response
    province_data = province.model_dump()
    if province.famous_attractions:
        province_data["famous_attractions"] = json.loads(province.famous_attractions)
    if province.local_specialties:
        province_data["local_specialties"] = json.loads(province.local_specialties)
    
    return ProvinceResponse(**province_data)

@router.get("/{province_id}/tax-info", response_model=ProvinceTaxInfo)
async def get_province_tax_info(province_id: int, session: Session = Depends(get_session)):
    """
    ดูข้อมูลลดหย่อนภาษีของจังหวัด
    """
    province = session.get(Province, province_id)
    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลจังหวัด"
        )
    
    return ProvinceTaxInfo(
        province_id=province.id,
        name_th=province.name_th,
        name_en=province.name_en,
        province_type=province.province_type,
        tax_reduction_percentage=province.tax_reduction_percentage,
        max_reduction_amount=province.max_reduction_amount,
        is_secondary_province=province.province_type == ProvinceType.SECONDARY
    )

@router.put("/{province_id}", response_model=ProvinceResponse)
async def update_province(
    province_id: int,
    province_update: ProvinceUpdate,
    current_admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    แก้ไขข้อมูลจังหวัด (สำหรับ Admin เท่านั้น)
    """
    province = session.get(Province, province_id)
    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลจังหวัด"
        )
    
    update_data = province_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            if field == "famous_attractions" and isinstance(value, list):
                setattr(province, field, json.dumps(value, ensure_ascii=False))
            elif field == "local_specialties" and isinstance(value, list):
                setattr(province, field, json.dumps(value, ensure_ascii=False))
            else:
                setattr(province, field, value)
    
    province.updated_at = datetime.utcnow()
    
    session.add(province)
    session.commit()
    session.refresh(province)
    
    # แปลง JSON string กลับเป็น list สำหรับ response
    province_data = province.model_dump()
    if province.famous_attractions:
        province_data["famous_attractions"] = json.loads(province.famous_attractions)
    if province.local_specialties:
        province_data["local_specialties"] = json.loads(province.local_specialties)
    
    return ProvinceResponse(**province_data)

@router.delete("/{province_id}")
async def delete_province(
    province_id: int,
    current_admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    ลบข้อมูลจังหวัด (สำหรับ Admin เท่านั้น)
    """
    province = session.get(Province, province_id)
    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลจังหวัด"
        )
    
    session.delete(province)
    session.commit()
    
    return {"message": "ลบข้อมูลจังหวัดเรียบร้อยแล้ว"}
