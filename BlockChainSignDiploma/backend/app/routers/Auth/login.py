"""
Authentication Router - Register & Login
Endpoints for user registration and authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_async_session
from app.Services.AuthService import get_auth_service
from app.Schemas.AuthSchemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse
)
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


# ==================== ENDPOINTS ====================

@router.post("/register", tags=["🔐 Authentication"], response_model=dict)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Đăng ký tài khoản trường
    
    **Public endpoint** - Trường tự đăng ký
    
    **Input:**
    - email: Email trường
    - password: Mật khẩu
    - schoolId: Mã trường (VD: HUST)
    - schoolName: Tên đầy đủ
    
    **Output:**
    - success: true/false
    - message: Thông báo
    
    **Next Step:**
    Sau khi đăng ký → Đăng nhập → Nộp CSR
    """
    try:
        auth_service = get_auth_service()
        result = await auth_service.register_school(request, db)
        
        return {
            "success": True,
            "message": "✅ Registration successful! Please login and submit CSR.",
            "data": result.model_dump(),
            "next_step": "Login with your email and password, then submit CSR to Ministry"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=dict, tags=["🔐 Authentication"])
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Login để lấy JWT access token
    
    **Tài khoản mặc định:**
    - Ministry: `admin` / `admin123`
    
    **Response:**
    - `access_token`: JWT token (dùng cho các request sau)
    - `token_type`: "bearer"
    - `user`: Thông tin user
    """
    try:
        auth_service = get_auth_service()
        result = await auth_service.login(request, db)
        
        return {
            "success": True,
            "data": result.model_dump()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
