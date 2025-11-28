from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class PresensiGenerateRequest(BaseModel):
    id_kelas: int
    kode_mk: str
    pertemuan_ke: int
    tanggal: date
    waktu_mulai: str  # Format: "HH:MM"
    waktu_selesai: str  # Format: "HH:MM"

class PresensiResponse(BaseModel):
    id_presensi: int
    id_mahasiswa: int
    kode_mk: str
    tanggal: date
    pertemuan_ke: int
    status: str
    waktu_input: Optional[datetime]
    waktu_mulai: Optional[str]
    waktu_selesai: Optional[str]
    
    class Config:
        from_attributes = True

class PresensiDetailResponse(BaseModel):
    id_presensi: int
    id_mahasiswa: int
    nim: str
    nama_mahasiswa: str
    status: str
    waktu_input: Optional[datetime]
    
    class Config:
        from_attributes = True

class PresensiSummary(BaseModel):
    id: int
    kelas: str
    matkul: str
    kode_mk: str
    pertemuan: int
    tanggal: date
    waktu_mulai: str
    waktu_selesai: str
    total_mhs: int
    hadir: int
    alpa: int
