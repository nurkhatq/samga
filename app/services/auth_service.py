"""
Сервис авторизации (JWT, login, logout)
"""
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
)
from app.core.config import settings
from app.schemas.user import UserLogin, TokenResponse


class AuthService:
    """Сервис для авторизации"""
    
    @staticmethod
    async def login(
        db: AsyncSession,
        credentials: UserLogin
    ) -> TokenResponse:
        """
        Вход в систему
        
        Args:
            db: Сессия БД
            credentials: Логин и пароль
        
        Returns:
            TokenResponse с access и refresh токенами
        
        Raises:
            HTTPException: Если неверные учетные данные
        """
        # Ищем пользователя по username
        result = await db.execute(
            select(User).where(User.username == credentials.username)
        )
        user = result.scalar_one_or_none()
        
        # Проверяем существование пользователя
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Проверяем пароль
        if not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Проверяем активность пользователя
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь заблокирован",
            )
        
        # Создаем токены
        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str
    ) -> TokenResponse:
        """
        Обновить access token используя refresh token
        
        Args:
            db: Сессия БД
            refresh_token: Refresh токен
        
        Returns:
            TokenResponse с новым access токеном
        
        Raises:
            HTTPException: Если токен недействителен
        """
        # Декодируем refresh токен
        payload = decode_token(refresh_token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный refresh токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Проверяем тип токена
        if not verify_token_type(payload, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный тип токена",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Получаем user_id
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Проверяем существование пользователя
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Создаем новые токены
        new_access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        new_refresh_token = create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    def get_password_hash_static(password: str) -> str:
        """Получить хеш пароля (вспомогательная функция)"""
        return get_password_hash(password)


# Создаем глобальный экземпляр
auth_service = AuthService()
