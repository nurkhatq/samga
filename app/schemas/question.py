"""
Pydantic схемы для вопросов
КРИТИЧЕСКИ ВАЖНО: QuestionResponse НЕ содержит is_correct!
"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.question import QuestionDifficulty, QuestionType


# ===================================
# Варианты ответа
# ===================================

class QuestionOptionBase(BaseModel):
    """Базовый вариант ответа"""
    
    key: str = Field(..., max_length=1, description="Ключ варианта (A, B, C, D, E)")
    text: str = Field(..., description="Текст варианта")


class QuestionOptionCreate(QuestionOptionBase):
    """Вариант ответа при создании (с is_correct)"""
    
    is_correct: bool = Field(..., description="Правильный ли вариант")
    
    class Config:
        json_schema_extra = {
            "example": {
                "key": "A",
                "text": "Вариант А",
                "is_correct": True
            }
        }


class QuestionOptionResponse(QuestionOptionBase):
    """
    Вариант ответа в ответе API
    БЕЗОПАСНО: БЕЗ is_correct!
    """
    
    class Config:
        json_schema_extra = {
            "example": {
                "key": "A",
                "text": "Вариант А"
            }
        }


class QuestionOptionWithCorrect(QuestionOptionBase):
    """
    Вариант ответа с правильным ответом
    ИСПОЛЬЗУЕТСЯ ТОЛЬКО для показа правильных ответов после завершения экзамена!
    """
    
    is_correct: bool = Field(..., description="Правильный ли вариант")
    
    class Config:
        json_schema_extra = {
            "example": {
                "key": "A",
                "text": "Вариант А",
                "is_correct": True
            }
        }


# ===================================
# Вопросы
# ===================================

class QuestionBase(BaseModel):
    """Базовые поля вопроса"""
    
    subject_code: str = Field(..., max_length=50, description="Код предмета")
    question_text: str = Field(..., description="Текст вопроса")
    difficulty: QuestionDifficulty = Field(default=QuestionDifficulty.A, description="Сложность")
    question_type: QuestionType = Field(default=QuestionType.SINGLE, description="Тип вопроса")
    points: int = Field(default=1, ge=1, description="Баллы")
    time_seconds: int = Field(default=90, ge=10, description="Время на ответ (секунды)")
    explanation: str | None = Field(None, description="Объяснение правильного ответа")
    tags: list[str] = Field(default_factory=list, description="Теги")


class QuestionCreate(QuestionBase):
    """Создание вопроса"""
    
    options: list[QuestionOptionCreate] = Field(..., min_length=2, max_length=6, description="Варианты ответа")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject_code": "TGO",
                "question_text": "Какая столица Казахстана?",
                "options": [
                    {"key": "A", "text": "Алматы", "is_correct": False},
                    {"key": "B", "text": "Астана", "is_correct": True},
                    {"key": "C", "text": "Шымкент", "is_correct": False}
                ],
                "difficulty": "A",
                "question_type": "single",
                "points": 1,
                "time_seconds": 90,
                "explanation": "Столица Казахстана - Астана",
                "tags": ["география", "столицы"]
            }
        }


class QuestionResponse(QuestionBase):
    """
    Ответ с данными вопроса
    БЕЗОПАСНО: варианты БЕЗ is_correct!
    """
    
    id: str = Field(..., description="UUID вопроса")
    options: list[QuestionOptionResponse] = Field(..., description="Варианты ответа БЕЗ правильных")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "3a5e96ce-1dbd-4982-9c17-6eecf071c813",
                "subject_code": "TGO",
                "question_text": "Какая столица Казахстана?",
                "options": [
                    {"key": "A", "text": "Алматы"},
                    {"key": "B", "text": "Астана"},
                    {"key": "C", "text": "Шымкент"}
                ],
                "difficulty": "A",
                "question_type": "single",
                "points": 1,
                "time_seconds": 90,
                "explanation": None,
                "tags": ["география"]
            }
        }


class QuestionWithCorrectResponse(QuestionBase):
    """
    Вопрос с правильными ответами
    ИСПОЛЬЗУЕТСЯ ТОЛЬКО после завершения экзамена или в Practice Mode при проверке!
    """
    
    id: str = Field(..., description="UUID вопроса")
    options: list[QuestionOptionWithCorrect] = Field(..., description="Варианты с правильными ответами")
    correct_keys: list[str] = Field(..., description="Правильные ключи")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "3a5e96ce-1dbd-4982-9c17-6eecf071c813",
                "subject_code": "TGO",
                "question_text": "Какая столица Казахстана?",
                "options": [
                    {"key": "A", "text": "Алматы", "is_correct": False},
                    {"key": "B", "text": "Астана", "is_correct": True},
                    {"key": "C", "text": "Шымкент", "is_correct": False}
                ],
                "correct_keys": ["B"],
                "difficulty": "A",
                "question_type": "single",
                "points": 1,
                "time_seconds": 90,
                "explanation": "Столица Казахстана - Астана",
                "tags": ["география"]
            }
        }


class QuestionListResponse(BaseModel):
    """Список вопросов (безопасный)"""
    
    questions: list[QuestionResponse] = Field(..., description="Вопросы БЕЗ правильных ответов")
    total: int = Field(..., description="Общее количество")
    offset: int = Field(default=0, description="Смещение")
    limit: int = Field(default=20, description="Лимит")
    has_more: bool = Field(..., description="Есть ли еще вопросы")
    
    class Config:
        json_schema_extra = {
            "example": {
                "questions": [],
                "total": 2000,
                "offset": 0,
                "limit": 20,
                "has_more": True
            }
        }


class QuestionImportResult(BaseModel):
    """Результат импорта вопросов"""
    
    imported_count: int = Field(..., description="Количество импортированных вопросов")
    skipped_count: int = Field(default=0, description="Количество пропущенных")
    errors: list[str] = Field(default_factory=list, description="Ошибки")
    
    class Config:
        json_schema_extra = {
            "example": {
                "imported_count": 2000,
                "skipped_count": 5,
                "errors": []
            }
        }
