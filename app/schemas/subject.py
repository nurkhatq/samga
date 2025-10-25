"""
Pydantic схемы для предметов (Subjects)
"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.subject import SubjectType


class SubjectBase(BaseModel):
    """Базовые поля предмета"""
    
    code: str = Field(..., max_length=50, description="Код предмета")
    title_kk: str = Field(..., max_length=500, description="Название на казахском")
    title_ru: str | None = Field(None, max_length=500, description="Название на русском")
    subject_type: SubjectType = Field(..., description="Тип предмета (общий/профильный)")
    major_code: str | None = Field(None, max_length=10, description="Код специальности (для профильных)")
    is_active: bool = Field(default=True, description="Активен ли предмет")


class SubjectCreate(SubjectBase):
    """Создание предмета"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "TGO",
                "title_kk": "Тарих, география және обществознание",
                "title_ru": "История, география и обществоведение",
                "subject_type": "common",
                "major_code": None,
                "is_active": True
            }
        }


class SubjectUpdate(BaseModel):
    """Обновление предмета"""
    
    title_kk: str | None = Field(None, max_length=500, description="Название на казахском")
    title_ru: str | None = Field(None, max_length=500, description="Название на русском")
    is_active: bool | None = Field(None, description="Активен ли предмет")


class SubjectResponse(SubjectBase):
    """Ответ с данными предмета"""
    
    questions_count: int = Field(default=0, description="Количество вопросов")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": "TGO",
                "title_kk": "Тарих, география және обществознание",
                "title_ru": "История, география и обществоведение",
                "subject_type": "common",
                "major_code": None,
                "is_active": True,
                "questions_count": 2000,
                "created_at": "2025-10-25T10:00:00Z",
                "updated_at": "2025-10-25T10:00:00Z"
            }
        }


class SubjectListResponse(BaseModel):
    """Список предметов"""
    
    subjects: list[SubjectResponse] = Field(..., description="Предметы")
    total: int = Field(..., description="Общее количество")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subjects": [],
                "total": 0
            }
        }


class SubjectStatsResponse(BaseModel):
    """Статистика по предмету"""
    
    subject_code: str = Field(..., description="Код предмета")
    total_questions: int = Field(..., description="Всего вопросов")
    answered_questions: int = Field(default=0, description="Отвечено вопросов")
    correct_answers: int = Field(default=0, description="Правильных ответов")
    accuracy_percentage: float = Field(default=0.0, description="Процент правильных ответов")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject_code": "TGO",
                "total_questions": 2000,
                "answered_questions": 100,
                "correct_answers": 85,
                "accuracy_percentage": 85.0
            }
        }
