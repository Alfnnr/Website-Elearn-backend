from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
from enum import Enum

class JenisKelamin(str, Enum):
    L = "L"
    P = "P"

# Schema for creating dosen profile only
class DosenCreate(BaseModel):
    nip: str = Field(..., max_length=50)
    nama_dosen: str = Field(..., max_length=150)
    email_dosen: Optional[EmailStr] = None
    tempat_lahir: Optional[str] = Field(None, max_length=100)
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[JenisKelamin] = None
    agama: Optional[str] = Field(None, max_length=50)
    alamat: Optional[str] = None
    no_hp: Optional[str] = Field(None, max_length=20)

# Schema for creating user + dosen (combined)
class UserDosenCreate(BaseModel):
    # User fields
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    
    # Dosen fields
    nip: str = Field(..., max_length=50)
    nama_dosen: str = Field(..., max_length=150)
    email_dosen: Optional[EmailStr] = None
    tempat_lahir: Optional[str] = Field(None, max_length=100)
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[JenisKelamin] = None
    agama: Optional[str] = Field(None, max_length=50)
    alamat: Optional[str] = None
    no_hp: Optional[str] = Field(None, max_length=20)

# Schema for updating dosen profile
class DosenUpdate(BaseModel):
    nip: Optional[str] = Field(None, max_length=50)
    nama_dosen: Optional[str] = Field(None, max_length=150)
    email_dosen: Optional[EmailStr] = None
    tempat_lahir: Optional[str] = Field(None, max_length=100)
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[JenisKelamin] = None
    agama: Optional[str] = Field(None, max_length=50)
    alamat: Optional[str] = None
    no_hp: Optional[str] = Field(None, max_length=20)

# Schema for updating user + dosen (combined)
class UserDosenUpdate(BaseModel):
    # User fields
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None
    
    # Dosen fields
    nip: Optional[str] = Field(None, max_length=50)
    nama_dosen: Optional[str] = Field(None, max_length=150)
    email_dosen: Optional[EmailStr] = None
    tempat_lahir: Optional[str] = Field(None, max_length=100)
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[JenisKelamin] = None
    agama: Optional[str] = Field(None, max_length=50)
    alamat: Optional[str] = None
    no_hp: Optional[str] = Field(None, max_length=20)

# Schema for response (user + dosen combined data)
class UserDosenResponse(BaseModel):
    # User fields
    id_user: int
    username: str
    email: str
    role: str
    is_active: bool
    
    # Dosen fields
    id_dosen: Optional[int] = None
    nip: Optional[str] = None
    nama_dosen: Optional[str] = None
    email_dosen: Optional[str] = None
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[str] = None
    agama: Optional[str] = None
    alamat: Optional[str] = None
    no_hp: Optional[str] = None

    class Config:
        from_attributes = True
