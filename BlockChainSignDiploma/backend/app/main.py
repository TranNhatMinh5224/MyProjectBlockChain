"""
Main FastAPI Application
Entry point for the Crypto Signature System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import database
from app.database.database import engine, Base

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for the application
    """
    # Startup
    print("🚀 Starting Crypto Signature System...")
    print("📊 Database tables created successfully")
    yield
    # Shutdown
    print("👋 Shutting down Crypto Signature System...")

# Create FastAPI app
app = FastAPI(
    title="Blockchain Diploma Management System",
    description="Hệ thống quản lý văn bằng dựa trên Hyperledger Fabric Blockchain với chữ ký số Custom Elliptic Curve TNM5224",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Blockchain Diploma Management System",
        "version": "2.0.0"
    }

# Include routers
from app.routers.Auth.login import router as login_router
from app.routers.Crypto.crypto import router as crypto_router
from app.routers.School.school import router as school_router
from app.routers.Ministry.csr import router as csr_router
from app.routers.Ministry.ministry import router as ministry_router
from app.routers.Verify.verify import router as verify_router

app.include_router(
    login_router,
    prefix="/api/v1/auth",
    tags=["🔐 Authentication"]
)

app.include_router(
    crypto_router, 
    prefix="/api/v1/crypto"
)

app.include_router(
    csr_router,
    prefix="/api/v1/school/csr"
)

app.include_router(
    ministry_router,
    prefix="/api/v1/ministry"
)

app.include_router(
    school_router,
    prefix="/api/v1/school"
)

app.include_router(
    verify_router,
    prefix="/api/v1/verify",
    tags=["✅ Verification"]
)


@app.get("/", tags=["Info"])
async def root():
    """
    API Root - Thông tin hệ thống
    """
    return {
        "name": "Blockchain Diploma Management System",
        "version": "2.0.0",
        "description": "Hệ thống quản lý văn bằng dựa trên Hyperledger Fabric Blockchain",
        "features": [
            "🏛️ Ministry Management",
            "🏫 School Management",
            "🎓 Diploma Issuance",
            "✅ Diploma Verification",
            "🔐 Custom Curve TNM5224 Cryptography",
            "📝 Certificate Signing Request (CSR)"
        ],
        "blockchain": "Hyperledger Fabric",
        "curve": "TNM5224 (Custom Elliptic Curve)",
        "algorithm": "ECDSA",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

# cú pháp chạy dự án là : 
#  uvicorn app.main:app --reload