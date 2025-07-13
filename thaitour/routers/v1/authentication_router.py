from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import timedelta, datetime
from sqlmodel import Session, select
from thaitour.core.security import create_access_token, verify_password
from thaitour.core.config import settings
from thaitour.models.user_model import User
from thaitour.models import get_session

router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    เข้าสู่ระบบด้วย username และ password
    """
    # ค้นหาผู้ใช้จากฐานข้อมูล
    user = session.exec(
        select(User).where(
            User.username == login_data.username,
            User.is_active == True
        )
    ).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # อัปเดต last_login
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )

@router.post("/refresh")
async def refresh_token():
    """
    รีเฟรช token
    """
    # Implementation for token refresh
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented yet"
    )

@router.post("/logout")
async def logout():
    """
    ออกจากระบบ
    """
    return {"message": "ออกจากระบบเรียบร้อยแล้ว"}
