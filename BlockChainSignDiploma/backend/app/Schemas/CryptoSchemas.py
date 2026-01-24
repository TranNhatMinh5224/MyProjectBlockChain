"""
Crypto Schemas - Pydantic Models for Validation
Input/Output validation for Crypto endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional


# ==================== GENERATE KEYPAIR ====================

class GenerateKeypairResponse(BaseModel):
    """Response for keypair generation"""
    privateKey: str = Field(..., description="Private key (hex format) - Keep SECRET!")
    publicKey: str = Field(..., description="Public key (hex format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "privateKey": "0x1a2b3c4d5e6f7890...",
                "publicKey": "0x9876543210fedcba...,0xabcdef1234567890..."
            }
        }


# ==================== SIGN FILE ====================

class SignFileResponse(BaseModel):
    """Response after signing a file"""
    file_name: str = Field(..., description="Original filename")
    file_hash: str = Field(..., description="SHA-256 hash of file")
    file_size: int = Field(..., description="File size in bytes")
    signature: str = Field(..., description="Digital signature (hex)")
    public_key: str = Field(..., description="Public key derived from private key")
    signed_at: str = Field(..., description="Timestamp (ISO 8601)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_name": "diploma.pdf",
                "file_hash": "abc123def456...",
                "file_size": 102400,
                "signature": "0xSIG123...",
                "public_key": "0x9876...,0xabcd...",
                "signed_at": "2024-01-22T10:00:00Z"
            }
        }


# ==================== VERIFY SIGNATURE ====================

class VerifySignatureResponse(BaseModel):
    """Response after verifying signature"""
    is_valid: bool = Field(..., description="True if signature is valid")
    file_hash: str = Field(..., description="SHA-256 hash of file")
    message: str = Field(..., description="Verification message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "file_hash": "abc123...",
                "message": "✅ Signature is valid"
            }
        }
