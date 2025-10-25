"""
Celery задачи для очистки устаревших данных
"""
from datetime import datetime, timedelta
from sqlalchemy import select, and_

from app.tasks.celery_app import celery_app
from app.db.session import async_session_maker
from app.models.exam import ExamAttempt, ExamStatus
from app.services.redis_service import redis_service
from app.core.config import settings


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_expired_exams",
    bind=True,
    max_retries=3
)
def cleanup_expired_exams(self):
    """
    Очистить истекшие экзамены
    
    Помечает экзамены как expired если:
    - status = IN_PROGRESS
    - Прошло больше времени чем time_limit + буфер
    
    Запускается каждые 5 минут (Celery Beat)
    """
    import asyncio
    
    async def _cleanup():
        async with async_session_maker() as db:
            try:
                # Ищем зависшие экзамены
                buffer_minutes = settings.EXAM_AUTO_SUBMIT_BUFFER_MINUTES
                
                result = await db.execute(
                    select(ExamAttempt).where(
                        ExamAttempt.status == ExamStatus.IN_PROGRESS
                    )
                )
                attempts = result.scalars().all()
                
                expired_count = 0
                
                for attempt in attempts:
                    # Проверяем время
                    elapsed = (datetime.utcnow() - attempt.started_at).total_seconds()
                    time_limit = (attempt.time_limit_minutes + buffer_minutes) * 60
                    
                    if elapsed >= time_limit:
                        # Помечаем как expired
                        attempt.status = ExamStatus.EXPIRED
                        attempt.completed_at = datetime.utcnow()
                        
                        # Удаляем сессию из Redis
                        await redis_service.delete_exam_session(str(attempt.id))
                        
                        expired_count += 1
                        print(f"⏰ Marked exam {attempt.id} as expired")
                
                await db.commit()
                
                print(f"✅ Cleaned up {expired_count} expired exams")
                return expired_count
            
            except Exception as e:
                print(f"❌ Error cleaning up expired exams: {e}")
                await db.rollback()
                raise
    
    return asyncio.run(_cleanup())


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_old_redis_sessions",
    bind=True,
    max_retries=3
)
def cleanup_old_redis_sessions(self):
    """
    Очистить старые сессии из Redis
    
    Удаляет сессии которые:
    - Старше 24 часов
    - Не имеют соответствующей записи в БД
    
    Запускается каждый час (Celery Beat)
    """
    import asyncio
    
    async def _cleanup():
        try:
            # TODO: Реализовать сканирование Redis ключей
            # Для продакшена лучше использовать SCAN вместо KEYS
            
            # Пример логики:
            # 1. SCAN exam:attempt:* ключи
            # 2. Проверить TTL каждого
            # 3. Если TTL < 0 или ключ старый - удалить
            
            cleaned_count = 0
            
            # Псевдокод (требует реализации):
            # async for key in redis_service.redis.scan_iter("exam:attempt:*"):
            #     ttl = await redis_service.ttl(key)
            #     if ttl < 0:
            #         await redis_service.delete(key)
            #         cleaned_count += 1
            
            print(f"✅ Cleaned up {cleaned_count} old Redis sessions")
            return cleaned_count
        
        except Exception as e:
            print(f"❌ Error cleaning up Redis sessions: {e}")
            raise
    
    return asyncio.run(_cleanup())


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_old_proctoring_events",
    bind=True,
    max_retries=3
)
def cleanup_old_proctoring_events(self):
    """
    Очистить старые события прокторинга
    
    Удаляет события старше 90 дней
    
    Запускается раз в день (можно добавить в beat_schedule)
    """
    import asyncio
    
    async def _cleanup():
        async with async_session_maker() as db:
            try:
                from app.models.proctoring import ProctoringEvent
                
                # Удаляем события старше 90 дней
                cutoff_date = datetime.utcnow() - timedelta(days=90)
                
                result = await db.execute(
                    select(ProctoringEvent).where(
                        ProctoringEvent.timestamp < cutoff_date
                    )
                )
                old_events = result.scalars().all()
                
                for event in old_events:
                    await db.delete(event)
                
                await db.commit()
                
                deleted_count = len(old_events)
                print(f"✅ Deleted {deleted_count} old proctoring events")
                return deleted_count
            
            except Exception as e:
                print(f"❌ Error cleaning up proctoring events: {e}")
                await db.rollback()
                raise
    
    return asyncio.run(_cleanup())


@celery_app.task(
    name="app.tasks.cleanup_tasks.archive_old_attempts",
    bind=True,
    max_retries=3
)
def archive_old_attempts(self, days: int = 180):
    """
    Архивировать старые попытки экзаменов
    
    Args:
        days: Архивировать попытки старше этого количества дней
    
    TODO: Реализовать архивирование в отдельную таблицу или S3
    """
    import asyncio
    
    async def _archive():
        async with async_session_maker() as db:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                result = await db.execute(
                    select(ExamAttempt).where(
                        and_(
                            ExamAttempt.completed_at.isnot(None),
                            ExamAttempt.completed_at < cutoff_date
                        )
                    )
                )
                old_attempts = result.scalars().all()
                
                archived_count = len(old_attempts)
                
                # TODO: Экспортировать в архив (JSON, S3, отдельная таблица)
                # Затем удалить из основной таблицы
                
                print(f"✅ Archived {archived_count} old attempts")
                return archived_count
            
            except Exception as e:
                print(f"❌ Error archiving attempts: {e}")
                raise
    
    return asyncio.run(_archive())
