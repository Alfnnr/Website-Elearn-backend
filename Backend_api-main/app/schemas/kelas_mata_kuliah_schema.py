from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class KelasMatKuliahBase(BaseModel):
    kode_mk: str
    id_kelas: int
    id_dosen: int
    tahun_ajaran: str = "2024/2025"
    semester_aktif: str = "Ganjil"
    status: str = "Aktif"

class KelasMatKuliahCreate(KelasMatKuliahBase):
    pass

class KelasMatKuliahUpdate(BaseModel):
    tahun_ajaran: Optional[str] = None
    semester_aktif: Optional[str] = None
    status: Optional[str] = None

class KelasMatKuliahResponse(KelasMatKuliahBase):
    id_kelas_mk: int
    created_at: datetime
    updated_at: datetime
    
    # Nested info
    nama_mk: Optional[str] = None
    nama_kelas: Optional[str] = None
    nama_dosen: Optional[str] = None
    
    class Config:
        from_attributes = True

class KelasMatKuliahDetail(KelasMatKuliahResponse):
    """Extended response with full details"""
    sks: Optional[int] = None
    semester: Optional[int] = None
    prodi: Optional[str] = None
    nip: Optional[str] = None
    email_dosen: Optional[str] = None
