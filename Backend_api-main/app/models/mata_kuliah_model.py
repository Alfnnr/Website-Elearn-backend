from sqlalchemy import Column, String, Integer, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MataKuliah(Base):
    __tablename__ = "mata_kuliah"
    
    kode_mk = Column(String(20), primary_key=True, index=True)
    nama_mk = Column(String(200), nullable=False)
    sks = Column(Integer)
    semester = Column(Integer)
    deskripsi = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    kelas_mata_kuliah = relationship("KelasMatKuliah", back_populates="mata_kuliah", cascade="all, delete-orphan")
    materi_list = relationship("Materi", back_populates="mata_kuliah", cascade="all, delete-orphan")