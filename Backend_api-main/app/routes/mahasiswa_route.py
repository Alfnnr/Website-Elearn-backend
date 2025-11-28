from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.core.database import get_db
from app.models.mahasiswa_model import Mahasiswa
from app.models.user_model import User

router = APIRouter(prefix="/mahasiswa", tags=["Mahasiswa (Read-Only)"])

# NOTE: This route is now READ-ONLY for backward compatibility
# For creating/updating mahasiswa, use /users/mahasiswa endpoint instead


class MahasiswaCreate(BaseModel):
    nim: str = Field(..., min_length=3)
    nama_mahasiswa: str = Field(..., min_length=2)
    id_kelas: int
    email: Optional[EmailStr] = None


class MahasiswaUpdate(BaseModel):
    nim: Optional[str] = None
    nama_mahasiswa: Optional[str] = None
    id_kelas: Optional[int] = None
    email: Optional[EmailStr] = None

@router.get("/{id_mahasiswa}")
def get_mahasiswa_by_id(id_mahasiswa: int, db: Session = Depends(get_db)):
    """Get mahasiswa by ID"""
    try:
        mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.id_mahasiswa == id_mahasiswa).first()
        
        if not mahasiswa:
            raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
        
        return {
            "id_mahasiswa": mahasiswa.id_mahasiswa,
            "nim": mahasiswa.nim,
            "nama_mahasiswa": mahasiswa.nama,  # Changed from nama_mahasiswa to nama
            "id_kelas": mahasiswa.id_kelas,
            "tempat_lahir": mahasiswa.tempat_lahir,
            "tanggal_lahir": mahasiswa.tanggal_lahir,
            "jenis_kelamin": mahasiswa.jenis_kelamin,
            "agama": mahasiswa.agama,
            "alamat": mahasiswa.alamat,
            "no_hp": mahasiswa.no_hp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔴 Error get_mahasiswa_by_id: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/kelas/{id_kelas}")
def get_mahasiswa_by_kelas(id_kelas: int, db: Session = Depends(get_db)):
    """Get all mahasiswa in a kelas"""
    try:
        mahasiswa_list = db.query(Mahasiswa).filter(Mahasiswa.id_kelas == id_kelas).all()
        
        result = []
        for mhs in mahasiswa_list:
            result.append({
                "id_mahasiswa": mhs.id_mahasiswa,
                "nim": mhs.nim,
                "nama_mahasiswa": mhs.nama,  # Changed from nama_mahasiswa to nama
                "id_kelas": mhs.id_kelas
            })
        
        return result
        
    except Exception as e:
        print(f"🔴 Error get_mahasiswa_by_kelas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# POST/PUT/DELETE DISABLED - Use /users/mahasiswa endpoint instead
# @router.post("/")
# def create_mahasiswa(payload: MahasiswaCreate, db: Session = Depends(get_db)):
#     """Use POST /users/mahasiswa instead"""
#     raise HTTPException(status_code=410, detail="This endpoint is deprecated. Use POST /users/mahasiswa instead")


# @router.put("/{id_mahasiswa}")
# def update_mahasiswa(id_mahasiswa: int, payload: MahasiswaUpdate, db: Session = Depends(get_db)):
#     """Use PUT /users/{user_id} instead"""
#     raise HTTPException(status_code=410, detail="This endpoint is deprecated. Use PUT /users/{user_id} instead")


# @router.delete("/{id_mahasiswa}")
# def delete_mahasiswa(id_mahasiswa: int, db: Session = Depends(get_db)):
#     """Use DELETE /users/{user_id} instead"""
#     raise HTTPException(status_code=410, detail="This endpoint is deprecated. Use DELETE /users/{user_id} instead")
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔴 Error delete_mahasiswa: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gagal menghapus mahasiswa: {str(e)}")
