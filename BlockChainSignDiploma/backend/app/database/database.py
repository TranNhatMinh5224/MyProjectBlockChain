# Import các class cần thiết từ SQLAlchemy async
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import create_engine

# Import cấu hình database từ file config
from app.core.config import DATABASE_URL

# Định nghĩa Base cho models
Base = declarative_base(cls=AsyncAttrs)

# Tạo async database URL (thêm +asyncpg driver)
SQLALCHEMY_DATABASE_URL = DATABASE_URL
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Tạo engine - công cụ kết nối và quản lý database
# echo=True: in ra các câu lệnh SQL được thực thi (để debug)
# future=True: sử dụng API mới của SQLAlchemy 2.0
engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=True, 
    future=True,
    pool_size=20,           # Giữ sẵn 20 kết nối trong pool
    max_overflow=30         # Có thể tạo thêm 30 kết nối (tối đa 50)
)

# Tạo sync engine (nếu cần cho legacy code)
sync_engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# Tạo factory để tạo các session database (phiên làm việc với DB)
# bind=engine: liên kết với engine đã tạo ở trên
# class_=AsyncSession: sử dụng AsyncSession cho async operations
# expire_on_commit=False: không làm expire objects sau khi commit (an toàn hơn)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,                    # Liên kết với database engine
    class_=AsyncSession,           # Sử dụng AsyncSession class
    expire_on_commit=False         # Không expire objects sau commit
) 

# Tạo session factory thứ hai với cùng cấu hình
# Có thể dùng cho các trường hợp đặc biệt hoặc tách biệt logic
StrictSessionLocal = async_sessionmaker(
    bind=engine,                    # Liên kết với database engine
    class_=AsyncSession,           # Sử dụng AsyncSession class
    expire_on_commit=False         # Không expire objects sau commit
)

# Dependency function cho FastAPI - cung cấp database session
# Được inject vào các endpoint thông qua Depends()
async def get_async_session():
    # Tạo session từ factory và sử dụng async context manager
    async with AsyncSessionLocal() as session:
        try:
            # Yield session để FastAPI có thể inject vào endpoint , Yield cho phép sử dụng session trong các endpoint
            yield session
        except Exception:
            # Nếu có lỗi xảy ra, rollback tất cả changes chưa commit
            await session.rollback()  
            # Re-raise exception để FastAPI xử lý
            raise