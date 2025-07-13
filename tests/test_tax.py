import pytest
from fastapi.testclient import TestClient
from thaitour.main import app

client = TestClient(app)

def test_get_all_tax_benefits():
    """ทดสอบการดึงข้อมูลสิทธิประโยชน์ลดหย่อนภาษีทั้งหมด"""
    response = client.get("/api/v1/tax/benefits")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_secondary_province_benefits():
    """ทดสอบการดึงสิทธิประโยชน์สำหรับจังหวัดรอง"""
    response = client.get("/api/v1/tax/benefits/secondary-provinces")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    for benefit in data:
        assert benefit["benefit_type"] == "secondary_province"
        assert benefit["is_active"] is True

def test_calculate_tax_reduction_secondary_province():
    """ทดสอบการคำนวณลดหย่อนภาษีสำหรับจังหวัดรอง"""
    calculation_data = {
        "citizen_id": "1234567890123",
        "province_id": 3,  # กาญจนบุรี (จังหวัดรอง)
        "spending_amount": 10000.0,
        "activities": ["ที่พัก", "อาหาร", "สถานที่ท่องเที่ยว"]
    }
    
    response = client.post("/api/v1/tax/calculate", json=calculation_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["citizen_id"] == "1234567890123"
    assert data["province_name"] == "กาญจนบุรี"
    assert data["spending_amount"] == 10000.0
    assert data["is_secondary_province_benefit"] is True
    assert data["eligible_reduction_percentage"] > 0
    assert data["final_reduction_amount"] > 0
    assert len(data["applicable_benefits"]) > 0

def test_calculate_tax_reduction_primary_province():
    """ทดสอบการคำนวณลดหย่อนภาษีสำหรับจังหวัดหลัก"""
    calculation_data = {
        "citizen_id": "1234567890123",
        "province_id": 1,  # กรุงเทพ (จังหวัดหลัก)
        "spending_amount": 10000.0,
        "activities": ["ที่พัก", "อาหาร"]
    }
    
    response = client.post("/api/v1/tax/calculate", json=calculation_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["citizen_id"] == "1234567890123"
    assert data["province_name"] == "กรุงเทพมหานคร"
    assert data["is_secondary_province_benefit"] is False
    # จังหวัดหลักไม่มีสิทธิลดหย่อน
    assert data["eligible_reduction_percentage"] == 0.0
    assert data["final_reduction_amount"] == 0.0

def test_calculate_tax_reduction_with_max_limit():
    """ทดสอบการคำนวณลดหย่อนภาษีที่เกินขีดจำกัด"""
    calculation_data = {
        "citizen_id": "1234567890123",
        "province_id": 3,  # กาญจนบุรี
        "spending_amount": 100000.0,  # จำนวนเงินมาก
        "activities": ["ที่พัก", "อาหาร", "สถานที่ท่องเที่ยว"]
    }
    
    response = client.post("/api/v1/tax/calculate", json=calculation_data)
    assert response.status_code == 200
    
    data = response.json()
    # ตรวจสอบว่าลดหย่อนไม่เกินขีดจำกัด
    assert data["final_reduction_amount"] <= data["max_reduction_amount"]

def test_calculate_tax_reduction_insufficient_spending():
    """ทดสอบการคำนวณลดหย่อนภาษีกับการใช้จ่ายที่ไม่ถึงขั้นต่ำ"""
    calculation_data = {
        "citizen_id": "1234567890123",
        "province_id": 3,  # กาญจนบุรี
        "spending_amount": 500.0,  # น้อยกว่าขั้นต่ำ
        "activities": ["อาหาร"]
    }
    
    response = client.post("/api/v1/tax/calculate", json=calculation_data)
    assert response.status_code == 200
    
    data = response.json()
    # อาจไม่มีสิทธิลดหย่อนเพราะใช้จ่ายน้อยเกินไป
    assert data["final_reduction_amount"] >= 0

def test_calculate_tax_reduction_invalid_province():
    """ทดสอบการคำนวณลดหย่อนภาษีกับจังหวัดที่ไม่มีอยู่"""
    calculation_data = {
        "citizen_id": "1234567890123",
        "province_id": 999,  # จังหวัดที่ไม่มีอยู่
        "spending_amount": 10000.0,
        "activities": ["ที่พัก"]
    }
    
    response = client.post("/api/v1/tax/calculate", json=calculation_data)
    assert response.status_code == 404
    assert "ไม่พบข้อมูลจังหวัด" in response.json()["detail"]

def test_filter_benefits_by_province():
    """ทดสอบการกรองสิทธิประโยชน์ตามจังหวัด"""
    response = client.get("/api/v1/tax/benefits?province_id=3")
    assert response.status_code == 200
    
    data = response.json()
    # ควรมีสิทธิประโยชน์ที่เกี่ยวข้องกับจังหวัดกาญจนบุรี
    assert len(data) > 0

def test_filter_benefits_by_type():
    """ทดสอบการกรองสิทธิประโยชน์ตามประเภท"""
    response = client.get("/api/v1/tax/benefits?benefit_type=secondary_province")
    assert response.status_code == 200
    
    data = response.json()
    for benefit in data:
        assert benefit["benefit_type"] == "secondary_province"
