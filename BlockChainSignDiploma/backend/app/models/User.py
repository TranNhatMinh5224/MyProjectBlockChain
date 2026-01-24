from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # Role (SCHOOL, MINISTRY)
    role_name = Column(String(50), nullable=True)  # "SCHOOL", "MINISTRY"
    
    # School specific fields
    school_id = Column(String(50), nullable=True)  # "HUST", "NEU"
    school_name = Column(String(255), nullable=True)  # "Đại Học Bách Khoa HN"
    
    # Status
    status = Column(String(50), default="PENDING")  # "PENDING", "ACTIVE", "REVOKED"
    
    # Optional: Thông tin người dùng
    full_name = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Legacy relationship (keep for backward compatibility)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", back_populates="users")

