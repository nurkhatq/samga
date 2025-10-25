"""
Celery задачи
"""
from app.tasks.celery_app import celery_app
from app.tasks.exam_tasks import auto_finish_exam, send_exam_reminder
from app.tasks.cleanup_tasks import (
    cleanup_expired_exams,
    cleanup_old_redis_sessions,
    cleanup_old_proctoring_events,
    archive_old_attempts,
)

__all__ = [
    "celery_app",
    "auto_finish_exam",
    "send_exam_reminder",
    "cleanup_expired_exams",
    "cleanup_old_redis_sessions",
    "cleanup_old_proctoring_events",
    "archive_old_attempts",
]
