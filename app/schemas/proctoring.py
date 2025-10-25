"""
Pydantic схемы для прокторинга
"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.proctoring import ProctoringEventType


class ProctoringEventCreate(BaseModel):
    """Создание события прокторинга"""
    
    event_type: ProctoringEventType = Field(..., description="Тип события")
    metadata: dict = Field(default_factory=dict, description="Дополнительные данные")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "tab_switch",
                "metadata": {
                    "from_tab": "exam",
                    "to_tab": "google"
                }
            }
        }


class ProctoringEventResponse(BaseModel):
    """Ответ о событии прокторинга"""
    
    id: int = Field(..., description="ID события")
    attempt_id: str = Field(..., description="UUID попытки")
    event_type: ProctoringEventType = Field(..., description="Тип события")
    timestamp: datetime = Field(..., description="Время события")
    metadata: dict = Field(..., description="Дополнительные данные")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "attempt_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "tab_switch",
                "timestamp": "2025-10-25T10:15:30Z",
                "metadata": {
                    "from_tab": "exam",
                    "to_tab": "google"
                }
            }
        }


class ProctoringEventBatchCreate(BaseModel):
    """Массовая отправка событий прокторинга"""
    
    events: list[ProctoringEventCreate] = Field(..., max_length=100, description="События (макс 100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "events": [
                    {
                        "event_type": "copy",
                        "metadata": {"text_length": 50}
                    },
                    {
                        "event_type": "tab_switch",
                        "metadata": {}
                    }
                ]
            }
        }


class ProctoringEventBatchResponse(BaseModel):
    """Ответ на массовую отправку"""
    
    created_count: int = Field(..., description="Количество созданных событий")
    
    class Config:
        json_schema_extra = {
            "example": {
                "created_count": 2
            }
        }


class ProctoringStatisticsResponse(BaseModel):
    """Статистика прокторинга для попытки"""
    
    attempt_id: str = Field(..., description="UUID попытки")
    total_events: int = Field(default=0, description="Всего событий")
    copy_paste_count: int = Field(default=0, description="Копирований/вставок")
    tab_switches_count: int = Field(default=0, description="Переключений вкладок")
    console_opens_count: int = Field(default=0, description="Открытий консоли")
    suspicious: bool = Field(default=False, description="Подозрительная активность")
    events_by_type: dict[str, int] = Field(default_factory=dict, description="События по типам")
    
    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "123e4567-e89b-12d3-a456-426614174000",
                "total_events": 12,
                "copy_paste_count": 3,
                "tab_switches_count": 5,
                "console_opens_count": 0,
                "suspicious": False,
                "events_by_type": {
                    "copy": 2,
                    "paste": 1,
                    "tab_switch": 5,
                    "window_blur": 4
                }
            }
        }
