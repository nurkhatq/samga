"""
Pydantic схемы для специальностей (Majors)
"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.major import MagistracyType


class MajorBase(BaseModel):
    """Базовые поля специальности"""
    
    code: str = Field(..., max_length=10, description="Код специальности (M001, M002...)")
    title_kk: str = Field(..., max_length=500, description="Название на казахском")
    title_ru: str | None = Field(None, max_length=500, description="Название на русском")
    magistracy_type: MagistracyType = Field(..., description="Тип магистратуры")
    categories: list[str] = Field(default_factory=list, description="Профильные предметы")
    is_active: bool = Field(default=True, description="Активна ли специальность")


class MajorCreate(MajorBase):
    """Создание специальности"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "M001",
                "title_kk": "M001 - Педагогика және Психология",
                "title_ru": "M001 - Педагогика и Психология",
                "magistracy_type": "profile",
                "categories": [
                    "M001 - Педагогика",
                    "M001 - Психология"
                ],
                "is_active": True
            }
        }


class MajorUpdate(BaseModel):
    """Обновление специальности"""
    
    title_kk: str | None = Field(None, max_length=500, description="Название на казахском")
    title_ru: str | None = Field(None, max_length=500, description="Название на русском")
    magistracy_type: MagistracyType | None = Field(None, description="Тип магистратуры")
    categories: list[str] | None = Field(None, description="Профильные предметы")
    is_active: bool | None = Field(None, description="Активна ли специальность")


class MajorResponse(MajorBase):
    """Ответ с данными специальности"""
    
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    
    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "code": "M001",
                "title_kk": "M001 - Педагогика және Психология",
                "title_ru": "M001 - Педагогика и Психология",
                "magistracy_type": "profile",
                "categories": [
                    "M001 - Педагогика",
                    "M001 - Психология"
                ],
                "is_active": True,
                "created_at": "2025-10-25T10:00:00Z",
                "updated_at": "2025-10-25T10:00:00Z"
            }
        }


class MajorListResponse(BaseModel):
    """Список специальностей"""
    
    majors: list[MajorResponse] = Field(..., description="Специальности")
    total: int = Field(..., description="Общее количество")
    
    class Config:
        json_schema_extra = {
            "example": {
                "majors": [],
                "total": 153
            }
        }


class MajorWithSubjectsResponse(MajorResponse):
    """Специальность с предметами для экзамена"""
    
    exam_subjects: list[str] = Field(..., description="Предметы для экзамена")
    total_questions: int = Field(..., description="Общее количество вопросов для экзамена")
    time_limit_minutes: int = Field(..., description="Время экзамена (минуты)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "M001",
                "title_kk": "M001 - Педагогика және Психология",
                "title_ru": "M001 - Педагогика и Психология",
                "magistracy_type": "profile",
                "categories": [
                    "M001 - Педагогика",
                    "M001 - Психология"
                ],
                "is_active": True,
                "created_at": "2025-10-25T10:00:00Z",
                "updated_at": "2025-10-25T10:00:00Z",
                "exam_subjects": ["ENG", "TGO", "M001_PEDAGOGY", "M001_PSYCHOLOGY"],
                "total_questions": 50,
                "time_limit_minutes": 90
            }
        }
