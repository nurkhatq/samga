"""
Сервис прокторинга
Отслеживание подозрительных действий во время экзамена
"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
import uuid

from app.models.user import User
from app.models.exam import ExamAttempt, ExamStatus
from app.models.proctoring import ProctoringEvent, ProctoringEventType
from app.services.redis_service import redis_service
from app.schemas.proctoring import (
    ProctoringEventCreate,
    ProctoringEventBatchCreate,
    ProctoringStatisticsResponse,
)


class ProctoringService:
    """Сервис для прокторинга"""
    
    @staticmethod
    async def log_event(
        db: AsyncSession,
        user: User,
        attempt_id: str,
        event: ProctoringEventCreate
    ) -> bool:
        """
        Зафиксировать событие прокторинга
        
        Args:
            db: Сессия БД
            user: Пользователь
            attempt_id: UUID попытки экзамена
            event: Данные события
        
        Returns:
            True если успешно
        
        Raises:
            HTTPException: Если попытка не найдена
        """
        # Проверяем попытку
        attempt_uuid = uuid.UUID(attempt_id)
        result = await db.execute(
            select(ExamAttempt).where(
                ExamAttempt.id == attempt_uuid,
                ExamAttempt.user_id == user.id,
                ExamAttempt.status == ExamStatus.IN_PROGRESS
            )
        )
        attempt = result.scalar_one_or_none()
        
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Активная попытка экзамена не найдена"
            )
        
        # Сохраняем событие в БД
        proctoring_event = ProctoringEvent(
            attempt_id=attempt_uuid,
            event_type=event.event_type,
            timestamp=datetime.utcnow(),
            proctoring_metadata=event.metadata
        )
        db.add(proctoring_event)
        
        # Обновляем счетчики в Redis сессии
        await redis_service.increment_proctoring_event(
            attempt_id,
            event.event_type.value
        )
        
        await db.commit()
        
        return True
    
    @staticmethod
    async def log_events_batch(
        db: AsyncSession,
        user: User,
        attempt_id: str,
        batch: ProctoringEventBatchCreate
    ) -> int:
        """
        Зафиксировать несколько событий прокторинга
        
        Args:
            db: Сессия БД
            user: Пользователь
            attempt_id: UUID попытки
            batch: Пакет событий (макс 100)
        
        Returns:
            Количество созданных событий
        """
        # Проверяем попытку
        attempt_uuid = uuid.UUID(attempt_id)
        result = await db.execute(
            select(ExamAttempt).where(
                ExamAttempt.id == attempt_uuid,
                ExamAttempt.user_id == user.id,
                ExamAttempt.status == ExamStatus.IN_PROGRESS
            )
        )
        attempt = result.scalar_one_or_none()
        
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Активная попытка экзамена не найдена"
            )
        
        # Сохраняем все события
        created_count = 0
        current_time = datetime.utcnow()
        
        for event in batch.events:
            proctoring_event = ProctoringEvent(
                attempt_id=attempt_uuid,
                event_type=event.event_type,
                timestamp=current_time,
                proctoring_metadata=event.metadata
            )
            db.add(proctoring_event)
            created_count += 1
            
            # Обновляем счетчики в Redis
            await redis_service.increment_proctoring_event(
                attempt_id,
                event.event_type.value
            )
        
        await db.commit()
        
        return created_count
    
    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        user: User,
        attempt_id: str
    ) -> ProctoringStatisticsResponse:
        """
        Получить статистику прокторинга для попытки
        
        Args:
            db: Сессия БД
            user: Пользователь
            attempt_id: UUID попытки
        
        Returns:
            Статистика прокторинга
        """
        # Проверяем попытку
        attempt_uuid = uuid.UUID(attempt_id)
        result = await db.execute(
            select(ExamAttempt).where(
                ExamAttempt.id == attempt_uuid,
                ExamAttempt.user_id == user.id
            )
        )
        attempt = result.scalar_one_or_none()
        
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Попытка экзамена не найдена"
            )
        
        # Получаем все события из БД
        events_result = await db.execute(
            select(ProctoringEvent)
            .where(ProctoringEvent.attempt_id == attempt_uuid)
        )
        events = events_result.scalars().all()
        
        # Подсчитываем события по типам
        events_by_type = {}
        for event in events:
            event_type = event.event_type.value
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
        
        # Группируем по категориям
        copy_paste_count = (
            events_by_type.get("copy", 0) +
            events_by_type.get("paste", 0) +
            events_by_type.get("cut", 0)
        )
        
        tab_switches_count = (
            events_by_type.get("tab_switch", 0) +
            events_by_type.get("window_blur", 0)
        )
        
        console_opens_count = events_by_type.get("console_open", 0)
        
        # Определяем подозрительность
        total_suspicious = copy_paste_count + tab_switches_count + console_opens_count
        from app.core.config import settings
        suspicious = total_suspicious >= settings.PROCTORING_SUSPICIOUS_THRESHOLD
        
        return ProctoringStatisticsResponse(
            attempt_id=str(attempt.id),
            total_events=len(events),
            copy_paste_count=copy_paste_count,
            tab_switches_count=tab_switches_count,
            console_opens_count=console_opens_count,
            suspicious=suspicious,
            events_by_type=events_by_type
        )


# Создаем глобальный экземпляр
proctoring_service = ProctoringService()
