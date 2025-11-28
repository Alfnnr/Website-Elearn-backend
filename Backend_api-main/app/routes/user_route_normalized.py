from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.core.database import get_db
from app.models.user_model import User, RoleEnum
from app.models.mahasiswa_model import Mahasiswa
from app.models.kelas_model import Kelas
from app.schemas.user_schema import UserResponse, UserRegister, UserUpdate, AdminCreate, AdminResponse
from app.schemas.mahasiswa_schema import (
    UserMahasiswaCreate, 
    UserMahasiswaResponse, 
    UserMahasiswaUpdate
)
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])

# =====================================================
# GET ALL USERS
# Returns users with their profile data (if mahasiswa)
# =====================================================
@router.get("/", response_model=List[UserMahasiswaResponse])
def get_users(
    role: Optional[str] = Query(None, description="Filter by role: admin, super_admin, mahasiswa"),
    db: Session = Depends(get_db)
):
    """Get all users with their profile data"""
    query = db.query(User).outerjoin(Mahasiswa, User.id_user == Mahasiswa.user_id)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.all()
    
    result = []
    for user in users:
        user_dict = {
            "id_user": user.id_user,
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "is_active": user.is_active,
        }
        
        # If mahasiswa, include profile data
        if user.role == RoleEnum.mahasiswa and hasattr(user, 'mahasiswa_profile') and user.mahasiswa_profile:
            mhs = user.mahasiswa_profile[0] if isinstance(user.mahasiswa_profile, list) else user.mahasiswa_profile
            user_dict.update({
                "id_mahasiswa": mhs.id_mahasiswa,
                "nim": mhs.nim,
                "nama": mhs.nama,
                "tempat_lahir": mhs.tempat_lahir,
                "tanggal_lahir": mhs.tanggal_lahir,
                "jenis_kelamin": mhs.jenis_kelamin,
                "agama": mhs.agama,
                "alamat": mhs.alamat,
                "no_hp": mhs.no_hp,
                "id_kelas": mhs.id_kelas,
            })
            
            # Add kelas name if exists
            if mhs.id_kelas:
                kelas = db.query(Kelas).filter(Kelas.id_kelas == mhs.id_kelas).first()
                if kelas:
                    user_dict["nama_kelas"] = kelas.nama_kelas
        
        result.append(user_dict)
    
    return result

