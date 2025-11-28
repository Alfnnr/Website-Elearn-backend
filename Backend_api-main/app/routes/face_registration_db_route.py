# app/routes/face_registration_db_route.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.face_registration_model import FaceRegistration
from app.models.mahasiswa_model import Mahasiswa
from app.schemas.face_registration_schema import (
    FaceRegistrationCreate,
    FaceRegistrationResponse,
    FaceVerificationRequest,
    FaceVerificationResponse
)
from typing import List
from datetime import datetime

router = APIRouter(prefix="/face-registration", tags=["Face Registration DB"])

@router.post("/register", response_model=FaceRegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_face_to_db(
    registration: FaceRegistrationCreate,
    db: Session = Depends(get_db)
):
    """
    Register mahasiswa's face embedding metadata to database.
    Called AFTER mobile app successfully saves the .pkl file via /face/register
    """
    # Check if mahasiswa exists
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.nim == registration.nim).first()
    if not mahasiswa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mahasiswa with NIM {registration.nim} not found"
        )
    
    # Check if already registered
    existing = db.query(FaceRegistration).filter(FaceRegistration.nim == registration.nim).first()
    if existing:
        # Update existing registration
        existing.embedding_filename = registration.embedding_filename
        existing.registration_date = datetime.now()
        existing.is_active = True
        existing.failed_attempts = 0
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new registration
    new_registration = FaceRegistration(
        nim=registration.nim,
        embedding_filename=registration.embedding_filename
    )
    
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)
    
    return new_registration


@router.post("/verify", response_model=FaceVerificationResponse)
def verify_face_update_stats(
    verification: FaceVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Update verification statistics after successful face match.
    Called AFTER mobile app successfully verifies face via /face/verify
    """
    # Check if face is registered
    face_reg = db.query(FaceRegistration).filter(
        FaceRegistration.nim == verification.nim,
        FaceRegistration.is_active == True
    ).first()
    
    if not face_reg:
        return FaceVerificationResponse(
            success=False,
            message="Face not registered or inactive"
        )
    
    # Check confidence threshold
    CONFIDENCE_THRESHOLD = 70.0  # 70%
    
    if verification.confidence_score >= CONFIDENCE_THRESHOLD:
        # Successful verification
        face_reg.last_verified = datetime.now()
        face_reg.verification_count += 1
        face_reg.failed_attempts = 0  # Reset failed attempts on success
        db.commit()
        
        return FaceVerificationResponse(
            success=True,
            message="Face verified successfully",
            confidence_score=verification.confidence_score,
            nim=verification.nim
        )
    else:
        # Failed verification
        face_reg.failed_attempts += 1
        
        # Auto-disable after too many failures
        if face_reg.failed_attempts >= 10:
            face_reg.is_active = False
            
        db.commit()
        
        return FaceVerificationResponse(
            success=False,
            message=f"Face verification failed. Confidence too low: {verification.confidence_score}%",
            confidence_score=verification.confidence_score
        )


@router.get("/status/{nim}", response_model=FaceRegistrationResponse)
def get_registration_status(
    nim: str,
    db: Session = Depends(get_db)
):
    """Get face registration status for a mahasiswa"""
    face_reg = db.query(FaceRegistration).filter(FaceRegistration.nim == nim).first()
    
    if not face_reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No face registration found for NIM {nim}"
        )
    
    return face_reg


@router.get("/all", response_model=List[FaceRegistrationResponse])
def get_all_registrations(
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Get all face registrations (for admin monitoring)"""
    query = db.query(FaceRegistration)
    
    if is_active is not None:
        query = query.filter(FaceRegistration.is_active == is_active)
    
    registrations = query.order_by(FaceRegistration.registration_date.desc()).all()
    return registrations


@router.put("/{nim}/toggle-active")
def toggle_face_active(
    nim: str,
    is_active: bool,
    db: Session = Depends(get_db)
):
    """Enable or disable face recognition for a mahasiswa"""
    face_reg = db.query(FaceRegistration).filter(FaceRegistration.nim == nim).first()
    
    if not face_reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No face registration found for NIM {nim}"
        )
    
    face_reg.is_active = is_active
    if is_active:
        face_reg.failed_attempts = 0  # Reset failed attempts when re-enabling
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Face recognition {'enabled' if is_active else 'disabled'} for {nim}",
        "is_active": is_active
    }


@router.delete("/{nim}")
def delete_face_registration(
    nim: str,
    db: Session = Depends(get_db)
):
    """
    Delete face registration from database (admin only).
    WARNING: Remember to also delete the .pkl file manually from embeddings folder!
    """
    face_reg = db.query(FaceRegistration).filter(FaceRegistration.nim == nim).first()
    
    if not face_reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No face registration found for NIM {nim}"
        )
    
    embedding_filename = face_reg.embedding_filename
    
    db.delete(face_reg)
    db.commit()
    
    return {
        "success": True,
        "message": f"Face registration deleted for {nim}",
        "note": f"Remember to manually delete file: embeddings/{embedding_filename}"
    }
