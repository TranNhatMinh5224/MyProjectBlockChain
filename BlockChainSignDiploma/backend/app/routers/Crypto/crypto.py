"""
Crypto API - File Signing
Public endpoints for signing files with private keys
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status

from app.Services.CryptoService import get_crypto_service
from app.Schemas.CryptoSchemas import (
    GenerateKeypairResponse,
    SignFileResponse,
    VerifySignatureResponse
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ==================== ENDPOINTS ====================

@router.post("/generate-keypair", tags=["🔐 Crypto"], response_model=dict)
async def generate_keypair():
    """
    Generate keypair using Custom Elliptic Curve TNM5224
    
    **Public endpoint** - Anyone can generate a keypair
    
    **Returns:**
    - privateKey: Keep this SECRET and SECURE
    - publicKey: Use this for verification
    
    **⚠️ IMPORTANT:**
    - SAVE YOUR PRIVATE KEY SECURELY
    - NEVER share your private key
    - You CANNOT recover it if lost
    """
    try:
        crypto_service = get_crypto_service()
        result = crypto_service.generate_keypair()
        
        return {
            "success": True,
            "data": result.model_dump(),
            "warning": "⚠️ SAVE YOUR PRIVATE KEY SECURELY! You cannot recover it if lost."
        }
        
    except Exception as e:
        logger.error(f"Failed to generate keypair: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate keypair: {str(e)}"
        )


@router.post("/sign-file", tags=["🔐 Crypto"], response_model=dict)
async def sign_file(
    file: UploadFile = File(..., description="File PDF/DOCX cần ký"),
    private_key: str = Form(..., description="Private key (hex string)")
):
    """
    Sign a file with your private key
    
    **Public endpoint** - Anyone can sign files
    
    **Input:**
    - file: PDF/DOCX file to sign
    - private_key: Your private key (hex format)
    
    **Output:**
    - file_hash: SHA-256 hash of the file
    - signature: Digital signature
    - public_key: Derived from private key
    
    **Use case:**
    - Sign diploma/transcript before pushing to blockchain
    - Anyone can sign, but only schools can push to Fabric
    """
    try:
        # Read file content
        content = await file.read()
        
        # Call service
        crypto_service = get_crypto_service()
        result = await crypto_service.sign_file(
            file_content=content,
            file_name=file.filename,
            private_key=private_key
        )
        
        return {
            "success": True,
            "data": result.model_dump(),
            "message": "✅ File signed successfully!",
            "next_step": "If you are a school, you can now push this to blockchain"
        }
        
    except ValueError as e:
        logger.error(f"Invalid private key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid private key: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to sign file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sign file: {str(e)}"
        )


@router.post("/verify-signature", tags=["🔐 Crypto"], response_model=dict)
async def verify_signature(
    file: UploadFile = File(..., description="File to verify"),
    signature: str = Form(..., description="Signature (hex string)"),
    public_key: str = Form(..., description="Public key (hex string)")
):
    """
    Verify a file's signature
    
    **Public endpoint** - Anyone can verify signatures
    
    **Input:**
    - file: Original file
    - signature: Signature to verify
    - public_key: Public key of the signer
    
    **Output:**
    - is_valid: True/False
    - file_hash: Hash of the file
    """
    try:
        # Read file content
        content = await file.read()
        
        # Call service
        crypto_service = get_crypto_service()
        result = await crypto_service.verify_signature(
            file_content=content,
            signature=signature,
            public_key=public_key
        )
        
        return {
            "success": True,
            "data": result.model_dump(),
            "status": "✅ VALID" if result.is_valid else "❌ INVALID"
        }
        
    except Exception as e:
        logger.error(f"Failed to verify signature: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify signature: {str(e)}"
        )
