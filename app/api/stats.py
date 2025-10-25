"""
API для статистики пользователя
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User
from app.models.exam import ExamAttempt, ExamMode, ExamStatus
from app.core.deps import get_current_active_student
from app.schemas.exam import UserStatisticsResponse, ExamResultResponse


router = APIRouter(prefix="/stats", tags=["Статистика"])


@router.get(
    "/my",
    response_model=UserStatisticsResponse,
    summary="Моя статистика",
    description="Получить статистику текущего пользователя"
)
async def get_my_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
) -> UserStatisticsResponse:
    """
    Получить статистику пользователя
    
    Возвращает:
    - total_practice_attempts: Попытки практики
    - total_exam_attempts: Попытки экзаменов
    - average_score: Средний балл
    - best_score: Лучший результат
    - recent_attempts: Недавние попытки
    """
    # Подсчет попыток практики
    practice_count_result = await db.execute(
        select(func.count(ExamAttempt.id)).where(
            ExamAttempt.user_id == current_user.id,
            ExamAttempt.mode == ExamMode.PRACTICE,
            ExamAttempt.status == ExamStatus.COMPLETED
        )
    )
    total_practice = practice_count_result.scalar() or 0
    
    # Подсчет попыток экзаменов
    exam_count_result = await db.execute(
        select(func.count(ExamAttempt.id)).where(
            ExamAttempt.user_id == current_user.id,
            ExamAttempt.mode == ExamMode.EXAM,
            ExamAttempt.status == ExamStatus.COMPLETED
        )
    )
    total_exams = exam_count_result.scalar() or 0
    
    # Средний балл и лучший балл
    exam_attempts_result = await db.execute(
        select(ExamAttempt).where(
            ExamAttempt.user_id == current_user.id,
            ExamAttempt.mode == ExamMode.EXAM,
            ExamAttempt.status == ExamStatus.COMPLETED,
            ExamAttempt.score_percentage.isnot(None)
        )
    )
    exam_attempts = exam_attempts_result.scalars().all()
    
    average_score = 0.0
    best_score = 0.0
    
    if exam_attempts:
        scores = [attempt.score_percentage for attempt in exam_attempts]
        average_score = sum(scores) / len(scores)
        best_score = max(scores)
    
    # Недавние попытки (последние 5)
    recent_result = await db.execute(
        select(ExamAttempt)
        .where(
            ExamAttempt.user_id == current_user.id,
            ExamAttempt.status == ExamStatus.COMPLETED
        )
        .order_by(ExamAttempt.completed_at.desc())
        .limit(5)
    )
    recent_attempts_models = recent_result.scalars().all()
    
    recent_attempts = [
        ExamResultResponse(
            attempt_id=str(attempt.id),
            mode=attempt.mode,
            status=attempt.status,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            total_questions=attempt.total_questions,
            answered_questions=attempt.answered_questions,
            correct_answers=attempt.correct_answers,
            score_percentage=attempt.score_percentage or 0.0,
            passed=attempt.score_percentage >= 70 if attempt.score_percentage else False,
            proctoring_copy_paste_count=attempt.proctoring_copy_paste_count,
            proctoring_tab_switches_count=attempt.proctoring_tab_switches_count,
            proctoring_console_opens_count=attempt.proctoring_console_opens_count,
            proctoring_suspicious=attempt.proctoring_suspicious
        )
        for attempt in recent_attempts_models
    ]
    
    return UserStatisticsResponse(
        total_practice_attempts=total_practice,
        total_exam_attempts=total_exams,
        average_score=round(average_score, 2),
        best_score=round(best_score, 2),
        subjects_stats={},  # TODO: Добавить статистику по предметам
        recent_attempts=recent_attempts
    )
