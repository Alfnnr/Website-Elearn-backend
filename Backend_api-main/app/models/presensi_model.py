from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, TIMESTAMP, Time, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Presensi(Base):
    __tablename__ = "presensi"

    id_presensi = Column(Integer, primary_key=True, autoincrement=True)
    id_mahasiswa = Column(Integer, ForeignKey('mahasiswa.id_mahasiswa', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    kode_mk = Column(String(20), ForeignKey('mata_kuliah.kode_mk', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    tanggal = Column(Date, nullable=False)
    pertemuan_ke = Column(Integer, nullable=False)
    status = Column(Enum("Hadir", "Belum Absen", "Alfa"), default="Belum Absen")
    waktu_input = Column(DateTime, default=None, nullable=True)
    waktu_mulai = Column(Time)  # TIME type
    waktu_selesai = Column(Time)  # TIME type
