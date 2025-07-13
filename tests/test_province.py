import pytest
from fastapi.testclient import TestClient
from thaitour.main import app

client = TestClient(app)

def test_get_all_provinces():
    """ทดสอบการดึงข้อมูลจังหวัดทั้งหมด"""
    response = client.get("/api/v1/provinces/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # ตรวจสอบว่ามีจังหวัดหลักและจังหวัดรอง
    primary_provinces = [p for p in data if p["province_type"] == "primary"]
    secondary_provinces = [p for p in data if p["province_type"] == "secondary"]
    
    assert len(primary_provinces) > 0
    assert len(secondary_provinces) > 0

def test_get_secondary_provinces():
    """ทดสอบการดึงข้อมูลจังหวัดรองที่มีสิทธิลดหย่อนภาษี"""
    response = client.get("/api/v1/provinces/secondary")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    for province in data:
        assert province["province_type"] == "secondary"
        assert province["is_secondary_province"] is True
        assert province["tax_reduction_percentage"] > 0

def test_get_province_by_id():
    """ทดสอบการดึงข้อมูลจังหวัดตาม ID"""
    # ทดสอบดึงข้อมูลกรุงเทพ (ID: 1)
    response = client.get("/api/v1/provinces/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == 1
    assert data["name_th"] == "กรุงเทพมหานคร"
    assert data["province_type"] == "primary"

def test_get_province_tax_info():
    """ทดสอบการดึงข้อมูลลดหย่อนภาษีของจังหวัด"""
    # ทดสอบกับจังหวัดรอง (กาญจนบุรี ID: 3)
    response = client.get("/api/v1/provinces/3/tax-info")
    assert response.status_code == 200
    
    data = response.json()
    assert data["province_id"] == 3
    assert data["name_th"] == "กาญจนบุรี"
    assert data["is_secondary_province"] is True
    assert data["tax_reduction_percentage"] > 0
    assert data["max_reduction_amount"] > 0

def test_filter_provinces_by_type():
    """ทดสอบการกรองจังหวัดตามประเภท"""
    # กรองจังหวัดรอง
    response = client.get("/api/v1/provinces/?province_type=secondary")
    assert response.status_code == 200
    
    data = response.json()
    for province in data:
        assert province["province_type"] == "secondary"

def test_filter_provinces_by_region():
    """ทดสอบการกรองจังหวัดตามภาค"""
    # กรองจังหวัดภาคเหนือ
    response = client.get("/api/v1/provinces/?region=เหนือ")
    assert response.status_code == 200
    
    data = response.json()
    for province in data:
        assert province["region"] == "เหนือ"

def test_province_not_found():
    """ทดสอบการหาจังหวัดที่ไม่มีอยู่"""
    response = client.get("/api/v1/provinces/999")
    assert response.status_code == 404
    assert "ไม่พบข้อมูลจังหวัด" in response.json()["detail"]

def test_province_tax_info_not_found():
    """ทดสอบการหาข้อมูลลดหย่อนภาษีของจังหวัดที่ไม่มีอยู่"""
    response = client.get("/api/v1/provinces/999/tax-info")
    assert response.status_code == 404
    assert "ไม่พบข้อมูลจังหวัด" in response.json()["detail"]
