#!/usr/bin/env python3
"""
Database initialization script for ThaiTour
สร้างฐานข้อมูลและใส่ข้อมูลเริ่มต้น
"""

from thaitour.models import create_db_and_tables, get_session
from thaitour.models.province_model import Province, ProvinceType
from thaitour.models.tax_model import TaxBenefit, TaxBenefitType
from thaitour.models.user_model import User, UserRole
from thaitour.core.security import get_password_hash
from sqlmodel import select
from datetime import datetime

def init_database():
    """สร้างตารางฐานข้อมูล"""
    print("🗄️ สร้างตารางฐานข้อมูล...")
    create_db_and_tables()
    print("✅ สร้างตารางเรียบร้อย")

def seed_provinces():
    """ใส่ข้อมูลจังหวัดเริ่มต้น"""
    print("🌎 ใส่ข้อมูลจังหวัด...")
    
    provinces = [
        {
            "name_th": "กรุงเทพมหานคร",
            "name_en": "Bangkok", 
            "code": "BKK",
            "province_type": ProvinceType.PRIMARY,
            "region": "กลาง",
            "description": "เมืองหลวงของประเทศไทย ศูนย์กลางทางเศรษฐกิจและการปกครอง",
            "famous_attractions": '["วัดพระแก้ว", "วัดโพธิ์", "วัดอรุณ", "จตุจักร"]',
            "local_specialties": '["ข้าวผัดกุ้ง", "ต้มยำกุ้ง", "ผักบุ้งไฟแดง"]',
            "tax_reduction_percentage": 0.0,
            "max_reduction_amount": 0.0
        },
        {
            "name_th": "เชียงใหม่",
            "name_en": "Chiang Mai",
            "code": "CNX", 
            "province_type": ProvinceType.PRIMARY,
            "region": "เหนือ",
            "description": "เมืองศิลปวัฒนธรรมภาคเหนือ เป็นจุดหมายท่องเที่ยวที่สำคัญ",
            "famous_attractions": '["วัดพระธาตุดอยสุเทพ", "ถนนคนเดิน", "ไนท์บาซาร์"]',
            "local_specialties": '["ขนมจีนน้ำเงี้ยว", "ไส้อั่ว", "แกงฮังเล"]',
            "tax_reduction_percentage": 0.0,
            "max_reduction_amount": 0.0
        },
        {
            "name_th": "กาญจนบุรี",
            "name_en": "Kanchanaburi",
            "code": "KAN",
            "province_type": ProvinceType.SECONDARY,
            "region": "กลาง",
            "description": "จังหวัดรองที่มีประวัติศาสตร์และธรรมชาติที่สวยงาม",
            "famous_attractions": '["สะพานข้ามแม่น้ำแคว", "น้ำตกเอราวัณ", "อุทยานแห่งชาติไทรโยค"]',
            "local_specialties": '["ข้าวโพดคั่ว", "มะม่วงน้ำดอกไม้", "ขนมถั่วแปบ"]',
            "tax_reduction_percentage": 30.0,
            "max_reduction_amount": 15000.0
        },
        {
            "name_th": "เชียงราย",
            "name_en": "Chiang Rai",
            "code": "CRI",
            "province_type": ProvinceType.SECONDARY,
            "region": "เหนือ",
            "description": "จังหวัดรองภาคเหนือ มีสถานที่ท่องเที่ยวที่เป็นเอกลักษณ์",
            "famous_attractions": '["วัดร่องขุ่น", "บ้านดำ", "ไร่ชา"]',
            "local_specialties": '["ชาอู่หลง", "ข้าวต้มมัด", "ลาบปลาดิบ"]',
            "tax_reduction_percentage": 30.0,
            "max_reduction_amount": 15000.0
        },
        {
            "name_th": "ภูเก็ต",
            "name_en": "Phuket",
            "code": "HKT",
            "province_type": ProvinceType.PRIMARY,
            "region": "ใต้",
            "description": "เกาะท่องเที่ยวชื่อดังของไทย",
            "famous_attractions": '["หาดป่าตอง", "วัดชลองวรราม", "อ่าวพังงา"]',
            "local_specialties": '["หอยทอด", "ข้าวยำ", "ลูกชิ้นปลา"]',
            "tax_reduction_percentage": 0.0,
            "max_reduction_amount": 0.0
        }
    ]
    
    with next(get_session()) as session:
        # ตรวจสอบว่ามีข้อมูลแล้วหรือไม่
        existing_provinces = session.exec(select(Province)).all()
        if existing_provinces:
            print("ℹ️ ข้อมูลจังหวัดมีอยู่แล้ว ข้ามขั้นตอนนี้")
            return
            
        for prov_data in provinces:
            province = Province(**prov_data)
            session.add(province)
        session.commit()
    
    print(f"✅ ใส่ข้อมูลจังหวัด {len(provinces)} จังหวัดเรียบร้อย")

