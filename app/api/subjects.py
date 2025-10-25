"""
API для предметов (Subjects)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.subject import Subject, SubjectType
from app.models.user import User
from app.core.deps import get_current_user
from app.schemas.subject import SubjectResponse, SubjectListResponse
from app.services.question_service import question_service


router = APIRouter(prefix="/subjects", tags=["Предметы"])


@router.get(
    "",
    response_model=SubjectListResponse,
    summary="Список предметов",
    description="Получить список всех предметов (ТГО, АНГЛ, профильные)"
)
async def get_subjects(
    subject_type: SubjectType | None = Query(None, description="Фильтр по типу"),
    major_code: str | None = Query(None, description="Фильтр по специальности"),
    active_only: bool = Query(True, description="Только активные"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SubjectListResponse:
    """
    Получить список предметов
    
    - **subject_type**: Тип предмета (common/profile)
    - **major_code**: Код специальности (для профильных)
    - **active_only**: Только активные предметы
    """
    # Запрос с фильтрами
    query = select(Subject)
    count_query = select(func.count(Subject.code))
    
    if active_only:
        query = query.where(Subject.is_active == True)
        count_query = count_query.where(Subject.is_active == True)
    
    if subject_type:
        query = query.where(Subject.subject_type == subject_type)
        count_query = count_query.where(Subject.subject_type == subject_type)
    
    if major_code:
        query = query.where(Subject.major_code == major_code)
        count_query = count_query.where(Subject.major_code == major_code)
    
    # Подсчет
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # Получение
    query = query.order_by(Subject.subject_type, Subject.code)
    result = await db.execute(query)
    subjects = result.scalars().all()
    
    # Добавляем количество вопросов
    subjects_with_counts = []
    for subject in subjects:
        questions_count = await question_service.count_questions_by_subject(
            db, subject.code
        )
        
        subjects_with_counts.append(
            SubjectResponse(
                code=subject.code,
                title_kk=subject.title_kk,
                title_ru=subject.title_ru,
                subject_type=subject.subject_type,
                major_code=subject.major_code,
                is_active=subject.is_active,
                questions_count=questions_count,
                created_at=subject.created_at,
                updated_at=subject.updated_at
            )
        )
    
    return SubjectListResponse(
        subjects=subjects_with_counts,
        total=total
    )


@router.get(
    "/{subject_code}",
    response_model=SubjectResponse,
    summary="Получить предмет по коду",
    description="Подробная информация о предмете"
)
async def get_subject(
    subject_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SubjectResponse:
    """
    Получить предмет по коду
    
    - **subject_code**: Код предмета (TGO, ENG, M001_PEDAGOGY, ...)
    """
    result = await db.execute(
        select(Subject).where(Subject.code == subject_code)
    )
    subject = result.scalar_one_or_none()
    
    if not subject:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Предмет не найден"
        )
    
    # Подсчитываем вопросы
    questions_count = await question_service.count_questions_by_subject(
        db, subject.code
    )
    
    return SubjectResponse(
        code=subject.code,
        title_kk=subject.title_kk,
        title_ru=subject.title_ru,
        subject_type=subject.subject_type,
        major_code=subject.major_code,
        is_active=subject.is_active,
        questions_count=questions_count,
        created_at=subject.created_at,
        updated_at=subject.updated_at
    )
