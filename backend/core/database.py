from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# aiosqlite asenkron driver'ını kullanıyoruz
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./mrfridge.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False # Canlıda performansı etkilememesi için logları kapatıyoruz
)

# Async oturum yöneticisi
SessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

Base = declarative_base()

# Dependency: Asenkron veritabanı oturumu
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()