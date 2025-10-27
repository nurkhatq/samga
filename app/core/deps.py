"""
FastAPI зависимости для аутентификации и авторизации
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import decode_token, verify_token_type
from app.models.user import User, UserRole
from sqlalchemy import select


# ===================================
# Security
# ===================================
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Получить текущего аутентифицированного пользователя
    
    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    token = credentials.credentials
    
    # Декодируем токен
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем тип токена
    if not verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный тип токена",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Получаем user_id из токена
    user_id: int = int(payload.get("sub"))
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ищем пользователя в БД
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_student(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Проверить что текущий пользователь - студент
    
    Raises:
        HTTPException: Если пользователь не студент
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для студентов"
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Проверить что текущий пользователь - администратор
    
    Raises:
        HTTPException: Если пользователь не администратор
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для администраторов"
        )
    return current_user


async def get_current_admin_or_moderator(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Проверить что текущий пользователь - администратор или модератор
    
    Raises:
        HTTPException: Если недостаточно прав
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return current_user
