# app/models/kelas_model.py
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class Kelas(Base):
    __tablename__ = "kelas"
    
    id_kelas = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nama_kelas = Column(String(50), nullable=False)
    prodi = Column(Enum('TIF', 'MIF', 'TKK', name='prodi_enum'), nullable=False)
    tahun_angkatan = Column(Integer, nullable=True)
    golongan = Column(String(10), nullable=True)
    
    # Relationships
    kelas_mata_kuliah = relationship("KelasMatKuliah", back_populates="kelas")