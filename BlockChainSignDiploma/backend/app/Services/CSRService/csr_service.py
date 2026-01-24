"""
CSR (Certificate Signing Request) Service
Xử lý logic nghiệp vụ cho CSR management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional, List
import uuid

from app.models.CertificateRequest import CertificateRequest, CSRStatus
from app.Services.FabricService.diploma_service import get_diploma_service
from app.core.crypto import sign_diploma
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class CSRService:
    """Service để xử lý CSR operations"""
    
    async def submit_csr(
        self,
        db: AsyncSession,
        school_id: str,
        school_name: str,
        public_key: str,
        csr_signature: str,
        address: Optional[str] = None,
        tax_code: Optional[str] = None,
        legal_representative: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> dict:
        """
        Trường nộp CSR
        
        Returns:
            dict với thông tin CSR đã tạo
        """
        try:
            # Check if school already submitted CSR
            query = select(CertificateRequest).where(CertificateRequest.school_id == school_id)
            result = await db.execute(query)
            existing = result.scalar_one_or_none()
            
            if existing:
                if existing.status in [CSRStatus.PENDING, CSRStatus.APPROVED, CSRStatus.REVOKED]:
                    raise ValueError(f"School {school_id} already has a CSR status: {existing.status}")
                
                # If REJECTED, update existing record to PENDING with new details
                if existing.status == CSRStatus.REJECTED:
                    logger.info(f"♻️ Re-submitting CSR for REJECTED school {school_id}")
                    existing.school_name = school_name
                    existing.public_key = public_key
                    existing.address = address
                    existing.tax_code = tax_code
                    existing.legal_representative = legal_representative
                    existing.phone = phone
                    existing.email = email
                    existing.csr_signature = csr_signature
                    existing.status = CSRStatus.PENDING
                    existing.rejection_reason = None # Clear old reason
                    existing.created_at = datetime.utcnow() # Reset timestamp
                    
                    # We reuse the 'existing' object, so 'csr' variable below should point to it
                    csr = existing
            else:
                # Create new CSR
                csr = CertificateRequest(
                    id=str(uuid.uuid4()),
                    school_id=school_id,
                    school_name=school_name,
                    public_key=public_key,
                    address=address,
                    tax_code=tax_code,
                    legal_representative=legal_representative,
                    phone=phone,
                    email=email,
                    csr_signature=csr_signature,
                    status=CSRStatus.PENDING
                )
                db.add(csr)
            
            # Logic below (lines 66+) needs to handle both add (new) and commit (update)
            # Since 'db.add(csr)' is only needed for new objects, but 'db.commit()' works for both attached objects.
            
            await db.commit()
            await db.refresh(csr)
            # Ghi thông tin trường lên Blockchain (Status: PENDING) với Public Key mới
            logger.info(f"🔵 CALLING CreateSchool for ID={school_id}, name={school_name}")
            diploma_service = get_diploma_service()
            result = await diploma_service.create_school(
                school_id=school_id,
                name=school_name,
                public_key=public_key
            )
            logger.info(f"✅ CreateSchool SUCCESS for ID={school_id}, result={result}")

            
            return {
                "id": csr.id,
                "schoolId": csr.school_id,
                "status": csr.status,
                "createdAt": csr.created_at.isoformat()
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to submit CSR: {str(e)}")
            raise
    
    async def list_csr(
        self,
        db: AsyncSession,
        status_filter: Optional[str] = None
    ) -> List[dict]:
        """
        Lấy danh sách CSR
        
        Returns:
            List of CSR dicts
        """
        try:
            from sqlalchemy import desc
            
            query = select(CertificateRequest).order_by(desc(CertificateRequest.created_at))
            
            if status_filter:
                query = query.where(CertificateRequest.status == status_filter)
            
            result = await db.execute(query)
            csrs = result.scalars().all()
            
            return [
                {
                    "id": csr.id,
                    "schoolId": csr.school_id,
                    "schoolName": csr.school_name,
                    "publicKey": csr.public_key,
                    "address": csr.address,
                    "taxCode": csr.tax_code,
                    "legalRepresentative": csr.legal_representative,
                    "phone": csr.phone,
                    "email": csr.email,
                    "status": csr.status,
                    "createdAt": csr.created_at.isoformat() if csr.created_at else None,
                    "approvedAt": csr.approved_at.isoformat() if csr.approved_at else None,
                    "rejectionReason": csr.rejection_reason
                }
                for csr in csrs
            ]
            
        except Exception as e:
            logger.error(f"Failed to list CSR: {str(e)}")
            raise
    
    async def approve_csr(
        self,
        db: AsyncSession,
        csr_id: str,
        ministry_private_key: str,
        registered_date: str
    ) -> dict:
        """
        Duyệt CSR và đăng ký trường lên Blockchain
        
        Returns:
            dict với thông tin CSR và school
        """
        try:
            # Get CSR
            query = select(CertificateRequest).where(CertificateRequest.id == csr_id)
            result = await db.execute(query)
            csr = result.scalar_one_or_none()
            
            if not csr:
                raise ValueError(f"CSR {csr_id} not found")
            
            if csr.status != CSRStatus.PENDING:
                raise ValueError(f"CSR already processed. Status: {csr.status}")
            
            # Sign certificate (Bộ ký Public Key của trường)
            cert_data = {
                "schoolId": csr.school_id,
                "schoolName": csr.school_name,
                "publicKey": csr.public_key,
                "registeredDate": registered_date
            }
            
            _, certificate = sign_diploma(cert_data, ministry_private_key)
            
            # Register school on blockchain
            diploma_service = get_diploma_service()
            school = await diploma_service.register_school(
                school_id=csr.school_id,
                name=csr.school_name,
                public_key=csr.public_key,
                certificate=certificate,
                registered_date=registered_date
            )
            
            # Update CSR status
            csr.status = CSRStatus.APPROVED
            csr.certificate = certificate
            csr.approved_at = datetime.utcnow()
            csr.approved_by = "Ministry Admin"  # TODO: Get from auth
            
            # Update User status to ACTIVE
            from app.models.User import User
            from sqlalchemy import update
            
            await db.execute(
                update(User)
                .where(User.school_id == csr.school_id)
                .values(status="ACTIVE")
            )
            
            await db.commit()
            await db.refresh(csr)
            
            return {
                "csr": {
                    "id": csr.id,
                    "status": csr.status,
                    "approvedAt": csr.approved_at.isoformat()
                },
                "school": school,
                "certificate": certificate
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to approve CSR: {str(e)}")
            raise
    
    async def reject_csr(
        self,
        db: AsyncSession,
        csr_id: str,
        reason: str
    ) -> dict:
        """
        Từ chối CSR
        
        Returns:
            dict với thông tin CSR đã reject
        """
        try:
            query = select(CertificateRequest).where(CertificateRequest.id == csr_id)
            result = await db.execute(query)
            csr = result.scalar_one_or_none()
            
            if not csr:
                raise ValueError(f"CSR {csr_id} not found")
            
            if csr.status != CSRStatus.PENDING:
                raise ValueError(f"CSR already processed. Status: {csr.status}")
            
            csr.status = CSRStatus.REJECTED
            csr.rejection_reason = reason
            
            await db.commit()
            await db.refresh(csr)
            
            return {
                "id": csr.id,
                "schoolId": csr.school_id,
                "status": csr.status,
                "rejectionReason": csr.rejection_reason
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to reject CSR: {str(e)}")
            raise


# Singleton instance
_csr_service_instance: Optional[CSRService] = None

def get_csr_service() -> CSRService:
    """Get singleton instance of CSR Service"""
    global _csr_service_instance
    if _csr_service_instance is None:
        _csr_service_instance = CSRService()
    return _csr_service_instance
