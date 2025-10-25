"""
Сервис свободного режима (Practice Mode)
- Пагинация по 20 вопросов
- Мгновенная проверка ответов
- Сохранение прогресса в Redis
"""
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.models.subject import Subject
from app.services.redis_service import redis_service
from app.services.question_service import question_service
from app.schemas.exam import (
    PracticeStartRequest,
    ExamStartResponse,
    GetQuestionsResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.schemas.question import QuestionResponse, QuestionOptionResponse
from app.core.config import settings
from sqlalchemy import select


class PracticeService:
    """Сервис для свободного режима"""
    
    @staticmethod
    async def start_practice(
        db: AsyncSession,
        user: User,
        request: PracticeStartRequest
    ) -> ExamStartResponse:
        """
        Начать свободный режим
        
        Args:
            db: Сессия БД
            user: Пользователь
            request: Запрос с subject_code
        
        Returns:
            Информация о начатой практике
        
        Raises:
            HTTPException: Если предмет не найден
        """
        # Проверяем существование предмета
        result = await db.execute(
            select(Subject).where(
                Subject.code == request.subject_code,
                Subject.is_active == True
            )
        )
        subject = result.scalar_one_or_none()
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        
        # Подсчитываем общее количество вопросов
        total_questions = await question_service.count_questions_by_subject(
            db, request.subject_code
        )
        
        if total_questions == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="В предмете нет вопросов"
            )
        
        # Инициализируем прогресс в Redis
        progress = {
            "answered_questions": [],
            "correct_count": 0,
            "total_count": 0,
            "last_offset": 0,
        }
        
        await redis_service.save_practice_progress(
            user.id,
            request.subject_code,
            progress
        )
        
        # Генерируем уникальный ID для сессии практики
        session_id = str(uuid.uuid4())
        
        return ExamStartResponse(
            attempt_id=session_id,
            mode="practice",
            started_at=datetime.utcnow(),
            time_limit_minutes=None,  # Нет ограничения по времени
            total_questions=total_questions
        )
    
    @staticmethod
    async def get_questions(
        db: AsyncSession,
        user: User,
        subject_code: str,
        offset: int = 0,
        limit: int = 20
    ) -> GetQuestionsResponse:
        """
        Получить вопросы с пагинацией (БЕЗ правильных ответов!)
        
        Args:
            db: Сессия БД
            user: Пользователь
            subject_code: Код предмета
            offset: Смещение
            limit: Количество вопросов (макс 100)
        
        Returns:
            Список вопросов БЕЗ is_correct
        """
        # Ограничиваем лимит
        if limit > 100:
            limit = 100
        
        # Получаем вопросы из БД
        questions, total = await question_service.get_questions_by_subject(
            db, subject_code, offset, limit, safe=True
        )
        
        # Преобразуем в безопасный формат БЕЗ is_correct
        safe_questions = [
            QuestionResponse(
                id=str(q.id),
                subject_code=q.subject_code,
                question_text=q.question_text,
                options=[
                    QuestionOptionResponse(key=opt["key"], text=opt["text"])
                    for opt in q.options
                ],
                difficulty=q.difficulty,
                question_type=q.question_type,
                points=q.points,
                time_seconds=q.time_seconds,
                explanation=None,  # НЕ показываем до проверки
                tags=q.tags
            )
            for q in questions
        ]
        
        # Обновляем прогресс в Redis
        progress = await redis_service.get_practice_progress(user.id, subject_code)
        if progress:
            progress["last_offset"] = offset + len(questions)
            await redis_service.save_practice_progress(user.id, subject_code, progress)
        
        return GetQuestionsResponse(
            questions=safe_questions,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + len(questions)) < total
        )
    
    @staticmethod
    async def submit_answer(
        db: AsyncSession,
        user: User,
        subject_code: str,
        request: SubmitAnswerRequest
    ) -> SubmitAnswerResponse:
        """
        Отправить ответ в свободном режиме
        С МГНОВЕННОЙ ПРОВЕРКОЙ!
        
        Args:
            db: Сессия БД
            user: Пользователь
            subject_code: Код предмета
            request: Ответ пользователя
        
        Returns:
            Результат проверки (is_correct, correct_keys, explanation)
        """
        # Получаем вопрос
        question_uuid = uuid.UUID(request.question_id)
        question = await question_service.get_question_by_id(
            db, question_uuid, safe=False
        )
        
        # Проверяем что вопрос из этого предмета
        if question.subject_code != subject_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вопрос не принадлежит этому предмету"
            )
        
        # Проверяем ответ (ТОЛЬКО НА БЕКЕНДЕ!)
        is_correct, correct_keys = question_service.check_answer(
            question, request.selected_keys
        )
        
        # Обновляем прогресс в Redis
        progress = await redis_service.get_practice_progress(user.id, subject_code)
        if progress:
            # Добавляем вопрос в answered_questions если его еще нет
            if request.question_id not in progress["answered_questions"]:
                progress["answered_questions"].append(request.question_id)
                progress["total_count"] += 1
                
                if is_correct:
                    progress["correct_count"] += 1
            
            await redis_service.save_practice_progress(user.id, subject_code, progress)
        
        # Возвращаем результат проверки
        return SubmitAnswerResponse(
            question_id=request.question_id,
            is_correct=is_correct,
            correct_keys=correct_keys,
            explanation=question.explanation
        )
    
    @staticmethod
    async def get_practice_stats(
        user: User,
        subject_code: str
    ) -> dict:
        """
        Получить статистику по свободному режиму
        
        Returns:
            {
                "answered_questions": 100,
                "correct_count": 85,
                "accuracy_percentage": 85.0
            }
        """
        progress = await redis_service.get_practice_progress(user.id, subject_code)
        
        if not progress:
            return {
                "answered_questions": 0,
                "correct_count": 0,
                "accuracy_percentage": 0.0
            }
        
        total = progress.get("total_count", 0)
        correct = progress.get("correct_count", 0)
        
        accuracy = (correct / total * 100) if total > 0 else 0.0
        
        return {
            "answered_questions": total,
            "correct_count": correct,
            "accuracy_percentage": round(accuracy, 2)
        }
    
    @staticmethod
    async def finish_practice(
        user: User,
        subject_code: str
    ) -> dict:
        """
        Завершить практику и получить итоговую статистику
        
        Returns:
            Финальная статистика
        """
        stats = await PracticeService.get_practice_stats(user, subject_code)
        
        # Удаляем прогресс из Redis (опционально)
        # await redis_service.delete_practice_progress(user.id, subject_code)
        
        return stats


# Создаем глобальный экземпляр
practice_service = PracticeService()
