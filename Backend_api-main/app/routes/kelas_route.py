from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.kelas_model import Kelas
from pydantic import BaseModel, Field

router = APIRouter(prefix="/kelas", tags=["Kelas"])


# 🧱 Model Response Aman
class KelasResponse(BaseModel):
    id_kelas: int
    nama_kelas: str
    prodi: Optional[str] = None
    tahun_angkatan: Optional[int] = None
    golongan: Optional[str] = None
    # Kolom lama yang mungkin tidak ada di DB, dibuat opsional agar aman
    tahun_ajaran: Optional[str] = None
    semester: Optional[str] = None

    class Config:
        from_attributes = True


class KelasCreate(BaseModel):
    nama_kelas: str = Field(..., min_length=2)
    prodi: str = Field(..., description="TIF|MIF|TKK")
    tahun_angkatan: Optional[int] = None
    golongan: Optional[str] = None


@router.get("/", response_model=List[KelasResponse])
def get_all_kelas(db: Session = Depends(get_db)):
    """
    Ambil semua kelas dari database.
    Akan menampilkan data meskipun kolom tahun_ajaran/semester belum ada atau NULL.
    """
    try:
        kelas_list = db.query(Kelas).all()

        if not kelas_list:
            raise HTTPException(status_code=404, detail="Belum ada data kelas")

        return kelas_list

    except HTTPException:
        raise
    except Exception as e:
        print(f"🔴 Error get_all_kelas: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data kelas: {str(e)}")


@router.get("/{id_kelas}", response_model=KelasResponse)
def get_kelas_by_id(id_kelas: int, db: Session = Depends(get_db)):
    """Get kelas by ID"""
    try:
        kelas = db.query(Kelas).filter(Kelas.id_kelas == id_kelas).first()
        
        if not kelas:
            raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")
        
        return kelas
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔴 Error get_kelas_by_id: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/", response_model=KelasResponse)
def create_kelas(payload: KelasCreate, db: Session = Depends(get_db)):
    """Tambah kelas baru"""
    try:
        if payload.prodi not in ("TIF", "MIF", "TKK"):
            raise HTTPException(status_code=400, detail="Prodi harus salah satu dari: TIF, MIF, TKK")

        new_kelas = Kelas(
            nama_kelas=payload.nama_kelas,
            prodi=payload.prodi,
            tahun_angkatan=payload.tahun_angkatan,
            golongan=payload.golongan
        )
        db.add(new_kelas)
        db.commit()
        db.refresh(new_kelas)
        return new_kelas
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔴 Error create_kelas: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal menambah kelas: {str(e)}")
