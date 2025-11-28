from pydantic import BaseModel, EmailStr
from typing import Optional

# =====================================================
# USER SCHEMAS (Authentication Only)
# =====================================================

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserRegister(UserBase):
    password: str
    role: str  # 'admin', 'super_admin', 'mahasiswa'

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id_user: int
    username: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

# =====================================================
# ADMIN SCHEMAS (Simple - no separate table yet)
# =====================================================

class AdminCreate(UserRegister):
    """For creating admin/super_admin users"""
    pass

class AdminResponse(UserResponse):
    """For returning admin user data"""
    pass