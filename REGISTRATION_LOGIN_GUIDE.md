# 🎯 วิธีการใช้งาน Registration + Login ใหม่

## 📋 **การลงทะเบียนใหม่ (พร้อมสร้าง User Account)**

### 1. ลงทะเบียนผ่าน Swagger UI

ไปที่ `http://localhost:8000/docs` → `POST /api/v1/registration/`

```json
{
  "citizen_id": "1234567890123",
  "first_name": "สมชาย",
  "last_name": "ใจดี", 
  "email": "somchai@example.com",
  "phone": "0812345678",
  "date_of_birth": "1990-01-01T00:00:00",
  "password": "mypassword123",
  "address": "123 ถนนสุขุมวิท",
  "province": "กรุงเทพมหานคร",
  "district": "วัฒนา",
  "sub_district": "ลุมพินี",
  "postal_code": "10330",
  "target_provinces": ["เชียงใหม่", "กาญจนบุรี"],
  "interests": ["ธรรมชาติ", "วัฒนธรรม"]
}
```

**📤 Response:**
```json
{
  "id": 1,
  "user_id": 3,
  "citizen_id": "1234567890123",
  "first_name": "สมชาย",
  "last_name": "ใจดี",
  "email": "somchai@example.com",
  "status": "pending",
  "target_provinces": ["เชียงใหม่", "กาญจนบุรี"],
  "interests": ["ธรรมชาติ", "วัฒนธรรม"]
}
```

## 🔐 **การเข้าสู่ระบบ**

### 2. Login ด้วยข้อมูลที่ลงทะเบียน

ไปที่ `POST /api/v1/auth/login`

```json
{
  "username": "somchai@example.com",
  "password": "mypassword123"
}
```

**📤 Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## 🎯 **การใช้งาน API ที่ต้อง Authentication**

### 3. ใช้ Token เพื่อเข้าถึง Protected Endpoints

คัดลอก `access_token` จากขั้นตอน 2 แล้วคลิก **"Authorize"** ใน Swagger UI

ใส่: `Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`

ตอนนี้สามารถใช้ API ต่างๆ ได้:

- ✅ `PUT /api/v1/registration/{id}` - แก้ไขข้อมูลการลงทะเบียน
- ✅ `POST /api/v1/auth/logout` - ออกจากระบบ

## 👥 **User Roles**

| Role | สิทธิ์ |
|------|--------|
| **USER** (ผู้ลงทะเบียนใหม่) | - แก้ไขข้อมูลการลงทะเบียนของตัวเอง<br>- ดูข้อมูลจังหวัด<br>- คำนวณลดหย่อนภาษี |
| **ADMIN** | - ทุกสิทธิ์ของ USER<br>- ดูรายการ Registration ทั้งหมด<br>- ลบ Registration<br>- จัดการข้อมูลจังหวัด<br>- จัดการสิทธิประโยชน์ภาษี |

## 🔄 **การ Migrate ข้อมูลเดิม**

หากมีข้อมูล Registration เดิมอยู่แล้ว ให้รันคำสั่งนี้:

```bash
python scripts/migrate_add_user_id.py
```

**สิ่งที่จะเกิดขึ้น:**
- เพิ่มคอลัมน์ `user_id` ในตาราง registration
- สร้าง User Account สำหรับ Registration เดิม
- รหัสผ่านเริ่มต้น: `123456`
- สามารถ login ด้วยอีเมลและรหัสผ่าน `123456` ได้

## 📝 **ข้อมูล Login ทั้งหมด**

| อีเมล | รหัสผ่าน | Role | หมายเหตุ |
|-------|----------|------|----------|
| `admin@thaitour.com` | `secret` | ADMIN | Admin เดิม |
| `user@thaitour.com` | `secret` | USER | User เดิม |
| `somchai@example.com` | `mypassword123` | USER | ผู้ลงทะเบียนใหม่ |
| `(registration เดิม)` | `123456` | USER | Registration เดิมหลัง migrate |

## 🎉 **สรุป**

✅ **ลงทะเบียนใหม่** → สร้าง User Account อัตโนมัติ → Login ได้ทันที

✅ **เป็น User Role** → มีสิทธิ์เข้าถึง API ที่ต้อง Authentication

✅ **รองรับข้อมูลเดิม** → Migration script จัดการให้
