"""
Verify Service - Business Logic Layer
Handles diploma verification operations
"""

import hashlib
from typing import Optional

from app.Schemas.VerifySchemas import VerificationResult, VerificationError
from app.Services.FabricService.diploma_service import get_diploma_service
from app.core.crypto import verify_diploma_signature
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class VerifyService:
    """Service for diploma verification"""
    
    async def verify_by_file(self, pdf_content: bytes) -> VerificationResult:
        """
        Verify diploma by PDF file content
        
        Args:
            pdf_content: PDF file bytes
            
        Returns:
            VerificationResult with validation details
        """
        try:
            # Calculate file hash
            file_hash = hashlib.sha256(pdf_content).hexdigest()
            logger.info(f"🔍 Verifying diploma with hash: {file_hash}")
            
            # Verify by hash
            return await self.verify_by_hash(file_hash)
            
        except Exception as e:
            logger.error(f"Failed to verify diploma by file: {str(e)}")
            raise
    
    async def verify_by_hash(self, file_hash: str) -> VerificationResult:
        """
        Verify diploma by file hash
        
        Args:
            file_hash: SHA-256 hash of diploma PDF
            
        Returns:
            VerificationResult with validation details
        """
        try:
            # Query blockchain
            diploma_service = get_diploma_service()
            
            try:
                blockchain_data = await diploma_service.verify_diploma(file_hash)
            except Exception as e:
                # Diploma not found on blockchain
                return VerificationResult(
                    is_valid=False,
                    file_hash=file_hash,
                    message="❌ Diploma not found on blockchain. This may be a fake diploma."
                )
            
            diploma = blockchain_data.get("diploma", {})
            school = blockchain_data.get("school", {})
            
            # Check 1: Diploma revoked?
            if diploma.get("status") == "REVOKED":
                return VerificationResult(
                    is_valid=False,
                    file_hash=file_hash,
                    diploma_id=diploma.get("diplomaId"),
                    school_id=diploma.get("schoolId"),
                    school_name=school.get("name"),
                    student_name=diploma.get("studentName"),
                    student_id=diploma.get("studentId"),
                    major=diploma.get("major"),
                    grade=diploma.get("grade"),
                    issue_date=diploma.get("issueDate"),
                    status="REVOKED",
                    school_status=school.get("status"),
                    message=f"❌ Diploma has been REVOKED. Reason: {diploma.get('revokeReason', 'Not specified')}"
                )
            
            # Check 2: School revoked?
            if school.get("status") == "REVOKED":
                return VerificationResult(
                    is_valid=False,
                    file_hash=file_hash,
                    diploma_id=diploma.get("diplomaId"),
                    school_id=diploma.get("schoolId"),
                    school_name=school.get("name"),
                    student_name=diploma.get("studentName"),
                    student_id=diploma.get("studentId"),
                    major=diploma.get("major"),
                    grade=diploma.get("grade"),
                    issue_date=diploma.get("issueDate"),
                    status=diploma.get("status"),
                    school_status="REVOKED",
                    message=f"❌ School has been REVOKED. This diploma is no longer valid."
                )
            
            # Check 3: Verify signature
            school_public_key = school.get("publicKey")
            signature = diploma.get("signature")
            
            data_to_verify = {"file_hash": file_hash}
            is_signature_valid, sig_message = verify_diploma_signature(
                data_to_verify,
                signature,
                school_public_key
            )
            
            if not is_signature_valid:
                return VerificationResult(
                    is_valid=False,
                    file_hash=file_hash,
                    diploma_id=diploma.get("diplomaId"),
                    school_id=diploma.get("schoolId"),
                    school_name=school.get("name"),
                    student_name=diploma.get("studentName"),
                    student_id=diploma.get("studentId"),
                    major=diploma.get("major"),
                    grade=diploma.get("grade"),
                    issue_date=diploma.get("issueDate"),
                    status=diploma.get("status"),
                    signature=signature,
                    signature_valid=False,
                    school_status=school.get("status"),
                    message=f"❌ Invalid signature: {sig_message}"
                )
            
            # All checks passed - diploma is valid!
            return VerificationResult(
                is_valid=True,
                file_hash=file_hash,
                diploma_id=diploma.get("diplomaId"),
                school_id=diploma.get("schoolId"),
                school_name=school.get("name"),
                student_name=diploma.get("studentName"),
                student_id=diploma.get("studentId"),
                major=diploma.get("major"),
                grade=diploma.get("grade"),
                issue_date=diploma.get("issueDate"),
                status="ACTIVE",
                signature=signature,
                signature_valid=True,
                school_status="ACTIVE",
                message="✅ Diploma is valid and verified on blockchain!"
            )
            
        except Exception as e:
            logger.error(f"Failed to verify diploma by hash: {str(e)}")
            raise


def get_verify_service() -> VerifyService:
    """Factory function to get Verify service instance"""
    return VerifyService()
