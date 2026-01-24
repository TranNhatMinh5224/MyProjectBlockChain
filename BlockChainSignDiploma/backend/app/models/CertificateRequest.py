"""
CSR (Certificate Signing Request) Database Model
Quản lý yêu cầu cấp chứng chỉ từ các trường
"""

from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class CSRStatus(str, enum.Enum):
    """Trạng thái của CSR"""
    PENDING = "PENDING"      # Đang chờ duyệt
    APPROVED = "APPROVED"    # Đã duyệt
    REJECTED = "REJECTED"    # Từ chối
    REVOKED = "REVOKED"      # Đã bị thu hồi


class CertificateRequest(Base):
    """
    Bảng lưu trữ Certificate Signing Requests
    """
    __tablename__ = "certificate_requests"
    
    id = Column(String, primary_key=True, index=True)
    school_id = Column(String, unique=True, nullable=False, index=True)
    school_name = Column(String, nullable=False)
    public_key = Column(Text, nullable=False)
    
    # Thông tin bổ sung của trường
    address = Column(String, nullable=True)
    tax_code = Column(String, nullable=True)
    legal_representative = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # CSR signature (trường tự ký để chứng minh sở hữu private key)
    csr_signature = Column(Text, nullable=False)
    
    # Trạng thái
    status = Column(SQLEnum(CSRStatus), default=CSRStatus.PENDING, nullable=False)
    
    # Certificate (sau khi Bộ ký)
    certificate = Column(Text, nullable=True)
    
    # Lý do từ chối (nếu có)
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String, nullable=True)  # Admin ID
