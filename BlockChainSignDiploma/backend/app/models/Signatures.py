from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class Signature(Base):
    """
    Model lưu lịch sử ký file
    """
    __tablename__ = "signatures"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # File information
    file_name = Column(String(255), nullable=False)
    file_hash = Column(Text, nullable=False)  # SHA-256 hash
    file_size = Column(BigInteger, nullable=False)  # Bytes
    file_type = Column(String(50), nullable=False)  # MIME type
    
    # Signature information
    signature = Column(Text, nullable=False)  # "0xr,0xs" format
    public_key = Column(Text, nullable=False)  # "0xx,0xy" format
    
    # Signer information (optional)
    signer_name = Column(String(255), nullable=True)
    signer_email = Column(String(255), nullable=True)
    
    # Timestamps
    signed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Signature(id={self.id}, file_name='{self.file_name}', signer='{self.signer_name}')>"
