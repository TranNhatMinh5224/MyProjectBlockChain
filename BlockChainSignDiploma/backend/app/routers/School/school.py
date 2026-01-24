"""
School API - Push to Fabric
Endpoints for schools to push signed diplomas to blockchain
"""

from fastapi import APIRouter, HTTPException, Form, Depends, status

from app.Services.SchoolService import get_school_service
from app.Schemas.SchoolSchemas import (
    PushToFabricRequest,
    RevokeDiplomaRequest
)
from app.core.logging_config import get_logger
from app.core.auth_dependencies import get_current_user

logger = get_logger(__name__)
router = APIRouter()


# ==================== ENDPOINTS ====================

@router.post("/push-to-fabric", tags=["🏫 School"], response_model=dict)
async def push_to_fabric(
    file_hash: str = Form(...),
    signature: str = Form(...),
    diploma_id: str = Form(...),
    school_id: str = Form(...),
    student_name: str = Form(...),
    student_id: str = Form(...),
    major: str = Form(...),
    grade: str = Form(...),
    issue_date: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Push signed diploma metadata to Fabric blockchain
    
    **Authentication Required** - Only schools can push to blockchain
    """
    try:
        # Create request object
        request = PushToFabricRequest(
            file_hash=file_hash,
            signature=signature,
            diploma_id=diploma_id,
            school_id=school_id,
            student_name=student_name,
            student_id=student_id,
            major=major,
            grade=grade,
            issue_date=issue_date
        )
        
        # Call service
        school_service = get_school_service()
        result = await school_service.push_to_fabric(request, current_user)
        
        return {
            "success": True,
            "message": "✅ Bằng đã được đưa lên Blockchain!",
            "data": result.model_dump(),
            "next_step": f"Sinh viên có thể verify bằng hash: {file_hash}"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to push to Fabric: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to push to Fabric: {str(e)}"
        )


@router.get("/diplomas", tags=["🏫 School"], response_model=dict)
async def get_school_diplomas(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of diplomas pushed by this school
    
    **Authentication Required**
    """
    try:
        school_service = get_school_service()
        result = await school_service.list_diplomas(limit, offset, current_user)
        
        return {
            "success": True,
            "data": result.model_dump(),
            "message": "Feature coming soon"
        }
        
    except Exception as e:
        logger.error(f"Failed to get diplomas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get diplomas: {str(e)}"
        )


@router.post("/diplomas/revoke", tags=["🏫 School"], response_model=dict)
async def revoke_diploma(
    file_hash: str = Form(...),
    reason: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Thu hồi bằng cấp đã cấp
    
    **Authentication Required** - Chỉ SCHOOL
    """
    try:
        # Create request object
        request = RevokeDiplomaRequest(
            file_hash=file_hash,
            reason=reason
        )
        
        # Call service
        school_service = get_school_service()
        result = await school_service.revoke_diploma(request, current_user)
        
        return {
            "success": True,
            "message": "✅ Diploma revoked successfully!",
            "data": result.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Failed to revoke diploma: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke diploma: {str(e)}"
        )
