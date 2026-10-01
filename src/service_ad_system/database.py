import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# 📌 로컬 환경에 맞춘 기본 DATABASE_URL 설정 (도커 미사용)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://user:password@localhost:5432/dbname"
)

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# 비동기 세션 팩토리 생성
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ORM 모델들이 상속받을 베이스 클래스
class Base(DeclarativeBase):
    pass

# FastAPI 의존성 주입(Depends)용 세션 제너레이터
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()