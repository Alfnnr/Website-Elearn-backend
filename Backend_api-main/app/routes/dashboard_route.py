from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from app.core.database import get_db
from datetime import date, datetime
from typing import List

router = APIRouter(prefix="/dashboard", tags=["Dashboard"]) 

# Response schemas
class DashboardStats(BaseModel):
    total_kelas_mk: int
    total_mahasiswa: int
    total_materi: int
    presensi_hari_ini: int

class RecentPresensi(BaseModel):
    id_kelas_mk: int
    nama_mk: str
    kelas: str
    tanggal: date
    pertemuan_ke: int
    total_mhs: int
    hadir: int
    alfa: int

class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_presensi: List[RecentPresensi]

@router.get("/stats", response_model=DashboardResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics: total kelas MK, mahasiswa, materi, presensi hari ini
    Plus 5 presensi terbaru
    """
    try:
        # 1. Get statistics
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM kelas_mata_kuliah WHERE status = 'Aktif') as total_kelas_mk,
                (SELECT COUNT(*) FROM mahasiswa) as total_mahasiswa,
                (SELECT COUNT(*) FROM materi) as total_materi,
                (SELECT COUNT(DISTINCT CONCAT(id_kelas_mk,'|',tanggal,'|',pertemuan_ke)) 
                 FROM presensi WHERE tanggal = CURDATE()) as presensi_hari_ini
        """
        stats_result = db.execute(text(stats_query)).fetchone()
        
        # 2. Get 5 recent presensi
        recent_query = """
            SELECT 
                p.id_kelas_mk,
                p.tanggal,
                p.pertemuan_ke,
                mk.nama_mk,
                k.nama_kelas,
                COUNT(p.id_presensi) as total_mhs,
                SUM(CASE WHEN p.status = 'Hadir' THEN 1 ELSE 0 END) as hadir,
                SUM(CASE WHEN p.status = 'Alfa' THEN 1 ELSE 0 END) as alfa
            FROM presensi p
            JOIN kelas_mata_kuliah km ON p.id_kelas_mk = km.id_kelas_mk
            JOIN mata_kuliah mk ON km.kode_mk = mk.kode_mk
            JOIN kelas k ON km.id_kelas = k.id_kelas
            GROUP BY p.id_kelas_mk, p.tanggal, p.pertemuan_ke, mk.nama_mk, k.nama_kelas
            ORDER BY p.tanggal DESC, p.pertemuan_ke DESC
            LIMIT 5
        """
        recent_results = db.execute(text(recent_query)).fetchall()
        
        # Format response
        stats = DashboardStats(
            total_kelas_mk=stats_result.total_kelas_mk or 0,
            total_mahasiswa=stats_result.total_mahasiswa or 0,
            total_materi=stats_result.total_materi or 0,
            presensi_hari_ini=stats_result.presensi_hari_ini or 0
        )
        
        recent_presensi = [
            RecentPresensi(
                id_kelas_mk=row.id_kelas_mk,
                nama_mk=row.nama_mk,
                kelas=row.nama_kelas,
                tanggal=row.tanggal,
                pertemuan_ke=row.pertemuan_ke,
                total_mhs=row.total_mhs or 0,
                hadir=row.hadir or 0,
                alfa=row.alfa or 0
            )
            for row in recent_results
        ]
        
        return DashboardResponse(
            stats=stats,
            recent_presensi=recent_presensi
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Gagal mengambil data dashboard: {str(e)}"
        )
