"""
School Schemas - Pydantic Models for School Operations
Input/Output validation for School endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional


# ==================== PUSH TO FABRIC ====================

class PushToFabricRequest(BaseModel):
    """Request to push diploma to Fabric"""
    file_hash: str = Field(..., description="SHA-256 hash của file")
    signature: str = Field(..., description="Chữ ký số (hex)")
    diploma_id: str = Field(..., description="Mã số văn bằng")
    school_id: str = Field(..., description="Mã trường")
    student_name: str = Field(..., description="Tên sinh viên")
    student_id: str = Field(..., description="Mã sinh viên")
    major: str = Field(..., description="Ngành học")
    grade: str = Field(..., description="Xếp loại")
    issue_date: str = Field(..., description="Ngày cấp (YYYY-MM-DD)")


class PushToFabricResponse(BaseModel):
    """Response after pushing to Fabric"""
    diploma_id: str
    file_hash: str
    student_name: str
    status: str
    pushed_at: str


# ==================== REVOKE DIPLOMA ====================

class RevokeDiplomaRequest(BaseModel):
    """Request to revoke a diploma"""
    file_hash: str = Field(..., description="Hash của file PDF")
    reason: str = Field(..., description="Lý do thu hồi")


class RevokeDiplomaResponse(BaseModel):
    """Response after revoking diploma"""
    file_hash: str
    status: str
    reason: str
    revoked_at: str
    revoked_by: str


# ==================== LIST DIPLOMAS ====================

class DiplomaInfo(BaseModel):
    """Diploma information"""
    diplomaId: str
    studentName: str
    studentId: str
    issueDate: str
    status: str


class ListDiplomasResponse(BaseModel):
    """Response for list diplomas"""
    total: int
    diplomas: list[DiplomaInfo]
