from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum

class RoleName(enum.Enum):
    """
    Roles trong hệ thống
    - USER: Người dùng thông thường (có thể ký file)
    - ADMIN: Quản trị viên (nếu cần)
    """
    USER = "USER"
    ADMIN = "ADMIN"

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(Enum(RoleName), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="role")