# =====================================================
# GET USER BY ID
# =====================================================
@router.get("/{user_id}", response_model=UserMahasiswaResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID with profile data"""
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    user_dict = {
        "id_user": user.id_user,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else user.role,
        "is_active": user.is_active,
    }
    
    # If mahasiswa, get profile data
    if user.role == RoleEnum.mahasiswa:
        mhs = db.query(Mahasiswa).filter(Mahasiswa.user_id == user_id).first()
        if mhs:
            user_dict.update({
                "id_mahasiswa": mhs.id_mahasiswa,
                "nim": mhs.nim,
                "nama": mhs.nama,
                "tempat_lahir": mhs.tempat_lahir,
                "tanggal_lahir": mhs.tanggal_lahir,
                "jenis_kelamin": mhs.jenis_kelamin,
                "agama": mhs.agama,
                "alamat": mhs.alamat,
                "no_hp": mhs.no_hp,
                "id_kelas": mhs.id_kelas,
            })
            
            if mhs.id_kelas:
                kelas = db.query(Kelas).filter(Kelas.id_kelas == mhs.id_kelas).first()
                if kelas:
                    user_dict["nama_kelas"] = kelas.nama_kelas
    
    return user_dict

# =====================================================
# CREATE ADMIN USER
# =====================================================
@router.post("/admin", response_model=AdminResponse)
def create_admin(user_data: AdminCreate, db: Session = Depends(get_db)):
    """Create admin or super_admin user"""
    # Validate role
    if user_data.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=400, detail="Role harus 'admin' atau 'super_admin'")
    
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username sudah digunakan")
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email sudah digunakan")
    
    # Create user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id_user": new_user.id_user,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role.value if hasattr(new_user.role, 'value') else new_user.role,
        "is_active": new_user.is_active
    }

# =====================================================
# CREATE MAHASISWA (User + Profile)
# =====================================================
@router.post("/mahasiswa", response_model=UserMahasiswaResponse)
def create_mahasiswa(mahasiswa_data: UserMahasiswaCreate, db: Session = Depends(get_db)):
    """Create mahasiswa with user account and profile"""
    # Check if username exists
    if db.query(User).filter(User.username == mahasiswa_data.username).first():
        raise HTTPException(status_code=400, detail="Username sudah digunakan")
    
    # Check if email exists
    if db.query(User).filter(User.email == mahasiswa_data.email).first():
        raise HTTPException(status_code=400, detail="Email sudah digunakan")
    
    # Check if NIM exists
    if db.query(Mahasiswa).filter(Mahasiswa.nim == mahasiswa_data.nim).first():
        raise HTTPException(status_code=400, detail="NIM sudah digunakan")
    
    try:
        # 1. Create user (authentication)
        new_user = User(
            username=mahasiswa_data.username,
            email=mahasiswa_data.email,
            password=hash_password(mahasiswa_data.password),
            role='mahasiswa',
            is_active=True
        )
        db.add(new_user)
        db.flush()  # Get user_id without committing
        
        # 2. Create mahasiswa profile
        new_mahasiswa = Mahasiswa(
            user_id=new_user.id_user,
            nim=mahasiswa_data.nim,
            nama=mahasiswa_data.nama,
            tempat_lahir=mahasiswa_data.tempat_lahir,
            tanggal_lahir=mahasiswa_data.tanggal_lahir,
            jenis_kelamin=mahasiswa_data.jenis_kelamin,
            agama=mahasiswa_data.agama,
            alamat=mahasiswa_data.alamat,
            no_hp=mahasiswa_data.no_hp,
            id_kelas=mahasiswa_data.id_kelas
        )
        db.add(new_mahasiswa)
        db.commit()
        db.refresh(new_user)
        db.refresh(new_mahasiswa)
        
        # Get kelas name
        nama_kelas = None
        if new_mahasiswa.id_kelas:
            kelas = db.query(Kelas).filter(Kelas.id_kelas == new_mahasiswa.id_kelas).first()
            if kelas:
                nama_kelas = kelas.nama_kelas
        
        return {
            "id_user": new_user.id_user,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role.value if hasattr(new_user.role, 'value') else new_user.role,
            "is_active": new_user.is_active,
            "id_mahasiswa": new_mahasiswa.id_mahasiswa,
            "nim": new_mahasiswa.nim,
            "nama": new_mahasiswa.nama,
            "tempat_lahir": new_mahasiswa.tempat_lahir,
            "tanggal_lahir": new_mahasiswa.tanggal_lahir,
            "jenis_kelamin": new_mahasiswa.jenis_kelamin,
            "agama": new_mahasiswa.agama,
            "alamat": new_mahasiswa.alamat,
            "no_hp": new_mahasiswa.no_hp,
            "id_kelas": new_mahasiswa.id_kelas,
            "nama_kelas": nama_kelas
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal membuat mahasiswa: {str(e)}")

# =====================================================
# UPDATE USER
# =====================================================
@router.put("/{user_id}", response_model=UserMahasiswaResponse)
def update_user(user_id: int, update_data: UserMahasiswaUpdate, db: Session = Depends(get_db)):
    """Update user (and mahasiswa profile if applicable)"""
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    try:
        # Update user fields
        if update_data.username is not None:
            # Check if new username already exists
            existing = db.query(User).filter(
                User.username == update_data.username,
                User.id_user != user_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Username sudah digunakan")
            user.username = update_data.username
        
        if update_data.email is not None:
            # Check if new email already exists
            existing = db.query(User).filter(
                User.email == update_data.email,
                User.id_user != user_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email sudah digunakan")
            user.email = update_data.email
        
        if update_data.password is not None and update_data.password != "":
            user.password = hash_password(update_data.password)
        
        # If user is mahasiswa, update profile
        if user.role == RoleEnum.mahasiswa:
            mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.user_id == user_id).first()
            if mahasiswa:
                if update_data.nim is not None:
                    # Check if NIM already exists
                    existing = db.query(Mahasiswa).filter(
                        Mahasiswa.nim == update_data.nim,
                        Mahasiswa.id_mahasiswa != mahasiswa.id_mahasiswa
                    ).first()
                    if existing:
                        raise HTTPException(status_code=400, detail="NIM sudah digunakan")
                    mahasiswa.nim = update_data.nim
                
                if update_data.nama is not None:
                    mahasiswa.nama = update_data.nama
                if update_data.tempat_lahir is not None:
                    mahasiswa.tempat_lahir = update_data.tempat_lahir
                if update_data.tanggal_lahir is not None:
                    mahasiswa.tanggal_lahir = update_data.tanggal_lahir
                if update_data.jenis_kelamin is not None:
                    mahasiswa.jenis_kelamin = update_data.jenis_kelamin
                if update_data.agama is not None:
                    mahasiswa.agama = update_data.agama
                if update_data.alamat is not None:
                    mahasiswa.alamat = update_data.alamat
                if update_data.no_hp is not None:
                    mahasiswa.no_hp = update_data.no_hp
                if update_data.id_kelas is not None:
                    mahasiswa.id_kelas = update_data.id_kelas
        
        db.commit()
        db.refresh(user)
        
        # Build response
        user_dict = {
            "id_user": user.id_user,
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "is_active": user.is_active,
        }
        
        # If mahasiswa, include profile data
        if user.role == RoleEnum.mahasiswa:
            mhs = db.query(Mahasiswa).filter(Mahasiswa.user_id == user_id).first()
            if mhs:
                user_dict.update({
                    "id_mahasiswa": mhs.id_mahasiswa,
                    "nim": mhs.nim,
                    "nama": mhs.nama,
                    "tempat_lahir": mhs.tempat_lahir,
                    "tanggal_lahir": mhs.tanggal_lahir,
                    "jenis_kelamin": mhs.jenis_kelamin,
                    "agama": mhs.agama,
                    "alamat": mhs.alamat,
                    "no_hp": mhs.no_hp,
                    "id_kelas": mhs.id_kelas,
                })
                
                if mhs.id_kelas:
                    kelas = db.query(Kelas).filter(Kelas.id_kelas == mhs.id_kelas).first()
                    if kelas:
                        user_dict["nama_kelas"] = kelas.nama_kelas
        
        return user_dict
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal update user: {str(e)}")

# =====================================================
# DELETE USER
# =====================================================
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user (mahasiswa profile will be deleted automatically via CASCADE)"""
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    db.delete(user)
    db.commit()
    return {"message": "User berhasil dihapus", "id": user_id}
