"""
Модели приложения
"""
from app.db.base import Base

# Импортируем все модели чтобы Alembic их видел
from app.models.user import User, UserRole
from app.models.major import Major, MagistracyType
from app.models.subject import Subject, SubjectType
from app.models.question import Question, QuestionDifficulty, QuestionType
from app.models.exam import ExamAttempt, ExamAnswer, ExamMode, ExamStatus
from app.models.proctoring import ProctoringEvent, ProctoringEventType

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Major",
    "MagistracyType",
    "Subject",
    "SubjectType",
    "Question",
    "QuestionDifficulty",
    "QuestionType",
    "ExamAttempt",
    "ExamAnswer",
    "ExamMode",
    "ExamStatus",
    "ProctoringEvent",
    "ProctoringEventType",
]
