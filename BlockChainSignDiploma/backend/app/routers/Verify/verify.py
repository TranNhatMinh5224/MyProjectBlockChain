"""
Verification API Endpoints
Các endpoint dành cho Nhà tuyển dụng / Public để verify bằng cấp
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, status

from app.Services.VerifyService import get_verify_service
from app.Schemas.VerifySchemas import VerificationResult
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ==================== ENDPOINTS ====================

@router.post("/diploma", response_model=VerificationResult, tags=["✅ Verification"])
async def verify_diploma_by_file(
    pdf_file: UploadFile = File(..., description="File PDF bằng cấp cần verify")
):
    """
    Verify tính hợp lệ của bằng cấp bằng cách upload file PDF
    
    **Public endpoint** - Ai cũng có thể gọi (Nhà tuyển dụng, Sinh viên, ...)
    
    **Flow:**
    1. Upload file PDF
    2. Tính SHA-256 hash của file
    3. Query Blockchain để lấy thông tin bằng
    4. Verify 4 lớp bảo mật:
       - ✅ Bằng có tồn tại trên Blockchain không?
       - ✅ Bằng có bị thu hồi không?
       - ✅ Trường cấp bằng có hợp pháp không?
       - ✅ Chữ ký số có đúng không?
    
    **Kết quả:**
    - `is_valid = true`: Bằng hợp lệ, có thể tin tưởng
    - `is_valid = false`: Bằng không hợp lệ hoặc đã bị thu hồi
    """
    try:
        # Read PDF content
        pdf_content = await pdf_file.read()
        
        # Call service
        verify_service = get_verify_service()
        result = await verify_service.verify_by_file(pdf_content)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to verify diploma: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify diploma: {str(e)}"
        )


@router.get("/diploma/{file_hash}", response_model=VerificationResult, tags=["✅ Verification"])
async def verify_diploma_by_hash(file_hash: str):
    """
    Verify tính hợp lệ của bằng cấp bằng file hash
    
    **Public endpoint** - Ai cũng có thể gọi
    
    **Use Case:**
    - Nhà tuyển dụng có sẵn hash (từ QR code hoặc link)
    - Không cần upload lại file PDF
    
    **Flow:**
    1. Nhận file_hash từ URL
    2. Query Blockchain
    3. Verify các điều kiện
    
    **Example:**
    ```
    GET /verify/diploma/abc123def456...
    ```
    """
    try:
        verify_service = get_verify_service()
        result = await verify_service.verify_by_hash(file_hash)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to verify diploma: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify diploma: {str(e)}"
        )