def seed_tax_benefits():
    """ใส่ข้อมูลสิทธิประโยชน์ลดหย่อนภาษี"""
    print("💰 ใส่ข้อมูลสิทธิประโยชน์ลดหย่อนภาษี...")
    
    tax_benefits = [
        {
            "benefit_name": "ลดหย่อนภาษีจังหวัดรองทั่วไป",
            "benefit_type": TaxBenefitType.SECONDARY_PROVINCE,
            "description": "ลดหย่อนภาษี 30% สำหรับการท่องเที่ยวในจังหวัดรอง",
            "reduction_percentage": 30.0,
            "max_reduction_amount": 15000.0,
            "min_spending_amount": 1000.0,
            "eligible_activities": '["ที่พัก", "อาหาร", "สถานที่ท่องเที่ยว", "กิจกรรม"]',
            "required_documents": '["ใบเสร็จ", "หลักฐานการเดินทาง"]',
            "start_date": datetime(2024, 1, 1),
            "end_date": datetime(2025, 12, 31),
            "is_active": True
        },
        {
            "benefit_name": "ลดหย่อนภาษีกาญจนบุรี",
            "benefit_type": TaxBenefitType.PROVINCE_SPECIFIC,
            "description": "ลดหย่อนภาษีเฉพาะการท่องเที่ยวในจังหวัดกาญจนบุรี",
            "province_id": 3,  # กาญจนบุรี
            "reduction_percentage": 30.0,
            "max_reduction_amount": 15000.0,
            "min_spending_amount": 500.0,
            "eligible_activities": '["ที่พัก", "อาหาร", "สถานที่ท่องเที่ยว"]',
            "required_documents": '["ใบเสร็จ", "หลักฐานการเดินทาง"]',
            "start_date": datetime(2024, 6, 1),
            "end_date": datetime(2025, 8, 31),
            "is_active": True
        }
    ]
    
    with next(get_session()) as session:
        for benefit_data in tax_benefits:
            benefit = TaxBenefit(**benefit_data)
            session.add(benefit)
        session.commit()
    
    print(f"✅ ใส่ข้อมูลสิทธิประโยชน์ {len(tax_benefits)} รายการเรียบร้อย")

def seed_users():
    """ใส่ข้อมูลผู้ใช้เริ่มต้น"""
    print("👥 ใส่ข้อมูลผู้ใช้...")
    
    users = [
        {
            "username": "admin",
            "hashed_password": get_password_hash("secret"),
            "email": "admin@thaitour.com",
            "full_name": "ผู้ดูแลระบบ",
            "role": UserRole.ADMIN,
            "is_active": True,
            "is_verified": True
        },
        {
            "username": "user",
            "hashed_password": get_password_hash("secret"),
            "email": "user@thaitour.com", 
            "full_name": "ผู้ใช้ทั่วไป",
            "role": UserRole.USER,
            "is_active": True,
            "is_verified": True
        }
    ]
    
    with next(get_session()) as session:
        for user_data in users:
            # ตรวจสอบว่ามี username นี้แล้วหรือไม่
            from sqlmodel import select
            existing_user = session.exec(
                select(User).where(User.username == user_data["username"])
            ).first()
            
            if not existing_user:
                user = User(**user_data)
                session.add(user)
            else:
                print(f"  - ข้าม: ผู้ใช้ {user_data['username']} มีอยู่แล้ว")
                
        session.commit()
    
    print(f"✅ ใส่ข้อมูลผู้ใช้ {len(users)} คนเรียบร้อย")

def main():
    """ฟังก์ชันหลักสำหรับเริ่มต้นฐานข้อมูล"""
    print("🚀 เริ่มต้นฐานข้อมูล ThaiTour...")
    
    # สร้างตาราง
    init_database()
    
    # ใส่ข้อมูลเริ่มต้น
    seed_provinces()
    seed_tax_benefits()
    seed_users()
    
    print("🎉 เริ่มต้นฐานข้อมูลเรียบร้อยแล้ว!")
    print("📁 ไฟล์ฐานข้อมูล: thaitour.db")

if __name__ == "__main__":
    main()
