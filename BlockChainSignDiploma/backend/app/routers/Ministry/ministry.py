"""
Ministry of Education API Endpoints
Các endpoint dành cho Bộ Giáo Dục
"""

from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_async_session
from app.Services.CSRService.csr_service import get_csr_service
from app.Services.FabricService.diploma_service import get_diploma_service
from app.Schemas.MinistrySchemas import (
    ApproveCSRRequest,
    RejectCSRRequest,
    RevokeSchoolRequest
)
from app.core.logging_config import get_logger
from app.core.auth_dependencies import get_current_user

logger = get_logger(__name__)
router = APIRouter()


# ==================== CSR MANAGEMENT ====================

@router.get("/csr/list", tags=["🏛️ Ministry - CSR"], response_model=dict)
async def list_csr(
    status_filter: str = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Lấy danh sách CSR (Certificate Signing Requests)
    
    **Query params:**
    - status: PENDING, APPROVED, REJECTED (optional)
    
    **Authentication Required** - Ministry only
    """
    try:
        csr_service = get_csr_service()
        csrs = await csr_service.list_csr(
            db=db,
            status_filter=status_filter
        )
        
        return {
            "success": True,
            "total": len(csrs),
            "data": csrs
        }
        
    except Exception as e:
        logger.error(f"Failed to list CSR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list CSR: {str(e)}"
        )


@router.get("/csr/{csr_id}", tags=["🏛️ Ministry - CSR"], response_model=dict)
async def get_csr_detail(
    csr_id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Xem chi tiết 1 CSR
    
    **Authentication Required** - Ministry only
    """
    try:
        from sqlalchemy import select
        from app.models.CertificateRequest import CertificateRequest
        
        # Query CSR
        result = await db.execute(
            select(CertificateRequest).where(CertificateRequest.id == csr_id)
        )
        csr = result.scalars().first()
        
        if not csr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CSR {csr_id} not found"
            )
        
        return {
            "success": True,
            "data": {
                "id": csr.id,
                "schoolId": csr.school_id,
                "schoolName": csr.school_name,
                "publicKey": csr.public_key,
                "email": csr.email,
                "address": csr.address,
                "taxCode": csr.tax_code,
                "legalRepresentative": csr.legal_representative,
                "phone": csr.phone,
                "status": csr.status,
                "createdAt": csr.created_at.isoformat() if csr.created_at else None,
                "approvedAt": csr.approved_at.isoformat() if csr.approved_at else None,
                "rejectionReason": csr.rejection_reason
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get CSR detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get CSR detail: {str(e)}"
        )


@router.post("/csr/{csr_id}/approve", tags=["🏛️ Ministry - CSR"], response_model=dict)
async def approve_csr(
    csr_id: str,
    ministry_private_key: str = Body(..., embed=True),
    registered_date: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Duyệt CSR và đăng ký trường lên Blockchain
    
    **Authentication Required** - Ministry only
    """
    try:
        csr_service = get_csr_service()
        result = await csr_service.approve_csr(
            db=db,
            csr_id=csr_id,
            ministry_private_key=ministry_private_key,
            registered_date=registered_date
        )
        
        return {
            "success": True,
            "message": "✅ CSR approved and school registered on blockchain!",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to approve CSR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve CSR: {str(e)}"
        )


@router.post("/csr/{csr_id}/reject", tags=["🏛️ Ministry - CSR"], response_model=dict)
async def reject_csr(
    csr_id: str,
    request: RejectCSRRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Từ chối CSR
    
    **Authentication Required** - Ministry only
    """
    try:
        csr_service = get_csr_service()
        result = await csr_service.reject_csr(
            db=db,
            csr_id=csr_id,
            reason=request.reason
        )
        
        return {
            "success": True,
            "message": "CSR rejected",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to reject CSR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject CSR: {str(e)}"
        )


# ==================== SCHOOL MANAGEMENT ====================

@router.post("/schools/{school_id}/revoke", tags=["🏛️ Ministry - Schools"], response_model=dict)
async def revoke_school(
    school_id: str,
    request: RevokeSchoolRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Thu hồi quyền của trường
    
    **Authentication Required** - Ministry only
    """
    try:
        # 1. Update on Fabric Blockchain
        diploma_service = get_diploma_service()
        school = await diploma_service.revoke_school(school_id)
        
        # 2. Update status in Database
        from app.models.CertificateRequest import CertificateRequest, CSRStatus
        from sqlalchemy import select
        
        query = select(CertificateRequest).where(CertificateRequest.school_id == school_id)
        result = await db.execute(query)
        csr = result.scalar_one_or_none()
        
        if csr:
            csr.status = CSRStatus.REVOKED
            # Optional: You might want to store the revocation reason somewhere if needed
            # csr.rejection_reason = request.reason 
            
            # Update User status to REVOKED
            from sqlalchemy import update
            from app.models.User import User
            
            await db.execute(
                update(User)
                .where(User.school_id == school_id)
                .values(status="REVOKED")
            )
            
            await db.commit()
            logger.info(f"✅ Updated DB status to REVOKED for school {school_id}")
        else:
            logger.warning(f"⚠️ School {school_id} revoked on chain but CSR not found in DB")
        
        return {
            "success": True,
            "message": f"School {school_id} has been revoked",
            "data": school,
            "reason": request.reason
        }
        
    except Exception as e:
        logger.error(f"Failed to revoke school: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke school: {str(e)}"
        )


@router.get("/schools", tags=["🏛️ Ministry - Schools"], response_model=dict)
async def list_schools(
    current_user: dict = Depends(get_current_user)
):
    """
    Lấy danh sách tất cả các trường
    
    **Authentication Required** - Ministry only
    """
    try:
        logger.info("📋 Ministry querying all schools from Fabric")
        
        # Query all schools from Fabric
        diploma_service = get_diploma_service()
        schools = await diploma_service.get_all_schools()
        
        return {
            "success": True,
            "data": {
                "schools": schools,
                "total": len(schools)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to list schools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list schools: {str(e)}"
        )


@router.get("/statistics", tags=["🏛️ Ministry - Statistics"], response_model=dict)
async def get_statistics(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Lấy thống kê hệ thống
    
    **Authentication Required** - Ministry only
    """
    try:
        from sqlalchemy import select, func
        from app.models.CertificateRequest import CertificateRequest
        
        logger.info("📊 Ministry querying system statistics")
        
        # Count CSRs by status from DB
        pending_count = await db.execute(
            select(func.count()).select_from(CertificateRequest)
            .where(CertificateRequest.status == "PENDING")
        )
        pending_csrs = pending_count.scalar() or 0
        
        # Query Fabric for schools and diplomas statistics
        diploma_service = get_diploma_service()
        fabric_stats = await diploma_service.get_system_statistics()
        
        return {
            "success": True,
            "data": {
                "total_schools": fabric_stats.get("total_schools", 0),
                "active_schools": fabric_stats.get("active_schools", 0),
                "revoked_schools": fabric_stats.get("revoked_schools", 0),
                "total_diplomas": fabric_stats.get("total_diplomas", 0),
                "pending_csrs": pending_csrs
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
