# app/models/dosen_model.py
from sqlalchemy import Column, Integer, String, Date, Enum, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Dosen(Base):
    __tablename__ = "dosen"
    
    id_dosen = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE", onupdate="CASCADE"), unique=True, nullable=False)
    nip = Column(String(50), unique=True, nullable=False, index=True)
    nama_dosen = Column(String(150), nullable=False)
    email_dosen = Column(String(150), nullable=True)
    tempat_lahir = Column(String(100), nullable=True)
    tanggal_lahir = Column(Date, nullable=True)
    jenis_kelamin = Column(Enum('L', 'P', name='gender_enum'), nullable=True)
    agama = Column(String(50), nullable=True)
    alamat = Column(Text, nullable=True)
    no_hp = Column(String(20), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    kelas_mata_kuliah = relationship("KelasMatKuliah", back_populates="dosen")