"""
Auth Service - Business Logic for Authentication
Handles user registration and login
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.models.User import User
from app.core.jwt_auth import create_access_token, verify_password, get_password_hash
from app.core.logging_config import get_logger
from app.Services.FabricService.diploma_service import get_diploma_service
from app.Schemas.AuthSchemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    UserInfo
)

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    async def register_school(
        request: RegisterRequest,
        db: AsyncSession
    ) -> RegisterResponse:
        """
        Register a new school account
        
        Args:
            request: Registration request data
            db: Database session
            
        Returns:
            RegisterResponse with user info
            
        Raises:
            ValueError if email already exists
            Exception for other errors
        """
        try:
            # Check if email already exists
            query = select(User).where(User.username == request.email)
            result = await db.execute(query)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise ValueError("Email already registered")
            
            # Hash password
            password_hash = get_password_hash(request.password)
            
            # Create new user
            new_user = User(
                username=request.email,
                password_hash=password_hash,
                email=request.email,
                school_id=request.schoolId,
                school_name=request.schoolName,
                role_name="SCHOOL",
                status="PENDING"  # Chờ nộp CSR
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            logger.info(f"✅ School {request.schoolId} registered successfully")
            
            return RegisterResponse(
                email=request.email,
                schoolId=request.schoolId,
                status="PENDING"
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            await db.rollback()
            raise Exception(f"Registration failed: {str(e)}")
    
    
    @staticmethod
    async def login(
        request: LoginRequest,
        db: AsyncSession
    ) -> LoginResponse:
        """
        Login user and generate JWT token
        
        Args:
            request: Login request data
            db: Database session
            
        Returns:
            LoginResponse with access token and user info
            
        Raises:
            ValueError if credentials are invalid
            Exception for other errors
        """
        try:
            # Find user in database
            query = select(User).where(User.username == request.username)
            result = await db.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("Incorrect username or password")
            
            # Verify password
            if not verify_password(request.password, user.password_hash):
                raise ValueError("Incorrect username or password")
            
            # Get role name
            role_name = user.role_name or "USER"
            
            # Create JWT token
            access_token = create_access_token(
                data={
                    "sub": str(user.id),
                    "role": role_name,
                    "school_id": user.school_id
                },
                expires_delta=timedelta(hours=24)
            )
            
            logger.info(f"✅ User {user.username} logged in successfully")
            
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserInfo(
                    username=user.username,
                    email=user.email,
                    role=role_name,
                    schoolId=user.school_id,
                    schoolName=user.school_name,
                    status=user.status or "PENDING"
                )
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise Exception(f"Login failed: {str(e)}")


# Singleton instance
_auth_service = AuthService()


def get_auth_service() -> AuthService:
    """Get AuthService instance"""
    return _auth_service
