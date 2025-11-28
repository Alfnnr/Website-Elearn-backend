from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class KelasMatKuliah(Base):
    __tablename__ = "kelas_mata_kuliah"
    
    id_kelas_mk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kode_mk = Column(String(20), ForeignKey("mata_kuliah.kode_mk", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_kelas = Column(Integer, ForeignKey("kelas.id_kelas", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_dosen = Column(Integer, ForeignKey("dosen.id_dosen", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    tahun_ajaran = Column(String(20), nullable=False, default="2024/2025")
    semester_aktif = Column(Enum("Ganjil", "Genap", name="semester_enum"), nullable=False, default="Ganjil")
    status = Column(Enum("Aktif", "Selesai", "Batal", name="status_kelas_mk_enum"), default="Aktif")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    mata_kuliah = relationship("MataKuliah", back_populates="kelas_mata_kuliah")
    kelas = relationship("Kelas", back_populates="kelas_mata_kuliah")
    dosen = relationship("Dosen", back_populates="kelas_mata_kuliah")
