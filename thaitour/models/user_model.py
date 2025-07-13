from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Authentication fields
    username: str = Field(index=True, unique=True, max_length=50)
    hashed_password: str = Field(max_length=255)
    email: Optional[str] = Field(default=None, index=True, unique=True, max_length=100)
    
    # User information
    full_name: Optional[str] = Field(default=None, max_length=200)
    role: UserRole = Field(default=UserRole.USER)
    
    # Status fields
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
