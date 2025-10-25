"""
API для админ панели
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.exam import ExamAttempt, ExamStatus
from app.core.deps import get_current_admin
from app.services.user_service import user_service
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.schemas.exam import ExamResultResponse
from app.schemas.common import SuccessResponse


router = APIRouter(prefix="/admin", tags=["Админ панель"])


# ===================================
# Управление пользователями
# ===================================

@router.post(
    "/users",
    response_model=UserResponse,
    summary="Создать пользователя",
    description="Создать нового пользователя (только админ)"
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> UserResponse:
    """
    Создать пользователя
    
    - **username**: Логин (уникальный)
    - **password**: Пароль
    - **full_name**: ФИО
    - **role**: Роль (student/admin/moderator)
    - **major_code**: Специальность (для студентов)
    """
    user = await user_service.create_user(db, user_data)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        major_code=user.major_code,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="Список пользователей",
    description="Получить список всех пользователей с фильтрами"
)
async def get_users(
    role: UserRole | None = Query(None, description="Фильтр по роли"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> UserListResponse:
    """
    Получить список пользователей
    
    - **role**: Фильтр по роли (student/admin/moderator)
    - **offset**: Смещение для пагинации
    - **limit**: Количество пользователей
    """
    users, total = await user_service.get_users_list(db, role, offset, limit)
    
    return UserListResponse(
        users=[
            UserResponse(
                id=u.id,
                username=u.username,
                full_name=u.full_name,
                role=u.role,
                major_code=u.major_code,
                is_active=u.is_active,
                created_at=u.created_at
            )
            for u in users
        ],
        total=total
    )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Получить пользователя",
    description="Получить пользователя по ID"
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> UserResponse:
    """Получить пользователя по ID"""
    user = await user_service.get_user_by_id(db, user_id)
    
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        major_code=user.major_code,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Обновить пользователя",
    description="Обновить данные пользователя"
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> UserResponse:
    """
    Обновить пользователя
    
    Можно обновить:
    - full_name
    - major_code
    - password
    - is_active (активен/заблокирован)
    """
    user = await user_service.update_user(db, user_id, user_data)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        major_code=user.major_code,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.delete(
    "/users/{user_id}",
    response_model=SuccessResponse,
    summary="Удалить пользователя",
    description="Удалить пользователя из системы"
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> SuccessResponse:
    """Удалить пользователя"""
    await user_service.delete_user(db, user_id)
    
    return SuccessResponse(
        message="Пользователь успешно удален",
        data={"user_id": user_id}
    )


# ===================================
# Просмотр попыток экзаменов
# ===================================

@router.get(
    "/attempts",
    response_model=list[ExamResultResponse],
    summary="Все попытки экзаменов",
    description="Получить все попытки экзаменов (для мониторинга)"
)
async def get_all_attempts(
    user_id: int | None = Query(None, description="Фильтр по пользователю"),
    status: ExamStatus | None = Query(None, description="Фильтр по статусу"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> list[ExamResultResponse]:
    """
    Получить все попытки экзаменов
    
    - **user_id**: Фильтр по пользователю
    - **status**: Фильтр по статусу (in_progress/completed/expired)
    """
    query = select(ExamAttempt)
    
    if user_id:
        query = query.where(ExamAttempt.user_id == user_id)
    
    if status:
        query = query.where(ExamAttempt.status == status)
    
    query = query.order_by(ExamAttempt.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    attempts = result.scalars().all()
    
    return [
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
        for attempt in attempts
    ]


# ===================================
# Статистика
# ===================================

@router.get(
    "/stats/overview",
    summary="Общая статистика",
    description="Общая статистика платформы"
)
async def get_overview_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> dict:
    """
    Получить общую статистику
    
    Возвращает:
    - Количество пользователей по ролям
    - Количество попыток экзаменов
    - Средний балл
    """
    # Пользователи по ролям
    users_by_role = await user_service.count_users_by_role(db)
    
    # Попытки экзаменов
    attempts_result = await db.execute(
        select(func.count(ExamAttempt.id)).where(
            ExamAttempt.status == ExamStatus.COMPLETED
        )
    )
    total_attempts = attempts_result.scalar() or 0
    
    # Средний балл
    avg_score_result = await db.execute(
        select(func.avg(ExamAttempt.score_percentage)).where(
            ExamAttempt.status == ExamStatus.COMPLETED,
            ExamAttempt.score_percentage.isnot(None)
        )
    )
    avg_score = avg_score_result.scalar() or 0.0
    
    return {
        "users_by_role": users_by_role,
        "total_completed_attempts": total_attempts,
        "average_score": round(float(avg_score), 2)
    }
