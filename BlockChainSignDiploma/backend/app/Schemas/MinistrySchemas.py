"""
Ministry Schemas
Pydantic models for Ministry operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== REQUEST SCHEMAS ====================

class ApproveCSRRequest(BaseModel):
    """Request to approve a CSR"""
    registered_date: str = Field(..., description="Ngày đăng ký (YYYY-MM-DD)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "registered_date": "2024-01-15"
            }
        }


class RejectCSRRequest(BaseModel):
    """Request to reject a CSR"""
    reason: str = Field(..., min_length=10, description="Lý do từ chối")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Thiếu giấy tờ pháp lý"
            }
        }


class RevokeSchoolRequest(BaseModel):
    """Request to revoke school's authority"""
    reason: str = Field(..., min_length=10, description="Lý do thu hồi quyền")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Vi phạm quy định cấp bằng"
            }
        }


# ==================== RESPONSE SCHEMAS ====================

class CSRListItem(BaseModel):
    """CSR item in list"""
    id: str
    schoolId: str
    schoolName: str
    email: str
    status: str
    createdAt: str
    approvedAt: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "csr_123456",
                "schoolId": "HUST",
                "schoolName": "Đại học Bách Khoa Hà Nội",
                "email": "contact@hust.edu.vn",
                "status": "PENDING",
                "createdAt": "2024-01-15T10:30:00Z",
                "approvedAt": None
            }
        }


class CSRDetailResponse(BaseModel):
    """Detailed CSR information"""
    id: str
    schoolId: str
    schoolName: str
    publicKey: str
    email: str
    address: Optional[str]
    taxCode: Optional[str]
    legalRepresentative: Optional[str]
    phone: Optional[str]
    status: str
    createdAt: str
    approvedAt: Optional[str]
    rejectionReason: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "csr_123456",
                "schoolId": "HUST",
                "schoolName": "Đại học Bách Khoa Hà Nội",
                "publicKey": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
                "email": "contact@hust.edu.vn",
                "address": "Số 1 Đại Cồ Việt, Hà Nội",
                "taxCode": "0100100100",
                "legalRepresentative": "GS. Nguyễn Văn A",
                "phone": "024-3869-2008",
                "status": "PENDING",
                "createdAt": "2024-01-15T10:30:00Z",
                "approvedAt": None,
                "rejectionReason": None
            }
        }


class ApproveCSRResponse(BaseModel):
    """Response after approving CSR"""
    csr_id: str
    school_id: str
    status: str
    certificate: str
    approved_at: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "csr_id": "csr_123456",
                "school_id": "HUST",
                "status": "APPROVED",
                "certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
                "approved_at": "2024-01-15T14:00:00Z",
                "message": "School registered successfully on blockchain"
            }
        }


class SchoolListItem(BaseModel):
    """School item in list"""
    school_id: str
    name: str
    status: str
    registered_date: str
    total_diplomas: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "school_id": "HUST",
                "name": "Đại học Bách Khoa Hà Nội",
                "status": "ACTIVE",
                "registered_date": "2024-01-15",
                "total_diplomas": 1250
            }
        }


class SystemStatistics(BaseModel):
    """System-wide statistics"""
    total_schools: int
    active_schools: int
    revoked_schools: int
    total_diplomas: int
    pending_csrs: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_schools": 50,
                "active_schools": 48,
                "revoked_schools": 2,
                "total_diplomas": 125000,
                "pending_csrs": 3
            }
        }
