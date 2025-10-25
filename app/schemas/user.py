"""
Pydantic схемы для пользователей и авторизации
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.user import UserRole


# ===================================
# Авторизация
# ===================================

class UserLogin(BaseModel):
    """Вход в систему"""
    
    username: str = Field(..., min_length=3, max_length=50, description="Логин")
    password: str = Field(..., min_length=6, description="Пароль")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "student123",
                "password": "SecurePass123"
            }
        }


class TokenResponse(BaseModel):
    """Ответ с токенами"""
    
    access_token: str = Field(..., description="Access токен")
    refresh_token: str = Field(..., description="Refresh токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни access токена (секунды)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена"""
    
    refresh_token: str = Field(..., description="Refresh токен")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


# ===================================
# Пользователь
# ===================================

class UserBase(BaseModel):
    """Базовые поля пользователя"""
    
    username: str = Field(..., min_length=3, max_length=50, description="Логин")
    full_name: str = Field(..., min_length=2, max_length=255, description="ФИО")
    major_code: str | None = Field(None, max_length=10, description="Код специальности (для студентов)")


class UserCreate(UserBase):
    """Создание пользователя"""
    
    password: str = Field(..., min_length=6, description="Пароль")
    role: UserRole = Field(default=UserRole.STUDENT, description="Роль")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "student123",
                "password": "SecurePass123",
                "full_name": "Иванов Иван Иванович",
                "role": "student",
                "major_code": "M001"
            }
        }


class UserUpdate(BaseModel):
    """Обновление пользователя"""
    
    full_name: str | None = Field(None, min_length=2, max_length=255, description="ФИО")
    major_code: str | None = Field(None, max_length=10, description="Код специальности")
    password: str | None = Field(None, min_length=6, description="Новый пароль")
    is_active: bool | None = Field(None, description="Активен ли пользователь")
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Иванов Иван Петрович",
                "major_code": "M002"
            }
        }


class UserResponse(UserBase):
    """Ответ с данными пользователя"""
    
    id: int = Field(..., description="ID пользователя")
    role: UserRole = Field(..., description="Роль")
    is_active: bool = Field(..., description="Активен ли")
    created_at: datetime = Field(..., description="Дата создания")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "student123",
                "full_name": "Иванов Иван Иванович",
                "role": "student",
                "major_code": "M001",
                "is_active": True,
                "created_at": "2025-10-25T10:00:00Z"
            }
        }


class UserListResponse(BaseModel):
    """Список пользователей"""
    
    users: list[UserResponse] = Field(..., description="Пользователи")
    total: int = Field(..., description="Общее количество")
    
    class Config:
        json_schema_extra = {
            "example": {
                "users": [],
                "total": 0
            }
        }


class CurrentUserResponse(UserResponse):
    """Текущий аутентифицированный пользователь"""
    
    # Можно добавить дополнительные поля если нужно
    pass
