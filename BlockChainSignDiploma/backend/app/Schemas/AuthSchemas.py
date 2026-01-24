"""
Auth Schemas - Pydantic Models for Authentication
Input/Output validation for Auth endpoints
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ==================== REGISTER ====================

class RegisterRequest(BaseModel):
    """Request to register a new school account"""
    email: EmailStr = Field(..., description="School email")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    schoolId: str = Field(..., description="School ID (e.g., HUST)")
    schoolName: str = Field(..., description="Full school name")
    role: str = Field(default="SCHOOL", description="User role")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "daotao@hust.edu.vn",
                "password": "secure123",
                "schoolId": "HUST",
                "schoolName": "Đại Học Bách Khoa Hà Nội",
                "role": "SCHOOL"
            }
        }


class RegisterResponse(BaseModel):
    """Response after successful registration"""
    email: str
    schoolId: str
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "daotao@hust.edu.vn",
                "schoolId": "HUST",
                "status": "PENDING"
            }
        }


# ==================== LOGIN ====================

class LoginRequest(BaseModel):
    """Request to login"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "daotao@hust.edu.vn",
                "password": "secure123"
            }
        }


class UserInfo(BaseModel):
    """User information in login response"""
    username: str
    email: Optional[str] = None
    role: str
    schoolId: Optional[str] = None
    schoolName: Optional[str] = None
    status: str


class LoginResponse(BaseModel):
    """Response after successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGc...",
                "token_type": "bearer",
                "user": {
                    "username": "daotao@hust.edu.vn",
                    "email": "daotao@hust.edu.vn",
                    "role": "SCHOOL",
                    "schoolId": "HUST",
                    "schoolName": "Đại Học Bách Khoa HN",
                    "status": "ACTIVE"
                }
            }
        }
