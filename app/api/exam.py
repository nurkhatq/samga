"""
API для экзаменов (Exam Mode)
"""
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_active_student
from app.services.exam_service import exam_service
from app.services.proctoring_service import proctoring_service
from app.services.redis_service import redis_service
from app.schemas.exam import (
    ExamStartRequest,
    ExamStartResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    ExamStatusResponse,
    ExamSubmitRequest,
    ExamResultResponse,
)
from app.schemas.proctoring import (
    ProctoringEventCreate,
    ProctoringEventBatchCreate,
    ProctoringEventBatchResponse,
)
from app.schemas.question import QuestionResponse, QuestionOptionResponse


router = APIRouter(prefix="/exam", tags=["Экзамены"])


@router.post(
    "/start",
    response_model=ExamStartResponse,
    summary="Начать пробный экзамен",
    description="Начать экзамен по выбранной специальности"
)
async def start_exam(
    request: ExamStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
) -> ExamStartResponse:
    """
    Начать пробный экзамен
    
    - **major_code**: Код специальности (M001, M002, ...)
    
    Генерирует вопросы в зависимости от типа магистратуры:
    - Профильная: 50 вопросов (90 минут)
    - Научно-педагогическая: 130 вопросов (180 минут)
    
    Возвращает:
    - attempt_id: UUID попытки экзамена
    - time_limit_minutes: Лимит времени
    - total_questions: Количество вопросов
    """
    return await exam_service.start_exam(db, current_user, request)


@router.get(
    "/{attempt_id}",
    response_model=ExamStatusResponse,
    summary="Текущее состояние экзамена",
    description="Получить информацию о текущей попытке"
)
async def get_exam_status(
    attempt_id: str = Path(..., description="UUID попытки экзамена"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
) -> ExamStatusResponse:
    """
    Получить состояние экзамена
    
    Возвращает:
    - status: Статус (in_progress, completed, expired)
    - time_remaining_seconds: Оставшееся время
    - answered_questions: Количество отвеченных вопросов
    - current_question_index: Текущий индекс
    """
    return await exam_service.get_exam_status(db, current_user, attempt_id)


@router.get(
    "/{attempt_id}/questions",
    response_model=list[QuestionResponse],
    summary="Получить вопросы экзамена",
    description="Получить все вопросы экзамена БЕЗ правильных ответов"
)
async def get_exam_questions(
    attempt_id: str = Path(..., description="UUID попытки"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
) -> list[QuestionResponse]:
    """
    Получить вопросы экзамена
    
    ВАЖНО: Вопросы БЕЗ is_correct!
    Правильные ответы показываются только после завершения экзамена.
    """
    import uuid
    from app.models.exam import ExamAttempt, ExamStatus
    from sqlalchemy import select
    
    # Проверяем попытку
    attempt_uuid = uuid.UUID(attempt_id)
    result = await db.execute(
        select(ExamAttempt).where(
            ExamAttempt.id == attempt_uuid,
            ExamAttempt.user_id == current_user.id,
            ExamAttempt.status == ExamStatus.IN_PROGRESS
        )
    )
    attempt = result.scalar_one_or_none()
    
    if not attempt:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Активная попытка экзамена не найдена"
        )
    
    # Получаем сессию из Redis
    session = await redis_service.get_exam_session(attempt_id)
    if not session:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Сессия экзамена не найдена"
        )
    
    # Получаем вопросы
    question_ids = session.get("questions", [])
    
    from app.services.question_service import question_service
    from app.models.question import Question
    
    questions = []
    for q_id in question_ids:
        question_uuid = uuid.UUID(q_id)
        question = await question_service.get_question_by_id(
            db, question_uuid, safe=True
        )
        
        # Преобразуем в безопасный формат БЕЗ is_correct
        questions.append(
            QuestionResponse(
                id=str(question.id),
                subject_code=question.subject_code,
                question_text=question.question_text,
                options=[
                    QuestionOptionResponse(key=opt["key"], text=opt["text"])
                    for opt in question.options
                ],
                difficulty=question.difficulty,
                question_type=question.question_type,
                points=question.points,
                time_seconds=question.time_seconds,
                explanation=None,  # НЕ показываем
                tags=question.tags
            )
        )
    
    return questions


@router.post(
    "/{attempt_id}/answer",
    response_model=SubmitAnswerResponse,
    summary="Отправить ответ (БЕЗ проверки)",
    description="Сохранить ответ без проверки правильности"
)
async def submit_exam_answer(
    attempt_id: str = Path(..., description="UUID попытки"),
    request: SubmitAnswerRequest = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
) -> SubmitAnswerResponse:
    """
    Отправить ответ в режиме экзамена
    
    - **question_id**: UUID вопроса
    - **selected_keys**: Выбранные варианты
    
    ВАЖНО: Ответ сохраняется БЕЗ проверки!
    Правильность не показывается до завершения экзамена.
    
    Возвращает:
    - is_correct: null (не показываем)
    - correct_keys: null (не показываем)
    """
    return await exam_service.submit_answer(
        db, current_user, attempt_id, request
    )


@router.post(
    "/{attempt_id}/submit",
    response_model=ExamResultResponse,
    summary="Завершить экзамен",
    description="Завершить экзамен и получить результаты"
)
async def submit_exam(
    attempt_id: str = Path(..., description="UUID попытки"),
    request: ExamSubmitRequest = ExamSubmitRequest(confirmed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
) -> ExamResultResponse:
    """
    Завершить экзамен
    
    После завершения:
    - Проверяются все ответы
    - Подсчитываются баллы
    - Формируется статистика прокторинга
    
    Возвращает:
    - score_percentage: Процент правильных ответов
    - passed: Сдал ли экзамен (>= 70%)
    - proctoring_*: Статистика прокторинга
    """
    return await exam_service.submit_exam(db, current_user, attempt_id)


@router.post(
    "/{attempt_id}/proctoring",
    response_model=ProctoringEventBatchResponse,
    summary="Отправить события прокторинга",
    description="Отправить события прокторинга (copy, paste, tab_switch, ...)"
)
async def log_proctoring_events(
    attempt_id: str = Path(..., description="UUID попытки"),
    batch: ProctoringEventBatchCreate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
) -> ProctoringEventBatchResponse:
    """
    Отправить события прокторинга
    
    Типы событий:
    - copy, paste, cut - Копирование/вставка
    - tab_switch, window_blur - Переключение окна
    - console_open - Открытие консоли разработчика
    - context_menu, right_click - Контекстное меню
    
    Можно отправить до 100 событий за раз
    """
    created_count = await proctoring_service.log_events_batch(
        db, current_user, attempt_id, batch
    )
    
    return ProctoringEventBatchResponse(created_count=created_count)
