"""
CSR (Certificate Signing Request) Schemas
Pydantic models for CSR input/output validation
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ==================== REQUEST SCHEMAS ====================

class SubmitCSRRequest(BaseModel):
    """Request to submit a Certificate Signing Request"""
    school_name: str = Field(..., min_length=3, max_length=200, description="Tên trường")
    school_id: str = Field(..., min_length=3, max_length=50, description="Mã trường")
    email: EmailStr = Field(..., description="Email liên hệ")
    public_key: str = Field(..., description="Public key (PEM format)")
    csr_data: str = Field(..., description="CSR data (PEM format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "school_name": "Đại học Bách Khoa Hà Nội",
                "school_id": "HUST",
                "email": "contact@hust.edu.vn",
                "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
                "csr_data": "-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----"
            }
        }


# ==================== RESPONSE SCHEMAS ====================

class SubmitCSRResponse(BaseModel):
    """Response after submitting CSR"""
    csr_id: str = Field(..., description="ID của CSR request")
    school_name: str
    school_id: str
    status: str = Field(..., description="PENDING/APPROVED/REJECTED/REVOKED")
    submitted_at: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "csr_id": "csr_123456",
                "school_name": "Đại học Bách Khoa Hà Nội",
                "school_id": "HUST",
                "status": "PENDING",
                "submitted_at": "2024-01-15T10:30:00Z",
                "message": "CSR submitted successfully. Waiting for Ministry approval."
            }
        }


class CSRStatusResponse(BaseModel):
    """Response for CSR status check"""
    csr_id: str
    school_name: str
    school_id: str
    email: str
    status: str = Field(..., description="PENDING/APPROVED/REJECTED/REVOKED")
    submitted_at: str
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    certificate: Optional[str] = Field(None, description="Certificate if approved")
    
    class Config:
        json_schema_extra = {
            "example": {
                "csr_id": "csr_123456",
                "school_name": "Đại học Bách Khoa Hà Nội",
                "school_id": "HUST",
                "email": "contact@hust.edu.vn",
                "status": "APPROVED",
                "submitted_at": "2024-01-15T10:30:00Z",
                "reviewed_at": "2024-01-15T14:00:00Z",
                "reviewed_by": "ministry_admin",
                "rejection_reason": None,
                "certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
            }
        }
