"""
API для специальностей (Majors)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.major import Major
from app.models.user import User
from app.core.deps import get_current_user
from app.schemas.major import MajorResponse, MajorListResponse


router = APIRouter(prefix="/majors", tags=["Специальности"])


@router.get(
    "",
    response_model=MajorListResponse,
    summary="Список всех специальностей",
    description="Получить список всех доступных специальностей для магистратуры"
)
async def get_majors(
    active_only: bool = Query(True, description="Только активные специальности"),
    offset: int = Query(0, ge=0, description="Смещение"),
    limit: int = Query(100, ge=1, le=500, description="Количество"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MajorListResponse:
    """
    Получить список специальностей
    
    - **active_only**: Фильтр только по активным
    - **offset**: Смещение для пагинации
    - **limit**: Количество специальностей
    
    Возвращает список всех 153 специальностей
    """
    # Запрос с фильтром
    query = select(Major)
    count_query = select(func.count(Major.code))
    
    if active_only:
        query = query.where(Major.is_active == True)
        count_query = count_query.where(Major.is_active == True)
    
    # Подсчет
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # Получение с пагинацией
    query = query.offset(offset).limit(limit).order_by(Major.code)
    result = await db.execute(query)
    majors = result.scalars().all()
    
    return MajorListResponse(
        majors=[
            MajorResponse(
                code=m.code,
                title_kk=m.title_kk,
                title_ru=m.title_ru,
                magistracy_type=m.magistracy_type,
                categories=m.categories,
                is_active=m.is_active,
                created_at=m.created_at,
                updated_at=m.updated_at
            )
            for m in majors
        ],
        total=total
    )


@router.get(
    "/{major_code}",
    response_model=MajorResponse,
    summary="Получить специальность по коду",
    description="Получить подробную информацию о специальности"
)
async def get_major(
    major_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MajorResponse:
    """
    Получить специальность по коду
    
    - **major_code**: Код специальности (M001, M002, ...)
    """
    result = await db.execute(
        select(Major).where(Major.code == major_code)
    )
    major = result.scalar_one_or_none()
    
    if not major:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Специальность не найдена"
        )
    
    return MajorResponse(
        code=major.code,
        title_kk=major.title_kk,
        title_ru=major.title_ru,
        magistracy_type=major.magistracy_type,
        categories=major.categories,
        is_active=major.is_active,
        created_at=major.created_at,
        updated_at=major.updated_at
    )
