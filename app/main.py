"""
Главный файл FastAPI приложения Connect AITU
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import time

from app.core.config import settings
from app.services.redis_service import redis_service
from app.api import (
    auth_router,
    majors_router,
    subjects_router,
    practice_router,
    exam_router,
    stats_router,
    admin_router,
)


# ===================================
# Lifecycle Events
# ===================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events (startup/shutdown)"""
    # Startup
    print("🚀 Starting Connect AITU Backend...")
    
    # Подключение к Redis
    await redis_service.connect()
    print("✅ Redis connected")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Connect AITU Backend...")
    
    # Отключение от Redis
    await redis_service.disconnect()
    print("✅ Redis disconnected")


# ===================================
# Create FastAPI App
# ===================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API для платформы подготовки к экзаменам в магистратуру Казахстана",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ===================================
# CORS Middleware
# ===================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ===================================
# Request Time Middleware
# ===================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Добавить время обработки запроса в заголовки"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ===================================
# Exception Handlers
# ===================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработка ошибок валидации Pydantic"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Ошибка валидации данных",
            "errors": exc.errors()
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Обработка ошибок базы данных"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Ошибка базы данных",
            "error": str(exc) if settings.DEBUG else "Internal server error"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработка всех остальных ошибок"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Внутренняя ошибка сервера",
            "error": str(exc) if settings.DEBUG else "Internal server error"
        }
    )


# ===================================
# Health Check
# ===================================

@app.get(
    "/health",
    tags=["Системные"],
    summary="Health check",
    description="Проверка работоспособности API"
)
async def health_check():
    """
    Проверка здоровья API
    
    Возвращает статус сервиса и версию
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get(
    "/",
    tags=["Системные"],
    summary="Корневой endpoint",
    description="Информация об API"
)
async def root():
    """
    Корневой endpoint
    
    Возвращает информацию об API
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# ===================================
# API Routers
# ===================================

# Группируем все роутеры под /api prefix
API_PREFIX = "/api"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(majors_router, prefix=API_PREFIX)
app.include_router(subjects_router, prefix=API_PREFIX)
app.include_router(practice_router, prefix=API_PREFIX)
app.include_router(exam_router, prefix=API_PREFIX)
app.include_router(stats_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)


# ===================================
# Startup Message
# ===================================

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    🎓 {settings.APP_NAME} v{settings.APP_VERSION}
    
    Environment: {settings.ENVIRONMENT}
    Debug: {settings.DEBUG}
    
    API Documentation: http://localhost:8000/docs
    Health Check: http://localhost:8000/health
    """)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
