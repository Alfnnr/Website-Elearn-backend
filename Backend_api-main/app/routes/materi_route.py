# # app/routes/materi_route.py
# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from app.core.database import get_db
# from app.models.materi_model import Materi
# from app.models.mata_kuliah_model import MataKuliah
# from app.schemas.materi_schema import MateriResponse, MateriCreate, MateriUpdate
# import shutil
# import os
# from pathlib import Path

# router = APIRouter(prefix="/materi", tags=["Materi"])

# # Direktori untuk menyimpan file PDF
# UPLOAD_DIR = Path("uploads/materi")
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# @router.get("/", response_model=List[MateriResponse])
# def get_all_materi(db: Session = Depends(get_db)):
#     """Ambil semua materi"""
#     materi = db.query(Materi).all()
#     return materi


# @router.get("/{kode_mk}", response_model=List[MateriResponse])
# def get_materi_by_matkul(kode_mk: str, db: Session = Depends(get_db)):
#     """Ambil semua materi berdasarkan kode mata kuliah"""
#     # Cek apakah mata kuliah ada
#     matkul = db.query(MataKuliah).filter(MataKuliah.kode_mk == kode_mk).first()
#     if not matkul:
#         raise HTTPException(status_code=404, detail="Mata kuliah tidak ditemukan")
    
#     materi = db.query(Materi).filter(Materi.kode_mk == kode_mk).order_by(Materi.minggu).all()
#     return materi


# @router.get("/minggu/{kode_mk}/{minggu}", response_model=MateriResponse)
# def get_materi_by_minggu(kode_mk: str, minggu: int, db: Session = Depends(get_db)):
#     """Ambil materi berdasarkan kode mata kuliah dan minggu"""
#     if minggu < 1 or minggu > 16:
#         raise HTTPException(status_code=400, detail="Minggu harus antara 1-16")
    
#     materi = db.query(Materi).filter(
#         Materi.kode_mk == kode_mk,
#         Materi.minggu == minggu
#     ).first()
    
#     if not materi:
#         raise HTTPException(status_code=404, detail="Materi tidak ditemukan")
    
#     return materi


# @router.post("/", response_model=MateriResponse, status_code=201)
# async def create_materi(
#     kode_mk: str = Form(...),
#     minggu: int = Form(...),
#     judul: str = Form(...),
#     deskripsi: Optional[str] = Form(None),
#     file_pdf: Optional[UploadFile] = File(None),
#     db: Session = Depends(get_db)
# ):
#     """Tambah materi baru"""
#     # Validasi minggu
#     if minggu < 1 or minggu > 16:
#         raise HTTPException(status_code=400, detail="Minggu harus antara 1-16")
    
#     # Cek apakah mata kuliah ada
#     matkul = db.query(MataKuliah).filter(MataKuliah.kode_mk == kode_mk).first()
#     if not matkul:
#         raise HTTPException(status_code=404, detail="Mata kuliah tidak ditemukan")
    
#     # Cek apakah materi untuk minggu ini sudah ada
#     existing = db.query(Materi).filter(
#         Materi.kode_mk == kode_mk,
#         Materi.minggu == minggu
#     ).first()
    
#     if existing:
#         raise HTTPException(
#             status_code=400, 
#             detail=f"Materi untuk minggu {minggu} sudah ada"
#         )
    
#     # Handle file upload
#     file_path = None
#     if file_pdf:
#         if not file_pdf.filename.endswith('.pdf'):
#             raise HTTPException(status_code=400, detail="File harus berformat PDF")
        
#         # Buat nama file unik
#         file_name = f"{kode_mk}_minggu{minggu}_{file_pdf.filename}"
#         file_path = UPLOAD_DIR / file_name
        
#         # Simpan file
#         with file_path.open("wb") as buffer:
#             shutil.copyfileobj(file_pdf.file, buffer)
        
#         file_path = str(file_name)  # Simpan hanya nama file
    
#     # Buat materi baru
#     new_materi = Materi(
#         kode_mk=kode_mk,
#         minggu=minggu,
#         judul=judul,
#         deskripsi=deskripsi,
#         file_pdf=file_path
#     )
    
#     db.add(new_materi)
#     db.commit()
#     db.refresh(new_materi)
    
#     return new_materi


# @router.put("/{id_materi}", response_model=MateriResponse)
# async def update_materi(
#     id_materi: int,
#     judul: Optional[str] = Form(None),
#     deskripsi: Optional[str] = Form(None),
#     minggu: Optional[int] = Form(None),
#     file_pdf: Optional[UploadFile] = File(None),
#     db: Session = Depends(get_db)
# ):
#     """Update materi"""
#     materi = db.query(Materi).filter(Materi.id_materi == id_materi).first()
#     if not materi:
#         raise HTTPException(status_code=404, detail="Materi tidak ditemukan")
    
#     # Validasi minggu jika diubah
#     if minggu is not None:
#         if minggu < 1 or minggu > 16:
#             raise HTTPException(status_code=400, detail="Minggu harus antara 1-16")
        
