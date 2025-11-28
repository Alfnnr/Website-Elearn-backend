from sqlalchemy import Column, Integer, String, Enum, Boolean
from app.core.database import Base
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"  # Admin
    super_admin = "super_admin"  # Super Admin
    mahasiswa = "mahasiswa"  # Mahasiswa

class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
