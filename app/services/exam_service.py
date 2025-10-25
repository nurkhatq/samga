"""
Сервис экзаменов (Exam Mode)
- Генерация вопросов по специальности
- Сохранение ответов БЕЗ проверки
- Автозавершение по таймеру (Celery)
- Проверка при завершении
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.models.major import Major, MagistracyType
from app.models.subject import Subject, SubjectType
from app.models.exam import ExamAttempt, ExamAnswer, ExamMode, ExamStatus
from app.models.question import Question
from app.services.redis_service import redis_service
from app.services.question_service import question_service
from app.schemas.exam import (
    ExamStartRequest,
    ExamStartResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    ExamStatusResponse,
    ExamResultResponse,
    ExamResultWithQuestionsResponse,
)
from app.schemas.question import QuestionResponse, QuestionWithCorrectResponse, QuestionOptionWithCorrect
from app.core.config import settings


class ExamService:
    """Сервис для экзаменов"""
    
    @staticmethod
    async def start_exam(
        db: AsyncSession,
        user: User,
        request: ExamStartRequest
    ) -> ExamStartResponse:
        """
        Начать пробный экзамен
        
        Args:
            db: Сессия БД
            user: Пользователь
            request: Запрос с major_code
        
        Returns:
            Информация о начатом экзамене
        
        Raises:
            HTTPException: Если специальность не найдена или недостаточно вопросов
        """
        # Получаем специальность
        result = await db.execute(
            select(Major).where(
                Major.code == request.major_code,
                Major.is_active == True
            )
        )
        major = result.scalar_one_or_none()
        
        if not major:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Специальность не найдена"
            )
        
        # Определяем параметры экзамена по типу магистратуры
        if major.magistracy_type == MagistracyType.PROFILE:
            # Профильная: 50 вопросов (30+20), 90 минут
            total_questions = settings.PROFILE_EXAM_QUESTIONS
            time_limit_minutes = settings.PROFILE_EXAM_TIME_MINUTES
            
            # Нужно: ТГО, АНГЛ, 2 профильных предмета
            required_subjects = ["TGO", "ENG"]
            
            # Получаем профильные предметы
            profile_result = await db.execute(
                select(Subject).where(
                    Subject.major_code == request.major_code,
                    Subject.subject_type == SubjectType.PROFILE,
                    Subject.is_active == True
                )
            )
            profile_subjects = profile_result.scalars().all()
            
            if len(profile_subjects) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недостаточно профильных предметов"
                )
            
            # Добавляем коды профильных предметов
            required_subjects.extend([s.code for s in profile_subjects[:2]])
            
            # Распределение вопросов: ТГО(10), АНГЛ(10), PROFILE1(15), PROFILE2(15)
            questions_distribution = {
                "TGO": 10,
                "ENG": 10,
                required_subjects[2]: 15,
                required_subjects[3]: 15,
            }
            
        else:
            # Научно-педагогическая: 130 вопросов, 180 минут
            total_questions = settings.SCIENTIFIC_EXAM_QUESTIONS
            time_limit_minutes = settings.SCIENTIFIC_EXAM_TIME_MINUTES
            
            # Нужно: Иностранный(50), ТГО(30), профильные(50)
            required_subjects = ["ENG", "TGO"]
            
            # Получаем профильные предметы
            profile_result = await db.execute(
                select(Subject).where(
                    Subject.major_code == request.major_code,
                    Subject.subject_type == SubjectType.PROFILE,
                    Subject.is_active == True
                )
            )
            profile_subjects = profile_result.scalars().all()
            
            if len(profile_subjects) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недостаточно профильных предметов"
                )
            
            required_subjects.extend([s.code for s in profile_subjects[:2]])
            
            # Распределение: ENG(50), TGO(30), PROFILE1(25), PROFILE2(25)
            questions_distribution = {
                "ENG": 50,
                "TGO": 30,
                required_subjects[2]: 25,
                required_subjects[3]: 25,
            }
        
        # Генерируем вопросы для экзамена
        all_question_ids = []
        
        for subject_code, count in questions_distribution.items():
            questions = await question_service.get_random_questions(
                db, subject_code, count
            )
            
            if len(questions) < count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Недостаточно вопросов по предмету {subject_code}"
                )
            
            all_question_ids.extend([str(q.id) for q in questions])
        
        # Создаем запись в БД
        attempt = ExamAttempt(
            user_id=user.id,
            mode=ExamMode.EXAM,
            major_code=request.major_code,
            started_at=datetime.utcnow(),
            time_limit_minutes=time_limit_minutes,
            status=ExamStatus.IN_PROGRESS,
            total_questions=total_questions,
        )
        
        db.add(attempt)
        await db.flush()
        await db.refresh(attempt)
        
        # Сохраняем сессию в Redis
        session_data = {
            "user_id": user.id,
            "major_code": request.major_code,
            "started_at": attempt.started_at.isoformat(),
            "questions": all_question_ids,
            "answers": {},
            "time_remaining": time_limit_minutes * 60,
            "proctoring": {
                "copy_paste": 0,
                "tab_switches": 0,
                "console_opens": 0,
            }
        }
        
        await redis_service.save_exam_session(
            str(attempt.id),
            session_data,
            expire_seconds=(time_limit_minutes + settings.EXAM_AUTO_SUBMIT_BUFFER_MINUTES) * 60
        )
        
        await db.commit()
        
        # TODO: Запустить Celery задачу на автозавершение
        # from app.tasks.exam_tasks import auto_finish_exam
        # auto_finish_exam.apply_async(
        #     args=[str(attempt.id)],
        #     countdown=time_limit_minutes * 60
        # )
        
        return ExamStartResponse(
            attempt_id=str(attempt.id),
            mode=ExamMode.EXAM,
            started_at=attempt.started_at,
            time_limit_minutes=time_limit_minutes,
            total_questions=total_questions
        )
    
    @staticmethod
    async def get_exam_status(
        db: AsyncSession,
        user: User,
        attempt_id: str
    ) -> ExamStatusResponse:
        """
        Получить текущее состояние экзамена
        
        Args:
            db: Сессия БД
            user: Пользователь
            attempt_id: UUID попытки
        
        Returns:
            Статус экзамена
        """
        # Получаем попытку из БД
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
        
        # Получаем сессию из Redis
        session = await redis_service.get_exam_session(attempt_id)
        
        # Вычисляем оставшееся время
        time_remaining = None
        if attempt.time_limit_minutes and attempt.status == ExamStatus.IN_PROGRESS:
            elapsed = (datetime.utcnow() - attempt.started_at).total_seconds()
            total_time = attempt.time_limit_minutes * 60
            time_remaining = max(0, int(total_time - elapsed))
        
        # Текущий индекс вопроса
        current_index = len(session.get("answers", {})) if session else attempt.answered_questions
        
        return ExamStatusResponse(
            attempt_id=str(attempt.id),
            mode=attempt.mode,
            status=attempt.status,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            time_limit_minutes=attempt.time_limit_minutes,
            time_remaining_seconds=time_remaining,
            total_questions=attempt.total_questions,
            answered_questions=attempt.answered_questions,
            current_question_index=current_index
        )
    
    @staticmethod
    async def submit_answer(
        db: AsyncSession,
        user: User,
        attempt_id: str,
        request: SubmitAnswerRequest
    ) -> SubmitAnswerResponse:
        """
        Отправить ответ в режиме экзамена
        БЕЗ ПРОВЕРКИ! Только сохранение.
        
        Args:
            db: Сессия БД
            user: Пользователь
            attempt_id: UUID попытки
            request: Ответ пользователя
        
        Returns:
            Подтверждение БЕЗ is_correct
        """
        # Получаем попытку
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
        
        # Проверяем что время не истекло
        if attempt.time_limit_minutes:
            elapsed = (datetime.utcnow() - attempt.started_at).total_seconds()
            if elapsed > (attempt.time_limit_minutes * 60):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Время экзамена истекло"
                )
        
        # Обновляем ответ в Redis
        await redis_service.update_exam_answer(
            attempt_id,
            request.question_id,
            request.selected_keys
        )
        
        # Возвращаем подтверждение БЕЗ проверки
        return SubmitAnswerResponse(
            question_id=request.question_id,
            is_correct=None,  # НЕ показываем правильность!
            correct_keys=None,  # НЕ показываем правильные ответы!
            explanation=None  # НЕ показываем объяснение!
        )
    
    @staticmethod
    async def submit_exam(
        db: AsyncSession,
        user: User,
        attempt_id: str
    ) -> ExamResultResponse:
        """
        Завершить экзамен и проверить ответы
        
        Returns:
            Результаты экзамена
        """
        # Получаем попытку
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
        
        # Получаем сессию из Redis
        session = await redis_service.get_exam_session(attempt_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сессия экзамена не найдена"
            )
        
        # Проверяем все ответы
        answers_dict = session.get("answers", {})
        correct_count = 0
        
        for question_id_str, selected_keys in answers_dict.items():
            question_uuid = uuid.UUID(question_id_str)
            question = await question_service.get_question_by_id(
                db, question_uuid, safe=False
            )
            
            is_correct, _ = question_service.check_answer(question, selected_keys)
            
            # Сохраняем ответ в БД
            answer = ExamAnswer(
                attempt_id=attempt.id,
                question_id=question_uuid,
                selected_keys=selected_keys,
                is_correct=is_correct,
                answered_at=datetime.utcnow()
            )
            db.add(answer)
            
            if is_correct:
                correct_count += 1
        
        # Обновляем попытку
        attempt.completed_at = datetime.utcnow()
        attempt.status = ExamStatus.COMPLETED
        attempt.answered_questions = len(answers_dict)
        attempt.correct_answers = correct_count
        attempt.score_percentage = (correct_count / attempt.total_questions * 100) if attempt.total_questions > 0 else 0
        
        # Прокторинг
        proctoring = session.get("proctoring", {})
        attempt.proctoring_copy_paste_count = proctoring.get("copy_paste", 0)
        attempt.proctoring_tab_switches_count = proctoring.get("tab_switches", 0)
        attempt.proctoring_console_opens_count = proctoring.get("console_opens", 0)
        
        # Проверяем на подозрительную активность
        total_suspicious = (
            attempt.proctoring_copy_paste_count +
            attempt.proctoring_tab_switches_count +
            attempt.proctoring_console_opens_count
        )
        attempt.proctoring_suspicious = total_suspicious >= settings.PROCTORING_SUSPICIOUS_THRESHOLD
        
        await db.commit()
        await db.refresh(attempt)
        
        # Удаляем сессию из Redis
        await redis_service.delete_exam_session(attempt_id)
        
        # Возвращаем результаты
        return ExamResultResponse(
            attempt_id=str(attempt.id),
            mode=attempt.mode,
            status=attempt.status,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            total_questions=attempt.total_questions,
            answered_questions=attempt.answered_questions,
            correct_answers=attempt.correct_answers,
            score_percentage=attempt.score_percentage,
            passed=attempt.score_percentage >= 70,  # Порог прохождения 70%
            proctoring_copy_paste_count=attempt.proctoring_copy_paste_count,
            proctoring_tab_switches_count=attempt.proctoring_tab_switches_count,
            proctoring_console_opens_count=attempt.proctoring_console_opens_count,
            proctoring_suspicious=attempt.proctoring_suspicious
        )


# Создаем глобальный экземпляр
exam_service = ExamService()
