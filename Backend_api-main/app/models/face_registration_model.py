# app/models/face_registration_model.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class FaceRegistration(Base):
    __tablename__ = "face_registrations"
    
    id_registration = Column(Integer, primary_key=True, autoincrement=True)
    nim = Column(String(20), ForeignKey("mahasiswa.nim", ondelete="CASCADE"), unique=True, nullable=False)
    embedding_filename = Column(String(255), nullable=False, comment="Filename of .pkl file in embeddings folder")
    registration_date = Column(DateTime, server_default=func.current_timestamp())
    last_verified = Column(DateTime, nullable=True, comment="Last successful face verification")
    verification_count = Column(Integer, default=0, comment="Total number of successful verifications")
    failed_attempts = Column(Integer, default=0, comment="Number of failed verification attempts")
    is_active = Column(Boolean, default=True, comment="Can be set to false to disable face login")
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
