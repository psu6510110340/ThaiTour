import pytest
from fastapi.testclient import TestClient
from thaitour.main import app

client = TestClient(app)

def test_create_registration():
    """ทดสอบการสร้างการลงทะเบียนใหม่พร้อม User Account"""
    import random
    citizen_id = f"{random.randint(1000000000000, 9999999999999)}"
    email = f"somchai{random.randint(1000, 9999)}@example.com"
    
    registration_data = {
        "citizen_id": citizen_id,
        "first_name": "สมชาย",
        "last_name": "ใจดี",
        "email": email,
        "phone": "0812345678",
        "date_of_birth": "1990-01-01T00:00:00",
        "password": "mypassword123",  # เพิ่ม password
        "address": "123 ถนนสุขุมวิท",
        "province": "กรุงเทพมหานคร",
        "district": "วัฒนา",
        "sub_district": "ลุมพินี",
        "postal_code": "10330",
        "target_provinces": ["เชียงใหม่", "กาญจนบุรี"],
        "interests": ["ธรรมชาติ", "วัฒนธรรม"]
    }
    
    response = client.post("/api/v1/registration/", json=registration_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["citizen_id"] == citizen_id
    assert data["first_name"] == "สมชาย"
    assert data["status"] == "pending"
    assert data["user_id"] is not None  # ตรวจสอบว่ามี user_id

def test_get_registration_by_citizen_id():
    """ทดสอบการดึงข้อมูลการลงทะเบียนตามเลขบัตรประชาชน"""
    import random
    citizen_id = f"{random.randint(1000000000000, 9999999999999)}"
    email = f"somying{random.randint(1000, 9999)}@example.com"
    
    # สร้างการลงทะเบียนก่อน
    registration_data = {
        "citizen_id": citizen_id,
        "first_name": "สมหญิง",
        "last_name": "ใจงาม",
        "email": email,
        "phone": "0887654321",
        "date_of_birth": "1985-05-15T00:00:00",
        "password": "securepass456",  # เพิ่ม password
        "address": "456 ถนนพระราม 4",
        "province": "กรุงเทพมหานคร",
        "district": "ปทุมวัน",
        "sub_district": "ปทุมวัน",
        "postal_code": "10330",
        "target_provinces": ["เชียงราย", "สุราษฎร์ธานี"],
        "interests": ["อาหาร", "ช้อปปิ้ง"]
    }
    
    create_response = client.post("/api/v1/registration/", json=registration_data)
    assert create_response.status_code == 201
    
    # ทดสอบดึงข้อมูล
    response = client.get(f"/api/v1/registration/citizen/{citizen_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["citizen_id"] == citizen_id
    assert data["first_name"] == "สมหญิง"

def test_duplicate_citizen_id():
    """ทดสอบการป้องกันเลขบัตรประชาชนซ้ำ"""
    import random
    citizen_id = f"{random.randint(1000000000000, 9999999999999)}"
    email1 = f"test1_{random.randint(1000, 9999)}@example.com"
    email2 = f"test2_{random.randint(1000, 9999)}@example.com"
    
    registration_data = {
        "citizen_id": citizen_id,
        "first_name": "ทดสอบ",
        "last_name": "ซ้ำ",
        "email": email1,
        "phone": "0811111111",
        "date_of_birth": "1990-01-01T00:00:00",
        "password": "testpass123",  # เพิ่ม password
        "address": "123 ถนนทดสอบ",
        "province": "กรุงเทพมหานคร",
        "district": "ทดสอบ",
        "sub_district": "ทดสอบ",
        "postal_code": "10000",
        "target_provinces": ["เชียงใหม่"],
        "interests": ["ทดสอบ"]
    }
    
    # สร้างครั้งแรก - ควรสำเร็จ
    response1 = client.post("/api/v1/registration/", json=registration_data)
    assert response1.status_code == 201
    
    # สร้างครั้งที่สอง - ควรล้มเหลว
    registration_data["email"] = email2  # เปลี่ยนอีเมลเพื่อไม่ให้ซ้ำ
    registration_data["password"] = "testpass456"     # เปลี่ยน password ด้วย
    response2 = client.post("/api/v1/registration/", json=registration_data)
    assert response2.status_code == 400
    assert "เลขบัตรประชาชนนี้ได้ลงทะเบียนแล้ว" in response2.json()["detail"]

def test_invalid_citizen_id():
    """ทดสอบเลขบัตรประชาชนที่ไม่ถูกต้อง"""
    registration_data = {
        "citizen_id": "123",  # เลขบัตรประชาชนไม่ครบ 13 หลัก
        "first_name": "ทดสอบ",
        "last_name": "ผิด",
        "email": "invalid@example.com",
        "phone": "0811111111",
        "date_of_birth": "1990-01-01T00:00:00",
        "password": "invalidpass",  # เพิ่ม password
        "address": "123 ถนนทดสอบ",
        "province": "กรุงเทพมหานคร",
        "district": "ทดสอบ",
        "sub_district": "ทดสอบ",
        "postal_code": "10000",
        "target_provinces": ["เชียงใหม่"],
        "interests": ["ทดสอบ"]
    }
    
    response = client.post("/api/v1/registration/", json=registration_data)
    assert response.status_code == 422  # Validation error

def test_login_after_registration():
    """ทดสอบการ login หลังจากลงทะเบียน"""
    import random
    # ลงทะเบียนก่อน - ใช้ random citizen_id เพื่อไม่ให้ซ้ำ
    citizen_id = f"{random.randint(1000000000000, 9999999999999)}"
    email = f"logintest{random.randint(1000, 9999)}@example.com"
    
    registration_data = {
        "citizen_id": citizen_id,
        "first_name": "ทดสอบ",
        "last_name": "เข้าสู่ระบบ",
        "email": email,
        "phone": "0855555555",
        "date_of_birth": "1995-03-15T00:00:00",
        "password": "loginpass123",
        "address": "789 ถนนทดสอบ",
        "province": "กรุงเทพมหานคร",
        "district": "ทดสอบ",
        "sub_district": "ทดสอบ",
        "postal_code": "10000",
        "target_provinces": ["กาญจนบุรี"],
        "interests": ["ทดสอบ"]
    }
    
    # สร้างการลงทะเบียน
    registration_response = client.post("/api/v1/registration/", json=registration_data)
    if registration_response.status_code != 201:
        print(f"Error: {registration_response.json()}")
    assert registration_response.status_code == 201
    
    # ทดสอบ login ด้วยอีเมลและรหัสผ่านที่สร้างไว้
    login_data = {
        "username": email,  # ใช้อีเมลเป็น username
        "password": "loginpass123"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    login_result = login_response.json()
    assert "access_token" in login_result
    assert login_result["token_type"] == "bearer"
