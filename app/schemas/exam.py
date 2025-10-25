"""
Pydantic схемы для экзаменов
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.exam import ExamMode, ExamStatus
from app.schemas.question import QuestionResponse, QuestionWithCorrectResponse


# ===================================
# Начало экзамена/практики
# ===================================

class PracticeStartRequest(BaseModel):
    """Начало свободного режима"""
    
    subject_code: str = Field(..., max_length=50, description="Код предмета")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject_code": "TGO"
            }
        }


class ExamStartRequest(BaseModel):
    """Начало пробного экзамена"""
    
    major_code: str = Field(..., max_length=10, description="Код специальности")
    
    class Config:
        json_schema_extra = {
            "example": {
                "major_code": "M001"
            }
        }


class ExamStartResponse(BaseModel):
    """Ответ при начале экзамена"""
    
    attempt_id: str = Field(..., description="UUID попытки")
    mode: ExamMode = Field(..., description="Режим")
    started_at: datetime = Field(..., description="Время начала")
    time_limit_minutes: int | None = Field(None, description="Лимит времени (минуты)")
    total_questions: int = Field(..., description="Всего вопросов")
    
    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "123e4567-e89b-12d3-a456-426614174000",
                "mode": "exam",
                "started_at": "2025-10-25T10:00:00Z",
                "time_limit_minutes": 90,
                "total_questions": 50
            }
        }


# ===================================
# Получение вопросов
# ===================================

class GetQuestionsRequest(BaseModel):
    """Запрос на получение вопросов (для Practice)"""
    
    offset: int = Field(default=0, ge=0, description="Смещение")
    limit: int = Field(default=20, ge=1, le=100, description="Количество вопросов")


class GetQuestionsResponse(BaseModel):
    """Ответ с вопросами (БЕЗ правильных ответов!)"""
    
    questions: list[QuestionResponse] = Field(..., description="Вопросы")
    total: int = Field(..., description="Всего вопросов в предмете")
    offset: int = Field(..., description="Текущее смещение")
    limit: int = Field(..., description="Лимит")
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


# ===================================
# Ответ на вопрос
# ===================================

class SubmitAnswerRequest(BaseModel):
    """Отправка ответа на вопрос"""
    
    question_id: str = Field(..., description="UUID вопроса")
    selected_keys: list[str] = Field(..., min_length=1, description="Выбранные ключи (A, B, C...)")
    
    @field_validator("selected_keys")
    @classmethod
    def validate_keys(cls, v):
        valid_keys = {"A", "B", "C", "D", "E", "F"}
        for key in v:
            if key not in valid_keys:
                raise ValueError(f"Недопустимый ключ: {key}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "3a5e96ce-1dbd-4982-9c17-6eecf071c813",
                "selected_keys": ["B"]
            }
        }


class SubmitAnswerResponse(BaseModel):
    """
    Ответ после отправки ответа
    Для Practice Mode - с проверкой (сразу показываем правильно/неправильно)
    Для Exam Mode - БЕЗ проверки (просто подтверждение)
    """
    
    question_id: str = Field(..., description="UUID вопроса")
    is_correct: bool | None = Field(None, description="Правильно ли (только для Practice)")
    correct_keys: list[str] | None = Field(None, description="Правильные ключи (только для Practice)")
    explanation: str | None = Field(None, description="Объяснение (только для Practice)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "3a5e96ce-1dbd-4982-9c17-6eecf071c813",
                "is_correct": True,
                "correct_keys": ["B"],
                "explanation": "Столица Казахстана - Астана"
            }
        }


# ===================================
# Состояние экзамена
# ===================================

class ExamStatusResponse(BaseModel):
    """Текущее состояние экзамена/практики"""
    
    attempt_id: str = Field(..., description="UUID попытки")
    mode: ExamMode = Field(..., description="Режим")
    status: ExamStatus = Field(..., description="Статус")
    started_at: datetime = Field(..., description="Время начала")
    completed_at: datetime | None = Field(None, description="Время завершения")
    time_limit_minutes: int | None = Field(None, description="Лимит времени")
    time_remaining_seconds: int | None = Field(None, description="Осталось времени (секунды)")
    total_questions: int = Field(..., description="Всего вопросов")
    answered_questions: int = Field(..., description="Отвечено вопросов")
    current_question_index: int = Field(default=0, description="Индекс текущего вопроса")
    
    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "123e4567-e89b-12d3-a456-426614174000",
                "mode": "exam",
                "status": "in_progress",
                "started_at": "2025-10-25T10:00:00Z",
                "completed_at": None,
                "time_limit_minutes": 90,
                "time_remaining_seconds": 4500,
                "total_questions": 50,
                "answered_questions": 10,
                "current_question_index": 10
            }
        }


# ===================================
# Завершение экзамена
# ===================================

class ExamSubmitRequest(BaseModel):
    """Запрос на завершение экзамена"""
    
    # Можно добавить подтверждение
    confirmed: bool = Field(default=True, description="Подтверждение завершения")


class ExamResultResponse(BaseModel):
    """Результаты экзамена"""
    
    attempt_id: str = Field(..., description="UUID попытки")
    mode: ExamMode = Field(..., description="Режим")
    status: ExamStatus = Field(..., description="Статус")
    started_at: datetime = Field(..., description="Время начала")
    completed_at: datetime = Field(..., description="Время завершения")
    total_questions: int = Field(..., description="Всего вопросов")
    answered_questions: int = Field(..., description="Отвечено вопросов")
    correct_answers: int = Field(..., description="Правильных ответов")
    score_percentage: float = Field(..., description="Процент правильных ответов")
    passed: bool = Field(..., description="Сдал ли экзамен")
    
    # Прокторинг
    proctoring_copy_paste_count: int = Field(default=0, description="Копирований/вставок")
    proctoring_tab_switches_count: int = Field(default=0, description="Переключений вкладок")
    proctoring_console_opens_count: int = Field(default=0, description="Открытий консоли")
    proctoring_suspicious: bool = Field(default=False, description="Подозрительная активность")
    
    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "123e4567-e89b-12d3-a456-426614174000",
                "mode": "exam",
                "status": "completed",
                "started_at": "2025-10-25T10:00:00Z",
                "completed_at": "2025-10-25T11:30:00Z",
                "total_questions": 50,
                "answered_questions": 50,
                "correct_answers": 42,
                "score_percentage": 84.0,
                "passed": True,
                "proctoring_copy_paste_count": 2,
                "proctoring_tab_switches_count": 5,
                "proctoring_console_opens_count": 0,
                "proctoring_suspicious": False
            }
        }


class ExamResultWithQuestionsResponse(ExamResultResponse):
    """Результаты с вопросами и правильными ответами"""
    
    questions: list[QuestionWithCorrectResponse] = Field(..., description="Вопросы с правильными ответами")
    user_answers: dict[str, list[str]] = Field(..., description="Ответы пользователя {question_id: [keys]}")
    
    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "123e4567-e89b-12d3-a456-426614174000",
                "mode": "exam",
                "status": "completed",
                "started_at": "2025-10-25T10:00:00Z",
                "completed_at": "2025-10-25T11:30:00Z",
                "total_questions": 50,
                "answered_questions": 50,
                "correct_answers": 42,
                "score_percentage": 84.0,
                "passed": True,
                "proctoring_copy_paste_count": 2,
                "proctoring_tab_switches_count": 5,
                "proctoring_console_opens_count": 0,
                "proctoring_suspicious": False,
                "questions": [],
                "user_answers": {}
            }
        }


# ===================================
# Статистика
# ===================================

class UserStatisticsResponse(BaseModel):
    """Статистика пользователя"""
    
    total_practice_attempts: int = Field(default=0, description="Всего попыток практики")
    total_exam_attempts: int = Field(default=0, description="Всего попыток экзаменов")
    average_score: float = Field(default=0.0, description="Средний балл")
    best_score: float = Field(default=0.0, description="Лучший балл")
    subjects_stats: dict[str, dict] = Field(default_factory=dict, description="Статистика по предметам")
    recent_attempts: list[ExamResultResponse] = Field(default_factory=list, description="Недавние попытки")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_practice_attempts": 15,
                "total_exam_attempts": 3,
                "average_score": 78.5,
                "best_score": 92.0,
                "subjects_stats": {
                    "TGO": {
                        "answered": 100,
                        "correct": 85,
                        "accuracy": 85.0
                    }
                },
                "recent_attempts": []
            }
        }
