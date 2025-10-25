"""
Асинхронная и синхронная сессии БД (SQLAlchemy 2.0)
Для FastAPI (async) и Celery (sync)
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings


# ===================================
# Асинхронная сессия для FastAPI
# ===================================
async_engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
)

# Создаем фабрику асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Алиас для обратной совместимости (если где-то используется async_session_maker)
async_session_maker = AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость FastAPI для получения асинхронной сессии БД
    
    Yields:
        AsyncSession: Асинхронная сессия базы данных
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ===================================
# Синхронная сессия для Celery
# ===================================
# Создаем синхронный URL (убираем asyncpg)
sync_database_url = str(settings.DATABASE_URL).replace('+asyncpg', '')

sync_engine = create_engine(
    sync_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Создаем фабрику синхронных сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

def get_sync_db():
    """
    Зависимость для получения синхронной сессии БД (для Celery)
    
    Yields:
        Session: Синхронная сессия базы данных
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()