#         # Cek apakah minggu baru sudah digunakan
#         existing = db.query(Materi).filter(
#             Materi.kode_mk == materi.kode_mk,
#             Materi.minggu == minggu,
#             Materi.id_materi != id_materi
#         ).first()
        
#         if existing:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Materi untuk minggu {minggu} sudah ada"
#             )
        
#         materi.minggu = minggu
    
#     # Update fields
#     if judul is not None:
#         materi.judul = judul
#     if deskripsi is not None:
#         materi.deskripsi = deskripsi
    
#     # Handle file upload baru
#     if file_pdf:
#         if not file_pdf.filename.endswith('.pdf'):
#             raise HTTPException(status_code=400, detail="File harus berformat PDF")
        
#         # Hapus file lama jika ada
#         if materi.file_pdf:
#             old_file = UPLOAD_DIR / materi.file_pdf
#             if old_file.exists():
#                 old_file.unlink()
        
#         # Simpan file baru
#         file_name = f"{materi.kode_mk}_minggu{materi.minggu}_{file_pdf.filename}"
#         file_path = UPLOAD_DIR / file_name
        
#         with file_path.open("wb") as buffer:
#             shutil.copyfileobj(file_pdf.file, buffer)
        
#         materi.file_pdf = str(file_name)
    
#     db.commit()
#     db.refresh(materi)
    
#     return materi


# @router.delete("/{id_materi}")
# def delete_materi(id_materi: int, db: Session = Depends(get_db)):
#     """Hapus materi"""
#     materi = db.query(Materi).filter(Materi.id_materi == id_materi).first()
#     if not materi:
#         raise HTTPException(status_code=404, detail="Materi tidak ditemukan")
    
#     # Hapus file PDF jika ada
#     if materi.file_pdf:
#         file_path = UPLOAD_DIR / materi.file_pdf
#         if file_path.exists():
#             file_path.unlink()
    
#     db.delete(materi)
#     db.commit()
    
#     return {"message": "Materi berhasil dihapus", "id_materi": id_materi}

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.materi_model import Materi
from app.models.mata_kuliah_model import MataKuliah
from app.models.dosen_model import Dosen
from app.schemas.materi_schema import MateriResponse
import shutil
import os
from pathlib import Path
import uuid
import mimetypes

router = APIRouter(prefix="/materi", tags=["Materi"])

