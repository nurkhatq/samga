"""
Асинхронная и синхронная сессии БД (SQLAlchemy 2.0)
Для FastAPI (async) и Celery (sync + async support)
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import asyncio

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
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Алиас для обратной совместимости
async_session_maker = AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость FastAPI для получения асинхронной сессии БД
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
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===================================
# Утилиты для Celery с async задачами
# ===================================
def run_async_task(async_func):
    """
    Запуск асинхронной функции в синхронном контексте (для Celery)
    
    Использование в Celery задачах:
        result = run_async_task(my_async_function())
    """
    try:
        # Пытаемся использовать существующий event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если loop уже запущен, создаем новый для этой задачи
            return asyncio.run(async_func)
        else:
            # Используем существующий loop
            return loop.run_until_complete(async_func)
    except RuntimeError:
        # Если нет event loop, создаем новый
        return asyncio.run(async_func)


async def get_async_db() -> AsyncSession:
    """
    Получить асинхронную сессию для использования в Celery задачах
    """
    async with AsyncSessionLocal() as session:
        try:
            return session
        except Exception:
            await session.rollback()
            raise