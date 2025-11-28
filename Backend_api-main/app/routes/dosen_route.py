from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.dosen_model import Dosen
from app.models.user_model import User
from app.schemas.dosen_schema import UserDosenResponse

router = APIRouter(prefix="/dosen", tags=["Dosen"])

# =====================================================
# GET ALL DOSEN (Read-Only - Backward Compatibility)
# =====================================================
@router.get("/", response_model=List[UserDosenResponse])
def get_all_dosen(db: Session = Depends(get_db)):
    """Get all dosen with their user data"""
    dosen_list = db.query(Dosen).all()
    
    result = []
    for dosen in dosen_list:
        # Get user data
        user = db.query(User).filter(User.id_user == dosen.user_id).first()
        if user:
            result.append({
                "id_user": user.id_user,
                "username": user.username,
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else user.role,
                "is_active": user.is_active,
                "id_dosen": dosen.id_dosen,
                "nip": dosen.nip,
                "nama_dosen": dosen.nama_dosen,
                "email_dosen": dosen.email_dosen,
                "tempat_lahir": dosen.tempat_lahir,
                "tanggal_lahir": dosen.tanggal_lahir,
                "jenis_kelamin": dosen.jenis_kelamin,
                "agama": dosen.agama,
                "alamat": dosen.alamat,
                "no_hp": dosen.no_hp
            })
    
    return result

# =====================================================
# GET DOSEN BY ID (Read-Only - Backward Compatibility)
# =====================================================
@router.get("/{id_dosen}", response_model=UserDosenResponse)
def get_dosen(id_dosen: int, db: Session = Depends(get_db)):
    """Get dosen by id_dosen"""
    dosen = db.query(Dosen).filter(Dosen.id_dosen == id_dosen).first()
    if not dosen:
        raise HTTPException(status_code=404, detail="Dosen tidak ditemukan")
    
    # Get user data
    user = db.query(User).filter(User.id_user == dosen.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User dosen tidak ditemukan")
    
    return {
        "id_user": user.id_user,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else user.role,
        "is_active": user.is_active,
        "id_dosen": dosen.id_dosen,
        "nip": dosen.nip,
        "nama_dosen": dosen.nama_dosen,
        "email_dosen": dosen.email_dosen,
        "tempat_lahir": dosen.tempat_lahir,
        "tanggal_lahir": dosen.tanggal_lahir,
        "jenis_kelamin": dosen.jenis_kelamin,
        "agama": dosen.agama,
        "alamat": dosen.alamat,
        "no_hp": dosen.no_hp
    }

# =====================================================
# POST/PUT/DELETE - DEPRECATED
# =====================================================
@router.post("/")
def create_dosen_deprecated():
    """DEPRECATED: Use POST /users/dosen instead"""
    raise HTTPException(
        status_code=410,
        detail="Endpoint ini sudah deprecated. Gunakan POST /users/dosen untuk membuat dosen baru."
    )

@router.put("/{id_dosen}")
def update_dosen_deprecated(id_dosen: int):
    """DEPRECATED: Use PUT /users/dosen/{user_id} instead"""
    raise HTTPException(
        status_code=410,
        detail="Endpoint ini sudah deprecated. Gunakan PUT /users/dosen/{user_id} untuk update dosen."
    )

@router.delete("/{id_dosen}")
def delete_dosen_deprecated(id_dosen: int):
    """DEPRECATED: Use DELETE /users/{user_id} instead"""
    raise HTTPException(
        status_code=410,
        detail="Endpoint ini sudah deprecated. Gunakan DELETE /users/{user_id} untuk hapus dosen."
    )
