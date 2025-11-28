from pydantic import BaseModel
from typing import Optional
from datetime import date

# =====================================================
# MAHASISWA SCHEMAS
# =====================================================

class MahasiswaBase(BaseModel):
    nim: str
    nama: str
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[str] = None  # 'L' or 'P'
    agama: Optional[str] = None
    alamat: Optional[str] = None
    no_hp: Optional[str] = None
    id_kelas: Optional[int] = None

class MahasiswaCreate(MahasiswaBase):
    user_id: int

class MahasiswaUpdate(BaseModel):
    nim: Optional[str] = None
    nama: Optional[str] = None
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[str] = None
    agama: Optional[str] = None
    alamat: Optional[str] = None
    no_hp: Optional[str] = None
    id_kelas: Optional[int] = None

class MahasiswaResponse(MahasiswaBase):
    id_mahasiswa: int
    user_id: int
    
    class Config:
        from_attributes = True

# =====================================================
# COMBINED USER + MAHASISWA SCHEMAS
# For endpoints that need both authentication and profile data
# =====================================================

class UserMahasiswaCreate(BaseModel):
    """Schema for creating a mahasiswa with user account"""
    # User (authentication) fields
    username: str
    email: str
    password: str
    
    # Mahasiswa (profile) fields
    nim: str
    nama: str
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[str] = None
    agama: Optional[str] = None
    alamat: Optional[str] = None
    no_hp: Optional[str] = None
    id_kelas: Optional[int] = None

class UserMahasiswaResponse(BaseModel):
    """Schema for returning mahasiswa with user account info"""
    # User fields
    id_user: int
    username: str
    email: str
    role: str
    is_active: bool
    
    # Mahasiswa fields
    id_mahasiswa: Optional[int] = None
    nim: Optional[str] = None
    nama: Optional[str] = None
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[str] = None
    agama: Optional[str] = None
    alamat: Optional[str] = None
    no_hp: Optional[str] = None
    id_kelas: Optional[int] = None
    nama_kelas: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserMahasiswaUpdate(BaseModel):
    """Schema for updating mahasiswa (both user and profile data)"""
    # User fields
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    
    # Mahasiswa fields
    nim: Optional[str] = None
    nama: Optional[str] = None
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[str] = None
    agama: Optional[str] = None
    alamat: Optional[str] = None
    no_hp: Optional[str] = None
    id_kelas: Optional[int] = None
