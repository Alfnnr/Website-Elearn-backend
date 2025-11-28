from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from app.core.database import get_db
from datetime import date

router = APIRouter(prefix="/dashboard", tags=["Dashboard"]) 

# Pydantic models defined in this route file as requested
class SuperadminSummary(BaseModel):
    total_admin: int
    total_mahasiswa: int
    total_mata_kuliah: int
    total_kelas: int
    total_materi: int
    presensi_hari_ini: int

@router.get("/superadmin/summary", response_model=SuperadminSummary)
def get_superadmin_summary(db: Session = Depends(get_db)):
    try:
        # counts via single roundtrip for performance
        queries = {
            # Count from dosen table (admin users with dosen profile)
            "total_admin": "SELECT COUNT(*) AS c FROM dosen",
            "total_mahasiswa": "SELECT COUNT(*) AS c FROM mahasiswa",
            "total_mata_kuliah": "SELECT COUNT(*) AS c FROM mata_kuliah",
            "total_kelas": "SELECT COUNT(*) AS c FROM kelas",
            "total_materi": "SELECT COUNT(*) AS c FROM materi",
            # Count distinct sessions created for today (kode_mk,tanggal,pertemuan_ke)
            "presensi_hari_ini": "SELECT COUNT(DISTINCT CONCAT(kode_mk,'|',tanggal,'|',pertemuan_ke)) AS c FROM presensi WHERE tanggal = CURDATE()",
        }

        results = {}
        for key, sql in queries.items():
            row = db.execute(text(sql)).fetchone()
            results[key] = int(row.c) if row and hasattr(row, 'c') else 0

        return SuperadminSummary(
            total_admin=results.get("total_admin", 0),
            total_mahasiswa=results.get("total_mahasiswa", 0),
            total_mata_kuliah=results.get("total_mata_kuliah", 0),
            total_kelas=results.get("total_kelas", 0),
            total_materi=results.get("total_materi", 0),
            presensi_hari_ini=results.get("presensi_hari_ini", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil ringkasan dashboard: {str(e)}")
