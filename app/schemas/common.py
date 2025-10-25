"""
Общие Pydantic схемы
"""
from typing import Any
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Стандартный ответ об ошибке"""
    
    detail: str = Field(..., description="Описание ошибки")
    error_code: str | None = Field(None, description="Код ошибки")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Пользователь не найден",
                "error_code": "USER_NOT_FOUND"
            }
        }


class SuccessResponse(BaseModel):
    """Стандартный ответ об успехе"""
    
    message: str = Field(..., description="Сообщение об успехе")
    data: Any | None = Field(None, description="Дополнительные данные")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Операция выполнена успешно",
                "data": None
            }
        }


class PaginationParams(BaseModel):
    """Параметры пагинации"""
    
    offset: int = Field(0, ge=0, description="Смещение")
    limit: int = Field(20, ge=1, le=100, description="Количество элементов")
    
    class Config:
        json_schema_extra = {
            "example": {
                "offset": 0,
                "limit": 20
            }
        }


class PaginatedResponse(BaseModel):
    """Ответ с пагинацией"""
    
    items: list[Any] = Field(..., description="Элементы")
    total: int = Field(..., description="Общее количество")
    offset: int = Field(..., description="Текущее смещение")
    limit: int = Field(..., description="Количество элементов на странице")
    has_more: bool = Field(..., description="Есть ли еще элементы")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "offset": 0,
                "limit": 20,
                "has_more": True
            }
        }
