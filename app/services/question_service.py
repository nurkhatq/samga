"""
Сервис для работы с вопросами
КРИТИЧЕСКИ ВАЖНО: методы get_questions* возвращают вопросы БЕЗ is_correct!
"""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.question import Question
from app.schemas.question import QuestionResponse, QuestionOptionResponse


class QuestionService:
    """Сервис для работы с вопросами"""
    
    @staticmethod
    async def get_question_by_id(
        db: AsyncSession,
        question_id: uuid.UUID,
        safe: bool = True
    ) -> Question:
        """
        Получить вопрос по ID
        
        Args:
            db: Сессия БД
            question_id: UUID вопроса
            safe: Если True - возвращает без is_correct (для фронта)
        
        Returns:
            Question модель
        
        Raises:
            HTTPException: Если вопрос не найден
        """
        result = await db.execute(
            select(Question).where(Question.id == question_id)
        )
        question = result.scalar_one_or_none()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вопрос не найден"
            )
        
        return question
    
    @staticmethod
    def question_to_safe_dict(question: Question) -> dict:
        """
        Преобразовать вопрос в безопасный dict БЕЗ is_correct
        
        Args:
            question: Question модель
        
        Returns:
            dict с вопросом БЕЗ правильных ответов
        """
        return {
            "id": str(question.id),
            "subject_code": question.subject_code,
            "question_text": question.question_text,
            "options": [
                {"key": opt["key"], "text": opt["text"]}
                for opt in question.options
            ],
            "difficulty": question.difficulty.value,
            "question_type": question.question_type.value,
            "points": question.points,
            "time_seconds": question.time_seconds,
            "explanation": None,  # НЕ показываем explanation до проверки
            "tags": question.tags,
        }
    
    @staticmethod
    async def get_questions_by_subject(
        db: AsyncSession,
        subject_code: str,
        offset: int = 0,
        limit: int = 20,
        safe: bool = True
    ) -> tuple[list[Question], int]:
        """
        Получить вопросы по предмету с пагинацией
        
        Args:
            db: Сессия БД
            subject_code: Код предмета
            offset: Смещение
            limit: Количество вопросов
            safe: Если True - БЕЗ is_correct
        
        Returns:
            (список вопросов, общее количество)
        """
        # Общее количество вопросов
        count_result = await db.execute(
            select(func.count(Question.id))
            .where(Question.subject_code == subject_code)
        )
        total = count_result.scalar() or 0
        
        # Получаем вопросы
        result = await db.execute(
            select(Question)
            .where(Question.subject_code == subject_code)
            .offset(offset)
            .limit(limit)
        )
        questions = result.scalars().all()
        
        return list(questions), total
    
    @staticmethod
    async def get_random_questions(
        db: AsyncSession,
        subject_code: str,
        count: int,
        exclude_ids: list[uuid.UUID] | None = None
    ) -> list[Question]:
        """
        Получить случайные вопросы по предмету
        
        Args:
            db: Сессия БД
            subject_code: Код предмета
            count: Количество вопросов
            exclude_ids: Исключить эти вопросы
        
        Returns:
            Список случайных вопросов
        """
        query = select(Question).where(Question.subject_code == subject_code)
        
        # Исключаем уже использованные вопросы
        if exclude_ids:
            query = query.where(~Question.id.in_(exclude_ids))
        
        # Случайная выборка
        query = query.order_by(func.random()).limit(count)
        
        result = await db.execute(query)
        questions = result.scalars().all()
        
        return list(questions)
    
    @staticmethod
    def check_answer(
        question: Question,
        selected_keys: list[str]
    ) -> tuple[bool, list[str]]:
        """
        Проверить ответ на вопрос
        ТОЛЬКО НА БЕКЕНДЕ!
        
        Args:
            question: Question модель
            selected_keys: Выбранные ключи (["A"], ["B", "C"])
        
        Returns:
            (is_correct, correct_keys)
        """
        # Получаем правильные ключи
        correct_keys = question.get_correct_keys()
        
        # Сортируем для корректного сравнения
        selected_sorted = sorted(selected_keys)
        correct_sorted = sorted(correct_keys)
        
        # Проверяем совпадение
        is_correct = selected_sorted == correct_sorted
        
        return is_correct, correct_keys
    
    @staticmethod
    async def count_questions_by_subject(
        db: AsyncSession,
        subject_code: str
    ) -> int:
        """Подсчитать количество вопросов по предмету"""
        result = await db.execute(
            select(func.count(Question.id))
            .where(Question.subject_code == subject_code)
        )
        return result.scalar() or 0


# Создаем глобальный экземпляр
question_service = QuestionService()
