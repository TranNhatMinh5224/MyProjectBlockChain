"""
Verify Schemas
Pydantic models for diploma verification
"""

from pydantic import BaseModel, Field
from typing import Optional


# ==================== RESPONSE SCHEMAS ====================

class VerificationResult(BaseModel):
    """Result of diploma verification"""
    is_valid: bool = Field(..., description="Whether diploma is valid")
    file_hash: str
    diploma_id: Optional[str] = None
    school_id: Optional[str] = None
    school_name: Optional[str] = None
    student_name: Optional[str] = None
    student_id: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    issue_date: Optional[str] = None
    status: Optional[str] = Field(None, description="ACTIVE/REVOKED")
    signature: Optional[str] = None
    signature_valid: Optional[bool] = None
    school_status: Optional[str] = Field(None, description="ACTIVE/REVOKED")
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "file_hash": "abc123def456...",
                "diploma_id": "D2024001",
                "school_id": "HUST",
                "school_name": "Đại học Bách Khoa Hà Nội",
                "student_name": "Nguyễn Văn A",
                "student_id": "SV001",
                "major": "Computer Science",
                "grade": "Excellent",
                "issue_date": "2024-06-15",
                "status": "ACTIVE",
                "signature": "0x1a2b3c...",
                "signature_valid": True,
                "school_status": "ACTIVE",
                "message": "✅ Diploma is valid and verified on blockchain"
            }
        }


class VerificationError(BaseModel):
    """Error response for verification"""
    is_valid: bool = False
    file_hash: Optional[str] = None
    error: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": False,
                "file_hash": "abc123...",
                "error": "DIPLOMA_NOT_FOUND",
                "message": "❌ Diploma not found on blockchain"
            }
        }
