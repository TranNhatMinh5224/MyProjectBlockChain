from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from app.Services.FabricService.gateway import get_fabric_gateway
from app.Services.PDFService.pdf_generator import get_pdf_generator
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class DiplomaService:
    """
    Service layer cho Diploma operations
    Wrapper around Fabric Gateway với business logic
    """
    
    def __init__(self):
        self.gateway = get_fabric_gateway()

    async def _query_with_retry(
        self, 
        function: str, 
        args: list, 
        retries: int = 15, 
        delay: float = 2.0
    ) -> Any:
        """
        Thực hiện query với cơ chế retry để đợi block commit
        Mặc định đợi tối đa 30s (15 retries * 2s)
        """
        last_error = None
        for i in range(retries):
            try:
                result = await self.gateway.query_chaincode(function, args)
                return result
            except Exception as e:
                last_error = e
                # Kiểm tra lỗi "not exist" hoặc "not found"
                err_str = str(e).lower()
                if "does not exist" in err_str or "not found" in err_str or "endorsement failure" in err_str:
                    logger.warning(f"⏳ Query {function} failed (attempt {i+1}/{retries}). Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                raise e
        
        logger.error(f"❌ Query {function} failed after {retries} attempts. Last error: {str(last_error)}")
        raise last_error
    
    # ==================== MINISTRY OPERATIONS ====================
    
    async def create_school(
        self,
        school_id: str,
        name: str,
        public_key: str
    ) -> Dict[str, Any]:
        """
        Khởi tạo thông tin trường trên Fabric (Status: PENDING)
        Sẽ được gọi ngay khi trường đăng ký tài khoản
        """
        try:
            logger.info(f"🏫 Creating school on ledger: {school_id}")
            await self.gateway.invoke_chaincode(
                function="CreateSchool",
                args=[school_id, name, public_key]
            )
            
            # Wait a moment for block to commit before verifying
            logger.info(f"⏳ Waiting for block commit...")
            await asyncio.sleep(3)
            
            # Verify with retry
            school = await self._query_with_retry(
                function="GetSchool",
                args=[school_id],
                retries=10,
                delay=2.0
            )
            return school
        except Exception as e:
            logger.error(f"❌ Failed to create school on ledger: {str(e)}")
            # Không raise lỗi để tránh break flow đăng ký DB nếu fabric gặp sự cố tạm thời
            # Tuy nhiên trong môi trường test này ta nên biết
            raise
    
    async def init_ministry(self, public_key: str) -> Dict[str, Any]:
        """
        Khởi tạo Ministry of Education trên Fabric
        CHỈ chạy 1 lần duy nhất khi setup hệ thống
        
        Args:
            public_key: Public key của Bộ Giáo Dục (hex format)
            
        Returns:
            Dict chứa thông tin Ministry
        """
        try:
            logger.info("🏛️ Initializing Ministry of Education...")
            
            await self.gateway.invoke_chaincode(
                function="InitLedger",
                args=[public_key]
            )
            
            # Query to verify with retry
            ministry = await self._query_with_retry(
                function="GetMinistry",
                args=[]
            )
            
            logger.info("✅ Ministry initialized successfully")
            return ministry
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ministry: {str(e)}")
            raise
    
    async def get_ministry(self) -> Dict[str, Any]:
        """
        Lấy thông tin Ministry of Education
        
        Returns:
            Dict chứa thông tin Ministry
        """
        try:
            ministry = await self.gateway.query_chaincode(
                function="GetMinistry",
                args=[]
            )
            return ministry
        except Exception as e:
            logger.error(f"❌ Failed to get Ministry: {str(e)}")
            raise
    
    async def register_school(
        self,
        school_id: str,
        name: str,
        public_key: str,
        certificate: str,
        registered_date: str
    ) -> Dict[str, Any]:
        """
        Đăng ký trường mới (chỉ Ministry được gọi)
        
        Args:
            school_id: Mã trường (VD: HUST, NEU)
            name: Tên đầy đủ của trường
            public_key: Public key của trường (hex)
            certificate: Certificate do Ministry ký (hex)
            registered_date: Ngày đăng ký (YYYY-MM-DD)
            
        Returns:
            Dict chứa thông tin trường vừa đăng ký
        """
        try:
            logger.info(f"🏫 Registering school: {school_id}")
            
            await self.gateway.invoke_chaincode(
                function="RegisterSchool",
                args=[school_id, name, public_key, certificate, registered_date]
            )
            
            # Query to verify with retry
            school = await self._query_with_retry(
                function="GetSchool",
                args=[school_id]
            )
            
            logger.info(f"✅ School registered: {school_id}")
            return school
            
        except Exception as e:
            logger.error(f"❌ Failed to register school: {str(e)}")
            raise
    
    async def revoke_school(self, school_id: str) -> Dict[str, Any]:
        """
        Thu hồi quyền của trường (chỉ Ministry được gọi)
        
        Args:
            school_id: Mã trường cần thu hồi
            
        Returns:
            Dict chứa thông tin trường sau khi thu hồi
        """
        try:
            logger.info(f"⛔ Revoking school: {school_id}")
            
            await self.gateway.invoke_chaincode(
                function="RevokeSchool",
                args=[school_id]
            )
            
            # Query to verify with retry
            # Lưu ý: RevokeSchool trong chaincode cập nhật status thành REVOKED
            # nhưng GetSchool vẫn trả về object. Ta query để verify status mới.
            school = await self._query_with_retry(
                function="GetSchool",
                args=[school_id]
            )
            
            logger.info(f"✅ School revoked: {school_id}")
            return school
            
        except Exception as e:
            logger.error(f"❌ Failed to revoke school: {str(e)}")
            raise
    
    # ==================== SCHOOL OPERATIONS ====================
    
    async def get_school(self, school_id: str) -> Dict[str, Any]:
        """
        Lấy thông tin trường
        
        Args:
            school_id: Mã trường
            
        Returns:
            Dict chứa thông tin trường
        """
        try:
            school = await self.gateway.query_chaincode(
                function="GetSchool",
                args=[school_id]
            )
            return school
        except Exception as e:
            logger.error(f"❌ Failed to get school: {str(e)}")
            raise
    
    async def issue_diploma(
        self,
        diploma_id: str,
        file_hash: str,
        signature: str,
        school_id: str,
        student_name: str,
        student_id: str,
        major: str,
        grade: str,
        issue_date: str
    ) -> Dict[str, Any]:
        """
        Cấp bằng cho sinh viên (chỉ School được gọi)
        
        Args:
            diploma_id: Mã số văn bằng (unique)
            file_hash: SHA-256 hash của file PDF
            signature: Chữ ký số của trường (hex)
            school_id: Mã trường cấp bằng
            student_name: Tên sinh viên
            student_id: Mã sinh viên
            major: Ngành học
            grade: Xếp loại (Excellent, Good, etc.)
            issue_date: Ngày cấp (YYYY-MM-DD)
            
        Returns:
            Dict chứa thông tin bằng vừa cấp
        """
        try:
            logger.info(f"📜 Issuing diploma: {diploma_id} for {student_name}")
            
            await self.gateway.invoke_chaincode(
                function="IssueDiploma",
                args=[
                    diploma_id,
                    file_hash,
                    signature,
                    school_id,
                    student_name,
                    student_id,
                    major,
                    grade,
                    issue_date
                ]
            )
            
            # Query to verify with retry
            diploma = await self._query_with_retry(
                function="VerifyDiploma",
                args=[file_hash]
            )
            
            logger.info(f"✅ Diploma issued: {diploma_id}")
            return diploma
            
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.warning(f"⚠️ Diploma {diploma_id} (hash: {file_hash}) already exists on ledger")
                # Return the existing diploma info instead of crashing
                # Or raise a specific 409 Conflict error
                raise ValueError(f"Văn bằng này đã tồn tại trên hệ thống (Hash: {file_hash})")
            
            logger.error(f"❌ Failed to issue diploma: {str(e)}")
            raise
    
    async def revoke_diploma(
        self,
        file_hash: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Thu hồi bằng cấp (School hoặc Ministry được gọi)
        
        Args:
            file_hash: Hash của file PDF
            reason: Lý do thu hồi
            
        Returns:
            Dict chứa thông tin bằng sau khi thu hồi
        """
        try:
            logger.info(f"⛔ Revoking diploma: {file_hash}")
            
            await self.gateway.invoke_chaincode(
                function="RevokeDiploma",
                args=[file_hash, reason]
            )
            
            # Query to verify with retry
            diploma = await self._query_with_retry(
                function="VerifyDiploma",
                args=[file_hash]
            )
            
            logger.info(f"✅ Diploma revoked: {file_hash}")
            return diploma
            
        except Exception as e:
            logger.error(f"❌ Failed to revoke diploma: {str(e)}")
            raise
    
    # ==================== VERIFICATION OPERATIONS ====================
    
    async def verify_diploma(self, file_hash: str) -> Dict[str, Any]:
        """
        Verify bằng cấp (Public - ai cũng gọi được)
        
        Args:
            file_hash: SHA-256 hash của file PDF
            
        Returns:
            Dict chứa toàn bộ thông tin verify (diploma + school + ministry)
        """
        try:
            logger.info(f"🔍 Verifying diploma: {file_hash}")
            
            result = await self.gateway.query_chaincode(
                function="GetDiplomaWithSchoolInfo",
                args=[file_hash]
            )
            
            logger.info(f"✅ Diploma verified: {file_hash}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to verify diploma: {str(e)}")
            raise
    
    async def issue_diploma_with_pdf(
        self,
        diploma_id: str,
        school_id: str,
        student_name: str,
        student_id: str,
        major: str,
        grade: str,
        issue_date: str,
        private_key: str,
        verify_base_url: str = "https://verify.edu.vn"
    ):
        """
        Issue diploma với auto-generate PDF
        Tất cả logic ở đây, không ở endpoint
        
        Returns:
            dict với pdf_buffer, file_hash, signature, headers
        """
        try:
            # 1. Get and validate school
            school = await self.get_school(school_id)
            
            if school.get("status") != "ACTIVE":
                raise ValueError(f"School {school_id} is not active (status: {school.get('status')})")
            
            # 2. Prepare data
            student_info = {
                "studentName": student_name,
                "studentId": student_id,
                "major": major,
                "grade": grade,
                "issueDate": issue_date
            }
            
            school_info = {
                "name": school.get("name"),
                "id": school_id
            }
            
            # 3. Sign diploma data
            from app.core.crypto import sign_diploma
            diploma_data_for_signing = {
                "diplomaId": diploma_id,
                "schoolId": school_id,
                "studentName": student_name,
                "studentId": student_id,
                "major": major,
                "grade": grade,
                "issueDate": issue_date
            }
            
            hash_hex, signature_hex = sign_diploma(diploma_data_for_signing, private_key)
            logger.info(f"✍️ Signature created: {signature_hex[:20]}...")
            
            # 4. Generate PDF
            from app.services.PDFService.pdf_generator import get_pdf_generator
            pdf_generator = get_pdf_generator()
            
            # Generate temp PDF
            pdf_buffer = pdf_generator.generate_diploma_pdf(
                student_info=student_info,
                school_info=school_info,
                file_hash="temp",
                signature=signature_hex,
                verify_base_url=verify_base_url
            )
            
            # 5. Calculate real hash
            import hashlib
            pdf_content = pdf_buffer.getvalue()
            file_hash = hashlib.sha256(pdf_content).hexdigest()
            logger.info(f"📄 File hash: {file_hash}")
            
            # 6. Regenerate PDF with real hash (for QR code)
            pdf_buffer = pdf_generator.generate_diploma_pdf(
                student_info=student_info,
                school_info=school_info,
                file_hash=file_hash,
                signature=signature_hex,
                verify_base_url=verify_base_url
            )
            
            # 7. Save to blockchain
            await self.issue_diploma(
                diploma_id=diploma_id,
                file_hash=file_hash,
                signature=signature_hex,
                school_id=school_id,
                student_name=student_name,
                student_id=student_id,
                major=major,
                grade=grade,
                issue_date=issue_date
            )
            
            logger.info(f"✅ Diploma issued successfully: {diploma_id}")
            
            # 8. Return result
            pdf_buffer.seek(0)
            return {
                "pdf_buffer": pdf_buffer,
                "file_hash": file_hash,
                "signature": signature_hex,
                "headers": {
                    "Content-Disposition": f"attachment; filename=diploma_{student_id}_{diploma_id}.pdf",
                    "X-File-Hash": file_hash,
                    "X-Signature": signature_hex
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to issue diploma with PDF: {str(e)}")
            raise

    async def issue_diploma_from_file(
        self,
        file_bytes: bytes,
        filename: str,
        diploma_id: str,
        school_id: str,
        student_name: str,
        student_id: str,
        major: str,
        grade: str,
        issue_date: str,
        private_key: str
    ):
        """
        Issue diploma từ file có sẵn (Option 2)
        1. Hash file input
        2. Ký số lên hash
        3. Lưu lên Blockchain
        """
        try:
            # 1. Validation basics
            if not file_bytes:
                raise ValueError("File content is empty")

            school = await self.get_school(school_id)
            if school.get("status") != "ACTIVE":
                raise ValueError(f"School {school_id} is not active")

            # 2. Calculate Hash of the input file
            import hashlib
            file_hash = hashlib.sha256(file_bytes).hexdigest()
            logger.info(f"📄 Calculated hash for uploaded file: {file_hash}")

            # 3. Sign the Hash (Proof of Origin)
            from app.core.crypto import sign_diploma
            
            # 3. Sign the Hash (Proof of Origin)
            from app.core.crypto import sign_diploma
            
            # CRITICAL UPDATE: Sign the file_hash to match Chaincode's verifySignatureInternal logic
            # Chaincode reconstructs message as: {"file_hash": "HASH"}
            data_to_sign = {"file_hash": file_hash}
            
            # Use data_to_sign instead of the full metadata dict
            hash_hex, signature_hex = sign_diploma(data_to_sign, private_key)
            
            # 4. Save to Blockchain
            await self.issue_diploma(
                diploma_id=diploma_id,
                file_hash=file_hash,
                signature=signature_hex,
                school_id=school_id,
                student_name=student_name,
                student_id=student_id,
                major=major,
                grade=grade,
                issue_date=issue_date
            )
            
            return {
                "success": True,
                "file_hash": file_hash,
                "signature": signature_hex,
                "message": "Diploma registered successfully with uploaded file"
            }

        except Exception as e:
            logger.error(f"❌ Failed to issue diploma from file: {str(e)}")
            raise
    async def get_diplomas_by_school(
        self,
        school_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list:
        """
        Query all diplomas issued by a specific school
        
        Args:
            school_id: School ID
            limit: Maximum number of results
            offset: Starting position
            
        Returns:
            List of diploma dictionaries
        """
        try:
            logger.info(f"📋 Querying diplomas for school: {school_id}")
            
            diplomas = await self.gateway.query_chaincode(
                function="GetDiplomasBySchool",
                args=[school_id]
            )
            
            # Map 'id' to 'diplomaId' to match Pydantic schema
            if isinstance(diplomas, list):
                for d in diplomas:
                    if isinstance(d, dict) and 'id' in d:
                        d['diplomaId'] = d['id']

            # TODO: Implement pagination on chaincode side or filter here
            return diplomas if isinstance(diplomas, list) else []
            
        except Exception as e:
            logger.error(f"❌ Failed to query diplomas by school: {str(e)}")
            # Return empty list instead of raising to avoid breaking the UI
            return []
    
    async def get_all_schools(self) -> list:
        """
        Query all registered schools from Fabric
        
        Returns:
            List of school dictionaries with their info
        """
        try:
            logger.info("📋 Querying all schools from Fabric")
            
            schools = await self.gateway.query_chaincode(
                function="GetAllSchools",
                args=[]
            )
            
            return schools if isinstance(schools, list) else []
            
        except Exception as e:
            logger.error(f"❌ Failed to query all schools: {str(e)}")
            # Return empty list instead of raising
            return []
    
    async def get_system_statistics(self) -> Dict[str, int]:
        """
        Get system-wide statistics from Fabric
        
        Returns:
            Dictionary with counts:
            - total_schools
            - active_schools
            - revoked_schools
            - total_diplomas
        """
        try:
            logger.info("📊 Querying system statistics from Fabric")
            
            stats = await self.gateway.query_chaincode(
                function="GetSystemStatistics",
                args=[]
            )
            
            # Ensure we return a dict with default values
            if isinstance(stats, dict):
                return {
                    "total_schools": stats.get("total_schools", 0),
                    "active_schools": stats.get("active_schools", 0),
                    "revoked_schools": stats.get("revoked_schools", 0),
                    "total_diplomas": stats.get("total_diplomas", 0)
                }
            else:
                return {
                    "total_schools": 0,
                    "active_schools": 0,
                    "revoked_schools": 0,
                    "total_diplomas": 0
                }
            
        except Exception as e:
            logger.error(f"❌ Failed to query system statistics: {str(e)}")
            # Return zeros instead of raising
            return {
                "total_schools": 0,
                "active_schools": 0,
                "revoked_schools": 0,
                "total_diplomas": 0
            }


# Singleton instance
_diploma_service_instance: Optional[DiplomaService] = None

def get_diploma_service() -> DiplomaService:
    """
    Get singleton instance of Diploma Service
    """
    global _diploma_service_instance
    if _diploma_service_instance is None:
        _diploma_service_instance = DiplomaService()
    return _diploma_service_instance
