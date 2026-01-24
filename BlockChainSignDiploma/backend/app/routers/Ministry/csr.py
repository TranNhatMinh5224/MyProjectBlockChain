"""
CSR (Certificate Signing Request) Router
Endpoints for schools to submit CSR and check status
"""

from fastapi import APIRouter, HTTPException, Form, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_async_session
from app.Services.CSRService.csr_service import get_csr_service
from app.Schemas.CSRSchemas import SubmitCSRRequest
from app.core.auth_dependencies import get_current_user
from app.core.logging_config import get_logger
from app.models.User import User

router = APIRouter()
logger = get_logger(__name__)


# ==================== ENDPOINTS ====================

@router.post("/submit", tags=["📝 CSR"], response_model=dict)
async def submit_csr(
    schoolId: str = Form(..., description="Mã trường (VD: HUST)"),
    schoolName: str = Form(..., description="Tên đầy đủ của trường"),
    publicKey: str = Form(..., description="Public key (format: 0xX,0xY)"),
    csrSignature: str = Form(..., description="Chữ ký CSR (format: 0xR,0xS)"),
    email: str = Form(..., description="Email liên hệ"),
    verificationFile: UploadFile = File(..., description="File đã ký để xác thực (Proof of Possession)"),
    address: str = Form(None, description="Địa chỉ trường"),
    taxCode: str = Form(None, description="Mã số thuế"),
    legalRepresentative: str = Form(None, description="Người đại diện pháp luật"),
    phone: str = Form(None, description="Số điện thoại"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Nộp CSR (Certificate Signing Request) cho Bộ
    
    **Authentication Required** - Chỉ SCHOOL
    """
    try:
        # 1. Read and Hash File
        file_content = await verificationFile.read()
        
        # Calculate SHA-256 hash of the file content (to match CryptoService.sign_file behavior)
        import hashlib
        file_hash_hex = hashlib.sha256(file_content).hexdigest()
        
        logger.info(f"VERIFYING CSR: schoolId={schoolId}, fileHash={file_hash_hex}, sig={csrSignature}")

        # 2. Verify Signature
        # IMPORTANT: The 'sign_file' tool signs the dictionary {"file_hash": <hash>}, NOT the raw file bytes or raw hash.
        # We must verify against the same data structure.
        data_to_verify = {"file_hash": file_hash_hex}
        
        from app.core.crypto import verify_diploma_signature
        is_valid, msg = verify_diploma_signature(data_to_verify, csrSignature, publicKey)
        
        if not is_valid:
            logger.warning(f"❌ Invalid CSR Signature for school {schoolId}: {msg}")
            raise ValueError(f"Invalid CSR Signature: {msg}. Make sure you signed the uploaded file correctly with your private key.")
            
        logger.info(f"✅ CSR Signature Validated for school {schoolId}")

        # Call service
        csr_service = get_csr_service()
        
        result = await csr_service.submit_csr(
            db=db,
            school_id=schoolId,
            school_name=schoolName,
            public_key=publicKey,
            csr_signature=csrSignature,
            address=address,
            tax_code=taxCode,
            legal_representative=legalRepresentative,
            phone=phone,
            email=email
        )
        
        return {
            "success": True,
            "message": "✅ CSR submitted successfully! Waiting for Ministry approval.",
            "data": result,
            "next_step": "Wait for Ministry to approve your CSR. Check status using GET /school/csr/status"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to submit CSR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit CSR: {str(e)}"
        )


@router.get("/status", tags=["📝 CSR"], response_model=dict)
async def get_csr_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Xem trạng thái CSR của trường
    
    **Authentication Required** - Chỉ SCHOOL
    """
    try:
        school_id = current_user.school_id
        
        if not school_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="School ID not found in token"
            )
        
        # Query CSR from service
        csr_service = get_csr_service()
        csrs = await csr_service.list_csr(db=db, status_filter=None)
        
        # Find CSR for this school
        school_csr = next((csr for csr in csrs if csr["schoolId"] == school_id), None)
        
        if not school_csr:
            return {
                "success": True,
                "data": None,
                "message": "No CSR found. Please submit a CSR first."
            }
        
        return {
            "success": True,
            "data": {
                "csr": school_csr,
                "school": {
                    "schoolId": school_id,
                    "status": current_user.status or "PENDING"
                }
            },
            "message": f"CSR status: {school_csr['status']}"
        }
        
    except Exception as e:
        logger.error(f"Failed to get CSR status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get CSR status: {str(e)}"
        )