# Direktori untuk menyimpan file PDF
UPLOAD_DIR = Path("uploads/materi")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===========================
# GET SEMUA MATERI (with optional filters)
# ===========================
@router.get("/", response_model=List[MateriResponse])
def get_all_materi(
    kode_mk: Optional[str] = None,
    id_kelas: Optional[int] = None,
    minggu: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Ambil semua materi dengan filter opsional (shared per kode_mk + id_kelas)"""
    query = db.query(Materi)
    
    # Filter by kode_mk
    if kode_mk is not None:
        query = query.filter(Materi.kode_mk == kode_mk)
    
    # Filter by id_kelas
    if id_kelas is not None:
        query = query.filter(Materi.id_kelas == id_kelas)
    
    # Filter by minggu
    if minggu is not None:
        if minggu < 1 or minggu > 16:
            raise HTTPException(status_code=400, detail="Minggu harus antara 1-16")
        query = query.filter(Materi.minggu == minggu)
    
    materi_list = query.order_by(Materi.minggu, Materi.tanggal_upload).all()
    
    # Enrich with nama_dosen
    result = []
    for materi in materi_list:
        materi_dict = {
            "id_materi": materi.id_materi,
            "kode_mk": materi.kode_mk,
            "id_kelas": materi.id_kelas,
            "minggu": materi.minggu,
            "judul": materi.judul,
            "deskripsi": materi.deskripsi,
            "file_pdf": materi.file_pdf,
            "uploaded_by": materi.uploaded_by,
            "tanggal_upload": materi.tanggal_upload,
            "nama_dosen": None
        }
        
        # Fetch nama dosen if uploaded_by exists
        if materi.uploaded_by:
            dosen = db.query(Dosen).filter(Dosen.id_dosen == materi.uploaded_by).first()
            if dosen:
                materi_dict["nama_dosen"] = dosen.nama_dosen
        
        result.append(materi_dict)
    
    return result


# ===========================
# CREATE MATERI BARU
# ===========================
@router.post("/", response_model=MateriResponse, status_code=201)
async def create_materi(
    kode_mk: str = Form(...),
    id_kelas: int = Form(...),
    minggu: int = Form(...),
    judul: str = Form(...),
    deskripsi: Optional[str] = Form(None),
    uploaded_by: Optional[int] = Form(None),
    file_pdf: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Tambah materi baru — shared per kode_mk + id_kelas, tracked by uploaded_by"""
    try:
        # Validasi minggu
        if minggu < 1 or minggu > 16:
            raise HTTPException(status_code=400, detail="Minggu harus antara 1–16")

        # Handle file upload (jika ada)
        file_name = None
        if file_pdf:
            if not file_pdf.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="File harus berformat PDF")

            mime_type, _ = mimetypes.guess_type(file_pdf.filename)
            if mime_type != "application/pdf":
                raise HTTPException(status_code=400, detail="File bukan PDF yang valid")

            # Buat nama file unik agar tidak bentrok
            safe_filename = f"{kode_mk}_kelas{id_kelas}_minggu{minggu}_{uuid.uuid4().hex}.pdf"
            file_path = UPLOAD_DIR / safe_filename

            try:
                with file_path.open("wb") as buffer:
                    shutil.copyfileobj(file_pdf.file, buffer)
                file_name = safe_filename
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Gagal menyimpan file: {e}")

        # Simpan ke database
        new_materi = Materi(
            kode_mk=kode_mk,
            id_kelas=id_kelas,
            minggu=minggu,
            judul=judul,
            deskripsi=deskripsi,
            file_pdf=file_name,
            uploaded_by=uploaded_by,
        )

        db.add(new_materi)
        db.commit()
        db.refresh(new_materi)

        return new_materi
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ===========================
# UPDATE MATERI
# ===========================
@router.put("/{id_materi}", response_model=MateriResponse)
async def update_materi(
    id_materi: int,
    judul: Optional[str] = Form(None),
    deskripsi: Optional[str] = Form(None),
    minggu: Optional[int] = Form(None),
    file_pdf: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Update materi"""
    materi = db.query(Materi).filter(Materi.id_materi == id_materi).first()
    if not materi:
        raise HTTPException(status_code=404, detail="Materi tidak ditemukan")

    # Validasi minggu
    if minggu is not None:
        if minggu < 1 or minggu > 16:
            raise HTTPException(status_code=400, detail="Minggu harus antara 1–16")
        materi.minggu = minggu

    # Update data umum
    if judul is not None:
        materi.judul = judul
    if deskripsi is not None:
        materi.deskripsi = deskripsi

    # Ganti file jika ada upload baru
    if file_pdf:
        if not file_pdf.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="File harus berformat PDF")

        mime_type, _ = mimetypes.guess_type(file_pdf.filename)
        if mime_type != "application/pdf":
            raise HTTPException(status_code=400, detail="File bukan PDF yang valid")

        # Hapus file lama jika ada
        if materi.file_pdf:
            old_file = UPLOAD_DIR / materi.file_pdf
            if old_file.exists():
                old_file.unlink()

        # Simpan file baru
        new_filename = f"{materi.kode_mk}_kelas{materi.id_kelas}_minggu{materi.minggu}_{uuid.uuid4().hex}.pdf"
        new_path = UPLOAD_DIR / new_filename

        try:
            with new_path.open("wb") as buffer:
                shutil.copyfileobj(file_pdf.file, buffer)
            materi.file_pdf = new_filename
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gagal menyimpan file baru: {e}")

    db.commit()
    db.refresh(materi)

    return materi


# ===========================
# DELETE MATERI
# ===========================
@router.delete("/{id_materi}")
def delete_materi(id_materi: int, db: Session = Depends(get_db)):
    """Hapus materi"""
    materi = db.query(Materi).filter(Materi.id_materi == id_materi).first()
    if not materi:
        raise HTTPException(status_code=404, detail="Materi tidak ditemukan")

    # Hapus file PDF jika ada
    if materi.file_pdf:
        file_path = UPLOAD_DIR / materi.file_pdf
        if file_path.exists():
            file_path.unlink()

    db.delete(materi)
    db.commit()

    return {"message": "Materi berhasil dihapus", "id_materi": id_materi}


# ===========================
# PREVIEW/VIEW FILE MATERI (INLINE)
# ===========================
@router.get("/view/{id_materi}")
def view_file_materi(id_materi: int, db: Session = Depends(get_db)):
    """Preview file PDF materi di browser (inline)"""
    materi = db.query(Materi).filter(Materi.id_materi == id_materi).first()
    if not materi:
        raise HTTPException(status_code=404, detail="Materi tidak ditemukan")

    if not materi.file_pdf:
        raise HTTPException(status_code=404, detail="File PDF tidak tersedia")

    file_path = UPLOAD_DIR / materi.file_pdf
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File PDF tidak ditemukan di server")

    # Return file dengan header Content-Disposition: inline
    # Ini akan membuat browser membuka PDF di tab baru, bukan mendownload
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{materi.judul}.pdf"'
        }
    )


# ===========================
# DOWNLOAD FILE MATERI (untuk download eksplisit)
# ===========================
@router.get("/download/{id_materi}")
def download_file_materi(id_materi: int, db: Session = Depends(get_db)):
    """Download file PDF materi"""
    materi = db.query(Materi).filter(Materi.id_materi == id_materi).first()
    if not materi:
        raise HTTPException(status_code=404, detail="Materi tidak ditemukan")

    if not materi.file_pdf:
        raise HTTPException(status_code=404, detail="File PDF tidak tersedia")

    file_path = UPLOAD_DIR / materi.file_pdf
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File PDF tidak ditemukan di server")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{materi.judul}.pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{materi.judul}.pdf"'
        }
    )