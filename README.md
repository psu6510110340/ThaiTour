# 🇹🇭 ThaiTour - ระบบท่องเที่ยวไทยและลดหย่อนภาษี

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-22%20Passed-brightgreen?style=flat-square)](https://pytest.org)

**REST API สำหรับระบบจัดการการท่องเที่ยวไทย** พร้อมระบบลงทะเบียน + Login แบบครบวงจร และคำนวณลดหย่อนภาษี

## ✨ คุณสมบัติหลัก

- 🔐 **Registration + Login Integration** - ลงทะเบียนครั้งเดียว Login ได้เลย
- 👥 **Role-based Permissions** - USER/MODERATOR/ADMIN แต่ละระดับ
- 🏛️ **Province Management** - จัดการ 77 จังหวัดไทย หลัก/รอง
- 💰 **Tax Calculation** - คำนวณลดหย่อนภาษี 30% สูงสุด 15,000 บาท
- 🧪 **Comprehensive Testing** - 22 tests ครอบคลุมทุกฟีเจอร์

## 🔑 ระบบ Authentication

### ลงทะเบียน → Login ทันที
```json
POST /api/v1/registration/
{
  "citizen_id": "1234567890123",
  "first_name": "สมชาย", "last_name": "ใจดี",
  "email": "somchai@example.com", "password": "mypass123",
  "province": "กรุงเทพมหานคร", "target_provinces": ["เชียงใหม่"]
}
```

### เข้าสู่ระบบ
```json
POST /api/v1/auth/login
{
  "username": "somchai@example.com",
  "password": "mypass123"
}
→ ได้ JWT Token
```

## 👥 สิทธิ์การใช้งาน

| Role | สิทธิ์ |
|------|--------|
| **USER** | ดูข้อมูล, คำนวณภาษี, จัดการข้อมูลตัวเอง |
| **MODERATOR** | + อนุมัติ/ปฏิเสธการลงทะเบียน |
| **ADMIN** | + จัดการผู้ใช้, เพิ่ม/ลบจังหวัด, จัดการสิทธิประโยชน์ |

## 🚀 การติดตั้งและรัน

```bash
# 1. โคลนโปรเจค
git clone https://github.com/psu6510110340/ThaiTour.git
cd ThaiTour

# 2. ติดตั้ง dependencies
pip install -r requirements.txt
# หรือใช้ poetry
poetry install

# 3. เริ่มต้นฐานข้อมูล
python scripts/init_db.py

# 4. รันเซิร์ฟเวอร์
uvicorn thaitour.main:app --reload
```

**🌐 API Documentation:** http://localhost:8000/docs

## � ตัวอย่างการคำนวณภาษี

```json
POST /api/v1/tax/calculate
Authorization: Bearer <jwt_token>
{
  "citizen_id": "1234567890123",
  "province_name": "เชียงใหม่",
  "spending_amount": 10000
}

Response:
{
  "reduction_amount": 3000,
  "reduction_percentage": 30,
  "max_benefit": 15000,
  "remaining_benefit": 12000
}
```

## �️ เทคโนโลยี

- **FastAPI** - Python web framework
- **SQLModel** - Database ORM with type safety  
- **JWT + bcrypt** - Authentication & security
- **Pytest** - Testing framework (22 tests)
- **SQLite** - Database with JSON field support

## 📁 โครงสร้างโปรเจค

```
thaitour/
├── models/          # Database models
├── routers/v1/      # API endpoints
├── schemas/         # Pydantic schemas
├── core/            # Security & config
├── scripts/         # DB utilities
└── tests/           # 22 comprehensive tests
```

## 🧪 การทดสอบ

```bash
# รัน tests ทั้งหมด
pytest tests/ -v

# ทดสอบเฉพาะ registration
pytest tests/test_registration.py -v
```

**📊 Test Coverage:** 22 tests ครอบคลุมทุก endpoint และ business logic

## 🎯 API Endpoints หลัก

### Authentication
- `POST /api/v1/registration/` - ลงทะเบียน + สร้าง User Account
- `POST /api/v1/auth/login` - เข้าสู่ระบบ
- `POST /api/v1/auth/logout` - ออกจากระบบ

### จังหวัด
- `GET /api/v1/province/` - ดูรายการจังหวัด
- `GET /api/v1/province/secondary` - จังหวัดรอง
- `POST /api/v1/province/` - เพิ่มจังหวัด (Admin)

### ภาษี
- `GET /api/v1/tax/benefits` - ดูสิทธิประโยชน์
- `POST /api/v1/tax/calculate` - คำนวณลดหย่อนภาษี

## 📝 หมายเหตุ

- ระบบใช้หลักเกณฑ์ลดหย่อนภาษีของรัฐบาลไทย
- Registration จะสร้าง User Account อัตโนมัติ (Role: USER)
- ใช้ JWT Token สำหรับ Authentication
- ข้อมูลจังหวัดและสิทธิประโยชน์พร้อมใช้งาน

---
**🏗️ พัฒนาโดย:** [PSU6510110340](https://github.com/psu6510110340) | **📅 อัพเดต:** July 2025

# รันทดสอบเฉพาะกลุ่ม
pytest tests/test_registration.py -v
```

## � Technology Stack

- **FastAPI** - Web framework
- **SQLModel** - ORM และ data validation
- **SQLite** - Database
- **JWT** - Authentication
- **Pytest** - Testing

## 📝 Admin Users

Default admin: `admin@thaitour.com` / `admin123`

---

**�🇭 ThaiTour API - จัดการการท่องเที่ยวไทยและลดหย่อนภาษี**

*Made with ❤️ for Thai Tourism Industry*
