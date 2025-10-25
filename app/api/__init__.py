"""
API роутеры
"""
from app.api.auth import router as auth_router
from app.api.majors import router as majors_router
from app.api.subjects import router as subjects_router
from app.api.practice import router as practice_router
from app.api.exam import router as exam_router
from app.api.stats import router as stats_router
from app.api.admin import router as admin_router

__all__ = [
    "auth_router",
    "majors_router",
    "subjects_router",
    "practice_router",
    "exam_router",
    "stats_router",
    "admin_router",
]
