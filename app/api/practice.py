"""
API для свободного режима (Practice Mode)
"""
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_active_student
from app.services.practice_service import practice_service
from app.schemas.exam import (
    PracticeStartRequest,
    ExamStartResponse,
    GetQuestionsResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)


router = APIRouter(prefix="/practice", tags=["Свободный режим"])


@router.post(
    "/start",
    response_model=ExamStartResponse,
    summary="Начать свободный режим",
    description="Начать практику по выбранному предмету"
)
async def start_practice(
    request: PracticeStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
) -> ExamStartResponse:
    """
    Начать свободный режим
    
    - **subject_code**: Код предмета (TGO, ENG, M001_PEDAGOGY, ...)
    
    Возвращает:
    - attempt_id: ID сессии
    - total_questions: Общее количество вопросов в предмете
    """
    return await practice_service.start_practice(db, current_user, request)


@router.get(
    "/{subject_code}/questions",
    response_model=GetQuestionsResponse,
    summary="Получить вопросы (пагинация)",
    description="Получить вопросы БЕЗ правильных ответов (пагинация по 20)"
)
async def get_practice_questions(
    subject_code: str = Path(..., description="Код предмета"),
    offset: int = Query(0, ge=0, description="Смещение"),
    limit: int = Query(20, ge=1, le=100, description="Количество вопросов"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
) -> GetQuestionsResponse:
    """
    Получить вопросы с пагинацией
    
    - **subject_code**: Код предмета
    - **offset**: Смещение (0, 20, 40, ...)
    - **limit**: Количество вопросов (по умолчанию 20)
    
    ВАЖНО: Вопросы возвращаются БЕЗ is_correct!
    Правильные ответы показываются только после submit_answer
    """
    return await practice_service.get_questions(
        db, current_user, subject_code, offset, limit
    )


@router.post(
    "/{subject_code}/submit-answer",
    response_model=SubmitAnswerResponse,
    summary="Отправить ответ (с проверкой)",
    description="Отправить ответ и получить мгновенную проверку"
)
async def submit_practice_answer(
    subject_code: str = Path(..., description="Код предмета"),
    request: SubmitAnswerRequest = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
) -> SubmitAnswerResponse:
    """
    Отправить ответ в свободном режиме
    
    - **question_id**: UUID вопроса
    - **selected_keys**: Выбранные варианты (["A"], ["B", "C"])
    
    Возвращает:
    - **is_correct**: Правильно ли
    - **correct_keys**: Правильные ответы
    - **explanation**: Объяснение (если есть)
    
    ТОЛЬКО для Practice Mode! В Exam Mode проверка не показывается.
    """
    return await practice_service.submit_answer(
        db, current_user, subject_code, request
    )


@router.get(
    "/{subject_code}/stats",
    summary="Статистика по практике",
    description="Текущая статистика по предмету"
)
async def get_practice_stats(
    subject_code: str = Path(..., description="Код предмета"),
    current_user: User = Depends(get_current_active_student)
) -> dict:
    """
    Получить статистику по практике
    
    Возвращает:
    - answered_questions: Количество отвеченных
    - correct_count: Количество правильных
    - accuracy_percentage: Процент точности
    """
    return await practice_service.get_practice_stats(current_user, subject_code)


@router.post(
    "/{subject_code}/finish",
    summary="Завершить практику",
    description="Завершить практику и получить итоговую статистику"
)
async def finish_practice(
    subject_code: str = Path(..., description="Код предмета"),
    current_user: User = Depends(get_current_active_student)
) -> dict:
    """
    Завершить практику
    
    Возвращает итоговую статистику
    """
    return await practice_service.finish_practice(current_user, subject_code)
