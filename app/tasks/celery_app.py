"""
Celery приложение для фоновых задач
"""
from celery import Celery
from app.core.config import settings

# Создаем Celery app
celery_app = Celery(
    "connect_aitu",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
    include=[
        "app.tasks.exam_tasks",
        "app.tasks.cleanup_tasks",
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,  # 1 час
    
    # Task execution
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Retry settings
    task_default_retry_delay=60,  # 1 минута
    task_max_retries=3,
    
    # Beat schedule (периодические задачи)
    beat_schedule={
        "cleanup-expired-exams": {
            "task": "app.tasks.cleanup_tasks.cleanup_expired_exams",
            "schedule": 300.0,  # Каждые 5 минут
        },
        "cleanup-old-redis-sessions": {
            "task": "app.tasks.cleanup_tasks.cleanup_old_redis_sessions",
            "schedule": 3600.0,  # Каждый час
        },
    },
)

# Task routes (опционально)
celery_app.conf.task_routes = {
    "app.tasks.exam_tasks.*": {"queue": "exams"},
    "app.tasks.cleanup_tasks.*": {"queue": "cleanup"},
}


if __name__ == "__main__":
    celery_app.start()
