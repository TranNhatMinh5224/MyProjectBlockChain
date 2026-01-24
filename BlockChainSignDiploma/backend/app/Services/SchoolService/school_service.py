"""
School Service - Business Logic for School Operations
Handles diploma push, revoke, and list operations
"""

from datetime import datetime

from app.Services.FabricService.diploma_service import get_diploma_service
from app.core.crypto import verify_diploma_signature
from app.core.logging_config import get_logger
from app.Schemas.SchoolSchemas import (
    PushToFabricRequest,
    PushToFabricResponse,
    RevokeDiplomaRequest,
    RevokeDiplomaResponse,
    ListDiplomasResponse
)

logger = get_logger(__name__)


class SchoolService:
    """Service for school operations"""
    
    @staticmethod
    async def push_to_fabric(
        request: PushToFabricRequest,
        current_user: dict
    ) -> PushToFabricResponse:
        """
        Push signed diploma to Fabric blockchain
        
        Args:
            request: Push request data
            current_user: Current authenticated user
            
        Returns:
            PushToFabricResponse with confirmation
            
        Raises:
            ValueError if validation fails
            Exception for other errors
        """
        try:
            logger.info(f"🏫 School {request.school_id} pushing diploma {request.diploma_id}")
            
            # Get diploma service
            diploma_service = get_diploma_service()
            
            # Verify school exists and is active
            school = await diploma_service.get_school(request.school_id)
            if school.get("status") != "ACTIVE":
                raise ValueError(f"School {request.school_id} is not active (status: {school.get('status')})")
            
            # Verify signature with school's public key
            school_public_key = school.get("publicKey")
            data_to_verify = {"file_hash": request.file_hash}
            is_valid, message = verify_diploma_signature(
                data_to_verify,
                request.signature,
                school_public_key
            )
            
            if not is_valid:
                raise ValueError(f"Invalid signature: {message}")
            
            logger.info(f"✅ Signature verified for school {request.school_id}")
            
            # Push to Fabric
            result = await diploma_service.issue_diploma(
                diploma_id=request.diploma_id,
                file_hash=request.file_hash,
                signature=request.signature,
                school_id=request.school_id,
                student_name=request.student_name,
                student_id=request.student_id,
                major=request.major,
                grade=request.grade,
                issue_date=request.issue_date
            )
            
            logger.info(f"✅ Diploma {request.diploma_id} pushed to Fabric successfully")
            
            return PushToFabricResponse(
                diploma_id=request.diploma_id,
                file_hash=request.file_hash,
                student_name=request.student_name,
                status="CONFIRMED",
                pushed_at=datetime.utcnow().isoformat() + "Z"
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to push to Fabric: {str(e)}")
            raise Exception(f"Failed to push to Fabric: {str(e)}")
    
    
    @staticmethod
    async def revoke_diploma(
        request: RevokeDiplomaRequest,
        current_user: dict
    ) -> RevokeDiplomaResponse:
        """
        Revoke a diploma
        
        Args:
            request: Revoke request data
            current_user: Current authenticated user
            
        Returns:
            RevokeDiplomaResponse with confirmation
        """
        try:
            school_id = current_user.school_id
            logger.info(f"🏫 School {school_id} revoking diploma {request.file_hash}")
            
            # Get diploma service
            diploma_service = get_diploma_service()
            
            # Verify the diploma exists and belongs to this school
            try:
                diploma_data = await diploma_service.verify_diploma(request.file_hash)
                diploma = diploma_data.get("diploma", {})
                
                # Check if diploma belongs to this school
                if diploma.get("schoolId") != school_id:
                    raise ValueError(f"Diploma does not belong to school {school_id}")
                
                # Check if already revoked
                if diploma.get("status") == "REVOKED":
                    raise ValueError("Diploma is already revoked")
                    
            except Exception as e:
                if "does not exist" in str(e).lower():
                    raise ValueError(f"Diploma with hash {request.file_hash} not found on blockchain")
                raise
            
            # Call chaincode to revoke diploma
            result = await diploma_service.revoke_diploma(
                file_hash=request.file_hash,
                reason=request.reason
            )
            
            logger.info(f"✅ Diploma {request.file_hash} revoked successfully on blockchain")
            
            return RevokeDiplomaResponse(
                file_hash=request.file_hash,
                status="REVOKED",
                reason=request.reason,
                revoked_at=datetime.utcnow().isoformat() + "Z",
                revoked_by=school_id
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to revoke diploma: {str(e)}")
            raise Exception(f"Failed to revoke diploma: {str(e)}")
    
    
    @staticmethod
    async def list_diplomas(
        limit: int,
        offset: int,
        current_user: dict
    ) -> ListDiplomasResponse:
        """
        List diplomas issued by school
        
        Args:
            limit: Number of records
            offset: Starting position
            current_user: Current authenticated user
            
        Returns:
            ListDiplomasResponse with diploma list
        """
        try:
            school_id = current_user.school_id
            
            if not school_id:
                raise ValueError("School ID not found in user context")
            
            logger.info(f"📋 Querying diplomas for school {school_id}")
            
            # Query Fabric for diplomas by school
            diploma_service = get_diploma_service()
            diplomas = await diploma_service.get_diplomas_by_school(
                school_id=school_id,
                limit=limit,
                offset=offset
            )
            
            return ListDiplomasResponse(
                total=len(diplomas),
                diplomas=diplomas
            )
            
        except Exception as e:
            logger.error(f"Failed to list diplomas: {str(e)}")
            raise Exception(f"Failed to list diplomas: {str(e)}")


# Singleton instance
_school_service = SchoolService()


def get_school_service() -> SchoolService:
    """Get SchoolService instance"""
    return _school_service
