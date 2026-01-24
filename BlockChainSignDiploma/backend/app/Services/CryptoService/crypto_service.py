"""
Crypto Service - Business Logic for Cryptographic Operations
Handles keypair generation, file signing, and signature verification
"""

from typing import Tuple
from datetime import datetime
import hashlib

from app.core.crypto import (
    generate_university_keypair,
    derive_public_key,
    sign_diploma,
    verify_diploma_signature
)
from app.core.logging_config import get_logger
from app.Schemas.CryptoSchemas import (
    GenerateKeypairResponse,
    SignFileResponse,
    VerifySignatureResponse
)

logger = get_logger(__name__)


class CryptoService:
    """Service for cryptographic operations"""
    
    @staticmethod
    def generate_keypair() -> GenerateKeypairResponse:
        """
        Generate a new keypair using TNM5224 curve
        
        Returns:
            GenerateKeypairResponse with privateKey and publicKey
            
        Raises:
            Exception if keypair generation fails
        """
        try:
            private_key, public_key = generate_university_keypair()
            
            logger.info("✅ Keypair generated successfully")
            
            return GenerateKeypairResponse(
                privateKey=private_key,
                publicKey=public_key
            )
            
        except Exception as e:
            logger.error(f"Failed to generate keypair: {str(e)}")
            raise Exception(f"Keypair generation failed: {str(e)}")
    
    
    @staticmethod
    async def sign_file(
        file_content: bytes,
        file_name: str,
        private_key: str
    ) -> SignFileResponse:
        """
        Sign a file with private key
        
        Args:
            file_content: Binary content of file
            file_name: Original filename
            private_key: Private key in hex format
            
        Returns:
            SignFileResponse with hash, signature, and metadata
            
        Raises:
            ValueError if private key is invalid
            Exception for other errors
        """
        try:
            # Calculate file hash
            file_hash = hashlib.sha256(file_content).hexdigest()
            logger.info(f"📄 File hash calculated: {file_hash[:16]}...")
            
            # Create data to sign
            data_to_sign = {"file_hash": file_hash}
            
            # Sign the data
            _, signature = sign_diploma(data_to_sign, private_key)
            logger.info(f"✍️ Signature created: {signature[:20]}...")
            
            # Derive public key
            public_key = derive_public_key(private_key)
            
            # Get timestamp
            signed_at = datetime.utcnow().isoformat() + "Z"
            
            return SignFileResponse(
                file_name=file_name,
                file_hash=file_hash,
                file_size=len(file_content),
                signature=signature,
                public_key=public_key,
                signed_at=signed_at
            )
            
        except ValueError as e:
            logger.error(f"Invalid private key: {str(e)}")
            raise ValueError(f"Invalid private key: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to sign file: {str(e)}")
            raise Exception(f"File signing failed: {str(e)}")
    
    
    @staticmethod
    async def verify_signature(
        file_content: bytes,
        signature: str,
        public_key: str
    ) -> VerifySignatureResponse:
        """
        Verify a file's signature
        
        Args:
            file_content: Binary content of file
            signature: Signature in hex format
            public_key: Public key in hex format
            
        Returns:
            VerifySignatureResponse with validation result
            
        Raises:
            Exception if verification fails
        """
        try:
            # Calculate file hash
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Verify signature
            data_to_verify = {"file_hash": file_hash}
            is_valid, message = verify_diploma_signature(
                data_to_verify,
                signature,
                public_key
            )
            
            logger.info(f"🔍 Signature verification: {message}")
            
            return VerifySignatureResponse(
                is_valid=is_valid,
                file_hash=file_hash,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Failed to verify signature: {str(e)}")
            raise Exception(f"Signature verification failed: {str(e)}")


# Singleton instance
_crypto_service = CryptoService()


def get_crypto_service() -> CryptoService:
    """Get CryptoService instance"""
    return _crypto_service
