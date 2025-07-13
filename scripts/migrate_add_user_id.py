#!/usr/bin/env python3
"""
Migration script to add user_id field to registration table
และอัปเดตฐานข้อมูลเดิม
"""

import sqlite3
from thaitour.models import get_session
from thaitour.models.registration_model import Registration
from thaitour.models.user_model import User, UserRole
from thaitour.core.security import get_password_hash
from sqlmodel import select
import json

def migrate_database():
    """อัปเดตโครงสร้างฐานข้อมูล"""
    
    # ใช้ sqlite3 เพื่อเพิ่มคอลัมน์ใหม่
    try:
        conn = sqlite3.connect('thaitour.db')
        cursor = conn.cursor()
        
        # เพิ่มคอลัมน์ user_id ในตาราง registration
        cursor.execute('''
            ALTER TABLE registration 
            ADD COLUMN user_id INTEGER 
            REFERENCES user(id)
        ''')
        
        conn.commit()
        print("✅ เพิ่มคอลัมน์ user_id ในตาราง registration เรียบร้อย")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ คอลัมน์ user_id มีอยู่แล้ว ข้ามขั้นตอนนี้")
        else:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
    finally:
        conn.close()

def create_user_accounts_for_existing_registrations():
    """สร้าง User Account สำหรับ Registration ที่มีอยู่แล้ว"""
    
    with next(get_session()) as session:
        # หา Registration ที่ยังไม่มี User Account
        registrations_without_user = session.exec(
            select(Registration).where(Registration.user_id.is_(None))
        ).all()
        
        print(f"📋 พบ Registration ที่ยังไม่มี User Account: {len(registrations_without_user)} รายการ")
        
        for reg in registrations_without_user:
            try:
                # ตรวจสอบว่ามี User ที่ใช้อีเมลนี้แล้วหรือไม่
                existing_user = session.exec(
                    select(User).where(User.email == reg.email)
                ).first()
                
                if existing_user:
                    # เชื่อม Registration กับ User ที่มีอยู่
                    reg.user_id = existing_user.id
                    print(f"🔗 เชื่อม Registration ID {reg.id} กับ User ID {existing_user.id}")
                else:
                    # สร้าง User Account ใหม่
                    username = reg.email  # ใช้อีเมลเป็น username
                    full_name = f"{reg.first_name} {reg.last_name}"
                    default_password = "123456"  # รหัสผ่านเริ่มต้น (ให้ผู้ใช้เปลี่ยนภายหลัง)
                    
                    new_user = User(
                        username=username,
                        hashed_password=get_password_hash(default_password),
                        email=reg.email,
                        full_name=full_name,
                        role=UserRole.USER,
                        is_active=True,
                        is_verified=True
                    )
                    
                    session.add(new_user)
                    session.commit()
                    session.refresh(new_user)
                    
                    # เชื่อม Registration กับ User ใหม่
                    reg.user_id = new_user.id
                    print(f"👤 สร้าง User Account ใหม่ ID {new_user.id} สำหรับ Registration ID {reg.id}")
                    print(f"   - Email: {reg.email}")
                    print(f"   - รหัสผ่านเริ่มต้น: {default_password}")
                
                session.add(reg)
                
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดกับ Registration ID {reg.id}: {e}")
                continue
        
        session.commit()
        print("✅ อัปเดต Registration ทั้งหมดเรียบร้อย")

def main():
    """ฟังก์ชันหลักสำหรับ migration"""
    print("🚀 เริ่มต้น Migration: เพิ่ม User Account สำหรับ Registration")
    
    # 1. อัปเดตโครงสร้างฐานข้อมูล
    migrate_database()
    
    # 2. สร้าง User Account สำหรับ Registration ที่มีอยู่
    create_user_accounts_for_existing_registrations()
    
    print("🎉 Migration เสร็จสิ้น!")
    print("\n📋 สรุป:")
    print("- Registration ใหม่จะสร้าง User Account อัตโนมัติ")
    print("- Registration เก่าที่ไม่มี User Account จะใช้รหัสผ่านเริ่มต้น: 123456")
    print("- สามารถ login ด้วยอีเมลและรหัสผ่านได้แล้ว")

if __name__ == "__main__":
    main()
