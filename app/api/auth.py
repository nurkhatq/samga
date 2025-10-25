"""
API для авторизации
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.auth_service import auth_service
from app.schemas.user import UserLogin, TokenResponse, RefreshTokenRequest
from app.schemas.common import SuccessResponse


router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему",
    description="Аутентификация пользователя и получение JWT токенов"
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Вход в систему
    
    - **username**: Логин пользователя
    - **password**: Пароль
    
    Возвращает access и refresh токены
    """
    return await auth_service.login(db, credentials)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Обновить access token",
    description="Получить новый access token используя refresh token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Обновить access token
    
    - **refresh_token**: Refresh токен
    
    Возвращает новые access и refresh токены
    """
    return await auth_service.refresh_access_token(db, request.refresh_token)


@router.post(
    "/logout",
    response_model=SuccessResponse,
    summary="Выход из системы",
    description="Завершить сессию (на клиенте нужно удалить токены)"
)
async def logout() -> SuccessResponse:
    """
    Выход из системы
    
    На стороне клиента необходимо удалить сохраненные токены.
    В будущем здесь можно добавить blacklist для токенов.
    """
    return SuccessResponse(
        message="Успешный выход из системы",
        data=None
    )
