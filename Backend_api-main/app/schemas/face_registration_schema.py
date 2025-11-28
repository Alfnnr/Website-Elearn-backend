# app/schemas/face_registration_schema.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FaceRegistrationCreate(BaseModel):
    nim: str
    embedding_filename: str

class FaceRegistrationResponse(BaseModel):
    id_registration: int
    nim: str
    embedding_filename: str
    registration_date: datetime
    last_verified: Optional[datetime] = None
    verification_count: int
    failed_attempts: int
    is_active: bool
    
    class Config:
        from_attributes = True

class FaceVerificationRequest(BaseModel):
    nim: str
    confidence_score: float
    verification_photo_path: Optional[str] = None
    device_info: Optional[str] = None
    app_version: Optional[str] = None

class FaceVerificationResponse(BaseModel):
    success: bool
    message: str
    confidence_score: Optional[float] = None
    nim: Optional[str] = None
