"""
Конфигурация приложения Connect AITU
Использует pydantic-settings для валидации переменных окружения
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, field_validator


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # ===================================
    # Application
    # ===================================
    APP_NAME: str = "Connect AITU"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Domain
    DOMAIN: str = "connect-aitu.me"
    BACKEND_URL: str = "https://connect-aitu.me/api"
    
    # CORS - ИСПРАВЛЕНО: убраны дефолтные значения
    CORS_ORIGINS: List[str] = []
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Проверка на пустую строку
            if not v or v.strip() == "":
                return []
            # Handle both JSON array and comma-separated string
            if v.startswith("["):
                import json
                return json.loads(v)
            else:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v if v else []
    
    # ===================================
    # Database (PostgreSQL)
    # ===================================
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "connect_user"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "connect_aitu_db"
    
    DATABASE_URL: str = ""
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_database_url(cls, v, info):
        if v:
            return v
        data = info.data
        return f"postgresql+asyncpg://{data['POSTGRES_USER']}:{data['POSTGRES_PASSWORD']}@{data['POSTGRES_HOST']}:{data['POSTGRES_PORT']}/{data['POSTGRES_DB']}"
    
    # ===================================
    # Redis
    # ===================================
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    REDIS_URL: str = ""
    
    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def build_redis_url(cls, v, info):
        if v:
            return v
        data = info.data
        password_part = f":{data['REDIS_PASSWORD']}@" if data.get("REDIS_PASSWORD") else ""
        return f"redis://{password_part}{data['REDIS_HOST']}:{data['REDIS_PORT']}/{data['REDIS_DB']}"
    
    # ===================================
    # Celery (RabbitMQ)
    # ===================================
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "connect_user"
    RABBITMQ_PASSWORD: str
    
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    
    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def build_broker_url(cls, v, info):
        if v:
            return v
        data = info.data
        return f"amqp://{data['RABBITMQ_USER']}:{data['RABBITMQ_PASSWORD']}@{data['RABBITMQ_HOST']}:{data['RABBITMQ_PORT']}//"
    
    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def build_result_backend(cls, v, info):
        if v:
            return v
        data = info.data
        password_part = f":{data['REDIS_PASSWORD']}@" if data.get("REDIS_PASSWORD") else ""
        return f"redis://{password_part}{data['REDIS_HOST']}:{data['REDIS_PORT']}/1"
    
    # ===================================
    # Security
    # ===================================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    
    # JWT tokens (в минутах)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ===================================
    # Rate Limiting
    # ===================================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # ===================================
    # Exam Settings
    # ===================================
    # Свободный режим
    PRACTICE_QUESTIONS_PER_PAGE: int = 20
    PRACTICE_SESSION_TTL_DAYS: int = 7
    
    # Экзамены
    EXAM_AUTO_SUBMIT_BUFFER_MINUTES: int = 5
    EXAM_SESSION_TTL_HOURS: int = 24
    
    # Профильная магистратура
    PROFILE_EXAM_QUESTIONS: int = 50
    PROFILE_EXAM_SUBJECT1: int = 30
    PROFILE_EXAM_SUBJECT2: int = 20
    PROFILE_EXAM_TIME_MINUTES: int = 90
    
    # Научно-педагогическая магистратура
    SCIENTIFIC_EXAM_QUESTIONS: int = 130
    SCIENTIFIC_EXAM_FOREIGN: int = 50
    SCIENTIFIC_EXAM_TGO: int = 30
    SCIENTIFIC_EXAM_PROFILE: int = 50
    SCIENTIFIC_EXAM_TIME_MINUTES: int = 180
    
    # ===================================
    # Proctoring
    # ===================================
    PROCTORING_ENABLED: bool = True
    PROCTORING_SUSPICIOUS_THRESHOLD: int = 10
    
    # ===================================
    # Admin
    # ===================================
    FIRST_ADMIN_USERNAME: str = "admin"
    FIRST_ADMIN_PASSWORD: str
    FIRST_ADMIN_FULLNAME: str = "Администратор"
    
    # ===================================
    # Logging
    # ===================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"


# Создаем глобальный экземпляр настроек
settings = Settings()