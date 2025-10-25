"""
Сервисы приложения (бизнес-логика)
"""

from app.services.redis_service import redis_service, RedisService
from app.services.auth_service import auth_service, AuthService
from app.services.user_service import user_service, UserService
from app.services.question_service import question_service, QuestionService
from app.services.practice_service import practice_service, PracticeService
from app.services.exam_service import exam_service, ExamService
from app.services.proctoring_service import proctoring_service, ProctoringService

__all__ = [
    "redis_service",
    "RedisService",
    "auth_service",
    "AuthService",
    "user_service",
    "UserService",
    "question_service",
    "QuestionService",
    "practice_service",
    "PracticeService",
    "exam_service",
    "ExamService",
    "proctoring_service",
    "ProctoringService",
]
