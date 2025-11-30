# app/models/face_registration_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class FaceRegistration(Base):
    __tablename__ = "face_registrations"
    
    id_registration = Column(Integer, primary_key=True, autoincrement=True)
    nim = Column(String(20), ForeignKey("mahasiswa.nim", ondelete="CASCADE"), unique=True, nullable=False)
    embedding_filename = Column(String(255), nullable=False, comment="Filename of .pkl file in embeddings folder")
    registration_date = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
