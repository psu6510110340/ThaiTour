from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlmodel import Session, select
from thaitour.schemas.tax_schema import (
    TaxBenefitCreate,
    TaxBenefitUpdate,
    TaxBenefitResponse,
    TaxCalculationRequest,
    TaxCalculationResponse,
    TaxBenefitType
)
from thaitour.models.tax_model import TaxBenefit
from thaitour.models.province_model import Province
from thaitour.models.user_model import User
from thaitour.models import get_session
from thaitour.core.deps import get_current_user, require_admin, require_admin_or_moderator
from datetime import datetime
import json

router = APIRouter()

@router.post("/benefits", response_model=TaxBenefitResponse, status_code=status.HTTP_201_CREATED)
async def create_tax_benefit(
    benefit: TaxBenefitCreate,
    current_admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    เพิ่มสิทธิประโยชน์ลดหย่อนภาษีใหม่ (สำหรับ Admin เท่านั้น)
    """
    # แปลง list เป็น JSON string
    applicable_provinces_json = json.dumps(benefit.applicable_provinces) if benefit.applicable_provinces else None
    eligible_activities_json = json.dumps(benefit.eligible_activities, ensure_ascii=False) if benefit.eligible_activities else None
    required_documents_json = json.dumps(benefit.required_documents, ensure_ascii=False) if benefit.required_documents else None
    
    db_benefit = TaxBenefit(
        benefit_name=benefit.benefit_name,
        benefit_type=benefit.benefit_type,
        description=benefit.description,
        province_id=benefit.province_id,
        applicable_provinces=applicable_provinces_json,
        reduction_percentage=benefit.reduction_percentage,
        max_reduction_amount=benefit.max_reduction_amount,
        min_spending_amount=benefit.min_spending_amount,
        eligible_activities=eligible_activities_json,
        required_documents=required_documents_json,
        start_date=benefit.start_date,
        end_date=benefit.end_date,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    session.add(db_benefit)
    session.commit()
    session.refresh(db_benefit)
    
    # แปลง JSON string กลับเป็น list สำหรับ response
    response_data = db_benefit.model_dump()
    if db_benefit.applicable_provinces:
        response_data["applicable_provinces"] = json.loads(db_benefit.applicable_provinces)
    if db_benefit.eligible_activities:
        response_data["eligible_activities"] = json.loads(db_benefit.eligible_activities)
    if db_benefit.required_documents:
        response_data["required_documents"] = json.loads(db_benefit.required_documents)
    
    return TaxBenefitResponse(**response_data)

@router.get("/benefits", response_model=List[TaxBenefitResponse])
async def get_tax_benefits(
    skip: int = 0,
    limit: int = 100,
    benefit_type: Optional[TaxBenefitType] = Query(None, description="ประเภทสิทธิประโยชน์"),
    province_id: Optional[int] = Query(None, description="ID จังหวัด"),
    is_active: Optional[bool] = Query(True, description="สถานะ"),
    session: Session = Depends(get_session)
):
    """
    ดูรายการสิทธิประโยชน์ลดหย่อนภาษี
    """
    statement = select(TaxBenefit)
    
    # Filter by benefit_type
    if benefit_type:
        statement = statement.where(TaxBenefit.benefit_type == benefit_type)
    
    # Filter by is_active
    if is_active is not None:
        statement = statement.where(TaxBenefit.is_active == is_active)
    
    # Filter by current date
    current_date = datetime.utcnow()
    statement = statement.where(
        (TaxBenefit.start_date <= current_date) & 
        (TaxBenefit.end_date >= current_date)
    )
    
    # Filter by province_id
    if province_id:
        # สิทธิประโยชน์ที่ใช้ได้กับจังหวัดนี้
        statement = statement.where(
            (TaxBenefit.province_id == province_id) |
            (TaxBenefit.applicable_provinces.contains(str(province_id)))
        )
    
    # Add pagination
    statement = statement.offset(skip).limit(limit)
    
    benefits = session.exec(statement).all()
    
    # แปลง JSON string กลับเป็น list สำหรับ response
    result = []
    for benefit in benefits:
        benefit_data = benefit.model_dump()
        if benefit.applicable_provinces:
            benefit_data["applicable_provinces"] = json.loads(benefit.applicable_provinces)
        if benefit.eligible_activities:
            benefit_data["eligible_activities"] = json.loads(benefit.eligible_activities)
        if benefit.required_documents:
            benefit_data["required_documents"] = json.loads(benefit.required_documents)
        result.append(TaxBenefitResponse(**benefit_data))
    
    return result

@router.get("/benefits/secondary-provinces", response_model=List[TaxBenefitResponse])
async def get_secondary_province_benefits(session: Session = Depends(get_session)):
    """
    ดูสิทธิประโยชน์ลดหย่อนภาษีสำหรับจังหวัดรองโดยเฉพาะ
    """
    current_date = datetime.utcnow()
    
    secondary_benefits = session.exec(
        select(TaxBenefit).where(
            (TaxBenefit.benefit_type == TaxBenefitType.SECONDARY_PROVINCE) &
            (TaxBenefit.is_active == True) &
            (TaxBenefit.start_date <= current_date) &
            (TaxBenefit.end_date >= current_date)
        )
    ).all()
    
    # แปลง JSON string กลับเป็น list สำหรับ response
    result = []
    for benefit in secondary_benefits:
        benefit_data = benefit.model_dump()
        if benefit.applicable_provinces:
            benefit_data["applicable_provinces"] = json.loads(benefit.applicable_provinces)
        if benefit.eligible_activities:
            benefit_data["eligible_activities"] = json.loads(benefit.eligible_activities)
        if benefit.required_documents:
            benefit_data["required_documents"] = json.loads(benefit.required_documents)
        result.append(TaxBenefitResponse(**benefit_data))
    
    return result

@router.get("/benefits/{benefit_id}", response_model=TaxBenefitResponse)
async def get_tax_benefit(benefit_id: int, session: Session = Depends(get_session)):
    """
    ดูข้อมูลสิทธิประโยชน์ลดหย่อนภาษีตาม ID
    """
    benefit = session.get(TaxBenefit, benefit_id)
    if not benefit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลสิทธิประโยชน์"
        )
    
    # แปลง JSON string กลับเป็น list สำหรับ response
    benefit_data = benefit.model_dump()
    if benefit.applicable_provinces:
        benefit_data["applicable_provinces"] = json.loads(benefit.applicable_provinces)
    if benefit.eligible_activities:
        benefit_data["eligible_activities"] = json.loads(benefit.eligible_activities)
    if benefit.required_documents:
        benefit_data["required_documents"] = json.loads(benefit.required_documents)
    
    return TaxBenefitResponse(**benefit_data)

@router.post("/calculate", response_model=TaxCalculationResponse)
async def calculate_tax_reduction(
    calculation: TaxCalculationRequest, 
    session: Session = Depends(get_session)
):
    """
    คำนวณลดหย่อนภาษีตามการใช้จ่ายและจังหวัดที่เที่ยว
    """
    # ตรวจสอบว่าจังหวัดมีอยู่หรือไม่
    province = session.get(Province, calculation.province_id)
    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลจังหวัด"
        )
    
    province_name = province.name_th
    is_secondary = province.province_type.value == "secondary"
    
    # หาสิทธิประโยชน์ที่เกี่ยวข้อง
    applicable_benefits = []
    total_reduction_percentage = 0.0
    max_reduction = 0.0
    
    current_date = datetime.utcnow()
    
    # ดึงสิทธิประโยชน์ที่เปิดใช้งานและยังไม่หมดอายุ
    benefits = session.exec(
        select(TaxBenefit).where(
            (TaxBenefit.is_active == True) &
            (TaxBenefit.start_date <= current_date) &
            (TaxBenefit.end_date >= current_date)
        )
    ).all()
    
    for benefit in benefits:
        # ตรวจสอบว่าจังหวัดมีสิทธิ์หรือไม่
        is_applicable = False
        
        if benefit.province_id == calculation.province_id:
            is_applicable = True
        elif benefit.applicable_provinces:
            applicable_provinces_list = json.loads(benefit.applicable_provinces)
            if calculation.province_id in applicable_provinces_list:
                is_applicable = True
        elif benefit.benefit_type == TaxBenefitType.SECONDARY_PROVINCE and is_secondary:
            is_applicable = True
        
        if is_applicable and calculation.spending_amount >= benefit.min_spending_amount:
            applicable_benefits.append(benefit.benefit_name)
            total_reduction_percentage = max(total_reduction_percentage, benefit.reduction_percentage)
            max_reduction = max(max_reduction, benefit.max_reduction_amount)
    
    # คำนวณลดหย่อน
    calculated_reduction = calculation.spending_amount * (total_reduction_percentage / 100)
    final_reduction = min(calculated_reduction, max_reduction)
    
    return TaxCalculationResponse(
        citizen_id=calculation.citizen_id,
        province_name=province_name,
        spending_amount=calculation.spending_amount,
        eligible_reduction_percentage=total_reduction_percentage,
        calculated_reduction=calculated_reduction,
        max_reduction_amount=max_reduction,
        final_reduction_amount=final_reduction,
        is_secondary_province_benefit=is_secondary,
        applicable_benefits=applicable_benefits
    )

@router.put("/benefits/{benefit_id}", response_model=TaxBenefitResponse)
async def update_tax_benefit(
    benefit_id: int,
    benefit_update: TaxBenefitUpdate,
    current_admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    แก้ไขสิทธิประโยชน์ลดหย่อนภาษี (สำหรับ Admin เท่านั้น)
    """
    benefit = session.get(TaxBenefit, benefit_id)
    if not benefit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลสิทธิประโยชน์"
        )
    
    update_data = benefit_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            if field == "applicable_provinces" and isinstance(value, list):
                setattr(benefit, field, json.dumps(value))
            elif field == "eligible_activities" and isinstance(value, list):
                setattr(benefit, field, json.dumps(value, ensure_ascii=False))
            elif field == "required_documents" and isinstance(value, list):
                setattr(benefit, field, json.dumps(value, ensure_ascii=False))
            else:
                setattr(benefit, field, value)
    
    benefit.updated_at = datetime.utcnow()
    
    session.add(benefit)
    session.commit()
    session.refresh(benefit)
    
    # แปลง JSON string กลับเป็น list สำหรับ response
    benefit_data = benefit.model_dump()
    if benefit.applicable_provinces:
        benefit_data["applicable_provinces"] = json.loads(benefit.applicable_provinces)
    if benefit.eligible_activities:
        benefit_data["eligible_activities"] = json.loads(benefit.eligible_activities)
    if benefit.required_documents:
        benefit_data["required_documents"] = json.loads(benefit.required_documents)
    
    return TaxBenefitResponse(**benefit_data)
    
    return TaxBenefitResponse(**benefit)

@router.delete("/benefits/{benefit_id}")
async def delete_tax_benefit(
    benefit_id: int,
    current_admin: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    ลบสิทธิประโยชน์ลดหย่อนภาษี (สำหรับ Admin เท่านั้น)
    """
    benefit = session.get(TaxBenefit, benefit_id)
    if not benefit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลสิทธิประโยชน์"
        )
    
    session.delete(benefit)
    session.commit()
    
    return {"message": "ลบข้อมูลสิทธิประโยชน์เรียบร้อยแล้ว"}
