"""
Ministry Configuration Model
Lưu trữ cấu hình của Bộ Giáo Dục (chỉ có 1 bản ghi duy nhất)
"""

from sqlalchemy import Column, Integer, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database.database import Base


class MinistryConfig(Base):
    """
    Bảng cấu hình Bộ Giáo Dục
    CHỈ có 1 bản ghi duy nhất (id=1)
    """
    __tablename__ = "ministry_config"
    
    id = Column(Integer, primary_key=True, default=1)
    public_key = Column(Text, nullable=False)
    initialized = Column(Boolean, default=False)  # Đã init trên Blockchain chưa?
    created_at = Column(DateTime(timezone=True), server_default=func.now())
