from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from app.core.database import get_db
from app.models.presensi_model import Presensi
from app.models.mahasiswa_model import Mahasiswa
from app.schemas.presensi_schema import (
    PresensiGenerateRequest, 
    PresensiResponse, 
    PresensiDetailResponse,
    PresensiSummary
)
from typing import List
from datetime import datetime, time, timedelta

router = APIRouter(prefix="/presensi", tags=["Presensi"])

@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_presensi(
    request: PresensiGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate presensi untuk semua mahasiswa di kelas tertentu
    Status default: Alfa (mahasiswa belum hadir)
    """
    
    # Validasi mata kuliah dengan query manual
    mata_kuliah = db.execute(
        text("SELECT kode_mk, nama_mk FROM mata_kuliah WHERE kode_mk = :kode_mk"),
        {"kode_mk": request.kode_mk}
    ).fetchone()
    
    if not mata_kuliah:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mata kuliah dengan kode {request.kode_mk} tidak ditemukan"
        )
    
    # Validasi kelas dengan query manual
    kelas = db.execute(
        text("SELECT id_kelas, nama_kelas FROM kelas WHERE id_kelas = :id_kelas"),
        {"id_kelas": request.id_kelas}
    ).fetchone()
    
    if not kelas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kelas dengan ID {request.id_kelas} tidak ditemukan"
        )
    
    # Cek apakah presensi untuk pertemuan ini sudah dibuat
    existing_presensi = db.query(Presensi).filter(
        and_(
            Presensi.kode_mk == request.kode_mk,
            Presensi.tanggal == request.tanggal,
            Presensi.pertemuan_ke == request.pertemuan_ke
        )
    ).first()
    
    if existing_presensi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Presensi untuk {mata_kuliah.nama_mk} pertemuan ke-{request.pertemuan_ke} pada tanggal {request.tanggal} sudah dibuat"
        )
    
    # Ambil semua mahasiswa di kelas tersebut
    mahasiswa_list = db.query(Mahasiswa).filter(
        Mahasiswa.id_kelas == request.id_kelas
    ).all()
    
    if not mahasiswa_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tidak ada mahasiswa di kelas {kelas.nama_kelas}"
        )
    
    # Generate presensi untuk semua mahasiswa
    presensi_created = []
    for mahasiswa in mahasiswa_list:
        new_presensi = Presensi(
            id_mahasiswa=mahasiswa.id_mahasiswa,
            kode_mk=request.kode_mk,
            tanggal=request.tanggal,
            pertemuan_ke=request.pertemuan_ke,
            status="Belum Absen",  # Default: Belum Absen (bukan Alfa)
            waktu_mulai=request.waktu_mulai,
            waktu_selesai=request.waktu_selesai,
            waktu_input=None  # Belum absen, waktu_input masih NULL
        )
        db.add(new_presensi)
        presensi_created.append({
            "nim": mahasiswa.nim,
            "nama": mahasiswa.nama
        })
    
    db.commit()
    
    return {
        "message": "Presensi berhasil digenerate",
        "data": {
            "kelas": kelas.nama_kelas,
            "mata_kuliah": mata_kuliah.nama_mk,
            "kode_mk": request.kode_mk,
            "pertemuan_ke": request.pertemuan_ke,
            "tanggal": request.tanggal,
            "waktu_mulai": request.waktu_mulai,
            "waktu_selesai": request.waktu_selesai,
            "total_mahasiswa": len(presensi_created),
            "mahasiswa": presensi_created
        }
    }


@router.get("/list", response_model=List[PresensiSummary])
def get_presensi_list(
    kelas: str = None,
    kode_mk: str = None,
    pertemuan_ke: int = None,
    db: Session = Depends(get_db)
):
    """
    Get daftar presensi yang sudah dibuat dengan filter
    """
    
    # Query manual dengan JOIN
    query = """
        SELECT 
            p.kode_mk,
            p.tanggal,
            p.pertemuan_ke,
            p.waktu_mulai,
            p.waktu_selesai,
            COUNT(p.id_presensi) as total_mhs,
            SUM(CASE WHEN p.status = 'Hadir' THEN 1 ELSE 0 END) as hadir,
            SUM(CASE WHEN p.status = 'Alfa' THEN 1 ELSE 0 END) as alpa,
            mk.nama_mk,
            k.nama_kelas
        FROM presensi p
        JOIN mata_kuliah mk ON p.kode_mk = mk.kode_mk
        JOIN mahasiswa m ON p.id_mahasiswa = m.id_mahasiswa
        JOIN kelas k ON m.id_kelas = k.id_kelas
        WHERE 1=1
    """
    
    params = {}
    
    if kode_mk:
        query += " AND p.kode_mk = :kode_mk"
        params["kode_mk"] = kode_mk
    
    if kelas:
        query += " AND k.nama_kelas LIKE :kelas"
        params["kelas"] = f"%{kelas}%"
    
    if pertemuan_ke:
        query += " AND p.pertemuan_ke = :pertemuan_ke"
        params["pertemuan_ke"] = pertemuan_ke
    
    query += """
        GROUP BY p.kode_mk, p.tanggal, p.pertemuan_ke, p.waktu_mulai, p.waktu_selesai, mk.nama_mk, k.nama_kelas
        ORDER BY p.tanggal DESC, p.pertemuan_ke DESC
    """
    
    results = db.execute(text(query), params).fetchall()
    
    # Format response
    response = []
    for idx, result in enumerate(results, start=1):
        # Convert timedelta to string format HH:MM
        waktu_mulai_str = str(result.waktu_mulai) if result.waktu_mulai else "00:00"
        waktu_selesai_str = str(result.waktu_selesai) if result.waktu_selesai else "00:00"
        
        # Handle timedelta format (remove seconds if present)
        if len(waktu_mulai_str) > 5:
            waktu_mulai_str = waktu_mulai_str[:5]  # Get HH:MM only
        if len(waktu_selesai_str) > 5:
            waktu_selesai_str = waktu_selesai_str[:5]  # Get HH:MM only
        
        response.append(PresensiSummary(
            id=idx,
            kelas=result.nama_kelas,
            matkul=result.nama_mk,
            kode_mk=result.kode_mk,
            pertemuan=result.pertemuan_ke,
            tanggal=result.tanggal,
            waktu_mulai=waktu_mulai_str,
            waktu_selesai=waktu_selesai_str,
            total_mhs=result.total_mhs,
            hadir=result.hadir or 0,
            alpa=result.alpa or 0
        ))
    
    return response


@router.get("/detail/{kode_mk}/{tanggal}/{pertemuan_ke}", response_model=List[PresensiDetailResponse])
def get_presensi_detail(
    kode_mk: str,
    tanggal: str,
    pertemuan_ke: int,
    db: Session = Depends(get_db)
):
    """
    Get detail presensi mahasiswa untuk pertemuan tertentu
    Auto-update status "Belum Absen" menjadi "Alfa" jika waktu sudah lewat
    """
    
    # Auto-update status Belum Absen menjadi Alfa jika sudah melewati waktu_selesai
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    
    # Update status yang masih "Belum Absen" menjadi "Alfa" jika sudah lewat waktu
    presensi_list_check = db.query(Presensi).filter(
        and_(
            Presensi.kode_mk == kode_mk,
            Presensi.tanggal == tanggal,
            Presensi.pertemuan_ke == pertemuan_ke,
            Presensi.status == "Belum Absen"
        )
    ).all()
    
    for presensi in presensi_list_check:
        # Jika tanggal presensi sudah lewat ATAU tanggal sama tapi waktu sudah lewat waktu_selesai
        if presensi.tanggal < current_date or \
           (presensi.tanggal == current_date and presensi.waktu_selesai and current_time > presensi.waktu_selesai):
            presensi.status = "Alfa"
    
    db.commit()
    
    # Query manual dengan JOIN
    query = """
        SELECT 
            p.id_presensi,
            p.id_mahasiswa,
            p.status,
            p.waktu_input,
            m.nim,
            m.nama
        FROM presensi p
        JOIN mahasiswa m ON p.id_mahasiswa = m.id_mahasiswa
        WHERE p.kode_mk = :kode_mk 
        AND p.tanggal = :tanggal 
        AND p.pertemuan_ke = :pertemuan_ke
        ORDER BY m.nim
    """
    
    results = db.execute(text(query), {
        "kode_mk": kode_mk,
        "tanggal": tanggal,
        "pertemuan_ke": pertemuan_ke
    }).fetchall()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presensi tidak ditemukan"
        )
    
    response = []
    for result in results:
        response.append(PresensiDetailResponse(
            id_presensi=result.id_presensi,
            id_mahasiswa=result.id_mahasiswa,
            nim=result.nim,
            nama_mahasiswa=result.nama,
            status=result.status,
            waktu_input=result.waktu_input
        ))
    
    return response


@router.put("/update-status/{id_presensi}")
def update_status_presensi(
    id_presensi: int,
    status: str,  # "Hadir" atau "Alfa"
    db: Session = Depends(get_db)
):
    """
    Update status presensi mahasiswa (untuk mobile app)
    """
    
    if status not in ["Hadir", "Alfa"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status harus 'Hadir' atau 'Alfa'"
        )
    
    presensi = db.query(Presensi).filter(Presensi.id_presensi == id_presensi).first()
    
    if not presensi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presensi tidak ditemukan"
        )
    
    presensi.status = status
    presensi.waktu_input = datetime.now()
    
    db.commit()
    db.refresh(presensi)
    
    return {
        "message": "Status presensi berhasil diupdate",
        "data": {
            "id_presensi": presensi.id_presensi,
            "status": presensi.status,
            "waktu_input": presensi.waktu_input
        }
    }


@router.delete("/delete/{kode_mk}/{tanggal}/{pertemuan_ke}")
def delete_presensi(
    kode_mk: str,
    tanggal: str,
    pertemuan_ke: int,
    db: Session = Depends(get_db)
):
    """
    Hapus presensi untuk pertemuan tertentu (hapus semua mahasiswa)
    """
    
    deleted_count = db.query(Presensi).filter(
        and_(
            Presensi.kode_mk == kode_mk,
            Presensi.tanggal == tanggal,
            Presensi.pertemuan_ke == pertemuan_ke
        )
    ).delete()
    
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presensi tidak ditemukan"
        )
    
    db.commit()
    
    return {
        "message": f"Presensi berhasil dihapus ({deleted_count} record)"
    }
