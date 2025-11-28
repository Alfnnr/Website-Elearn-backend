from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.user_model import User, RoleEnum
from app.schemas.user_schema import UserResponse, UserRegister
from app.core.security import hash_password
from pydantic import BaseModel, EmailStr
from datetime import date

router = APIRouter(prefix="/users", tags=["Users"])

class UserUpdate(BaseModel):
    nama: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    # Admin/Super Admin fields
    nip: Optional[str] = None
    # Mahasiswa fields
    nim: Optional[str] = None
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[str] = None
    agama: Optional[str] = None
    alamat: Optional[str] = None
    no_hp: Optional[str] = None
    kelas: Optional[str] = None

@router.get("/")
def get_users(
    role: Optional[str] = Query(None, description="Filter by role: admin, super_admin, mahasiswa"),
    db: Session = Depends(get_db)
):
    """Get all users, optionally filtered by role"""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    users = query.all()
    
    # Convert to dict to ensure proper serialization
    result = []
    for user in users:
        result.append({
            "id_user": user.id_user,
            "nama": user.nama,
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "nip": user.nip,
            "nim": user.nim,
            "tempat_lahir": user.tempat_lahir,
            "tanggal_lahir": str(user.tanggal_lahir) if user.tanggal_lahir else None,
            "jenis_kelamin": user.jenis_kelamin,
            "agama": user.agama,
            "alamat": user.alamat,
            "no_hp": user.no_hp,
            "kelas": user.kelas
        })
    return result

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return {
        "id_user": user.id_user,
        "nama": user.nama,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else user.role,
        "nip": user.nip,
        "nim": user.nim,
        "tempat_lahir": user.tempat_lahir,
        "tanggal_lahir": str(user.tanggal_lahir) if user.tanggal_lahir else None,
        "jenis_kelamin": user.jenis_kelamin,
        "agama": user.agama,
        "alamat": user.alamat,
        "no_hp": user.no_hp,
        "kelas": user.kelas
    }

@router.post("/")
def create_user(user: UserRegister, db: Session = Depends(get_db)):
    """Create new user (admin, super_admin, or mahasiswa)"""
    # Check if username already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username sudah digunakan")
    
    # Check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email sudah digunakan")
    
    new_user = User(
        nama=user.nama,
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=user.role,
        nip=user.nip,
        nim=user.nim,
        tempat_lahir=user.tempat_lahir,
        tanggal_lahir=user.tanggal_lahir,
        jenis_kelamin=user.jenis_kelamin,
        agama=user.agama,
        alamat=user.alamat,
        no_hp=user.no_hp,
        kelas=user.kelas
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id_user": new_user.id_user,
        "nama": new_user.nama,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role.value if hasattr(new_user.role, 'value') else new_user.role,
        "nip": new_user.nip,
        "nim": new_user.nim,
        "tempat_lahir": new_user.tempat_lahir,
        "tanggal_lahir": new_user.tanggal_lahir,
        "jenis_kelamin": new_user.jenis_kelamin,
        "agama": new_user.agama,
        "alamat": new_user.alamat,
        "no_hp": new_user.no_hp,
        "kelas": new_user.kelas
    }

@router.put("/{user_id}")
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user data"""
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    # Update fields if provided
    if user_data.nama is not None:
        user.nama = user_data.nama
    if user_data.username is not None:
        # Check if new username already exists (excluding current user)
        existing = db.query(User).filter(
            User.username == user_data.username,
            User.id_user != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username sudah digunakan")
        user.username = user_data.username
    if user_data.email is not None:
        # Check if new email already exists (excluding current user)
        existing = db.query(User).filter(
            User.email == user_data.email,
            User.id_user != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email sudah digunakan")
        user.email = user_data.email
    if user_data.password is not None:
        user.password = hash_password(user_data.password)
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.nip is not None:
        user.nip = user_data.nip
    if user_data.nim is not None:
        user.nim = user_data.nim
    if user_data.tempat_lahir is not None:
        user.tempat_lahir = user_data.tempat_lahir
    if user_data.tanggal_lahir is not None:
        user.tanggal_lahir = user_data.tanggal_lahir
    if user_data.jenis_kelamin is not None:
        user.jenis_kelamin = user_data.jenis_kelamin
    if user_data.agama is not None:
        user.agama = user_data.agama
    if user_data.alamat is not None:
        user.alamat = user_data.alamat
    if user_data.no_hp is not None:
        user.no_hp = user_data.no_hp
    if user_data.kelas is not None:
        user.kelas = user_data.kelas
    
    db.commit()
    db.refresh(user)
    return {
        "id_user": user.id_user,
        "nama": user.nama,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else user.role,
        "nip": user.nip,
        "nim": user.nim,
        "tempat_lahir": user.tempat_lahir,
        "tanggal_lahir": user.tanggal_lahir,
        "jenis_kelamin": user.jenis_kelamin,
        "agama": user.agama,
        "alamat": user.alamat,
        "no_hp": user.no_hp,
        "kelas": user.kelas
    }

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user"""
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    db.delete(user)
    db.commit()
    return {"message": "User berhasil dihapus", "id": user_id}
