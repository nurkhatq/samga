"""
Сервис для управления пользователями (CRUD)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: int
    ) -> User | None:
        """Получить пользователя по ID"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(
        db: AsyncSession,
        username: str
    ) -> User | None:
        """Получить пользователя по username"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate
    ) -> User:
        """
        Создать пользователя
        
        Args:
            db: Сессия БД
            user_data: Данные нового пользователя
        
        Returns:
            Созданный пользователь
        
        Raises:
            HTTPException: Если username уже занят
        """
        # Проверяем уникальность username
        existing_user = await UserService.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким логином уже существует"
            )
        
        # Хешируем пароль
        password_hash = get_password_hash(user_data.password)
        
        # Создаем пользователя
        user = User(
            username=user_data.username,
            password_hash=password_hash,
            full_name=user_data.full_name,
            role=user_data.role,
            major_code=user_data.major_code,
            is_active=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate
    ) -> User:
        """
        Обновить пользователя
        
        Args:
            db: Сессия БД
            user_id: ID пользователя
            user_data: Данные для обновления
        
        Returns:
            Обновленный пользователь
        
        Raises:
            HTTPException: Если пользователь не найден
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Обновляем поля
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.major_code is not None:
            user.major_code = user_data.major_code
        
        if user_data.password is not None:
            user.password_hash = get_password_hash(user_data.password)
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def delete_user(
        db: AsyncSession,
        user_id: int
    ) -> bool:
        """
        Удалить пользователя
        
        Args:
            db: Сессия БД
            user_id: ID пользователя
        
        Returns:
            True если успешно
        
        Raises:
            HTTPException: Если пользователь не найден
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        await db.delete(user)
        await db.commit()
        
        return True
    
    @staticmethod
    async def get_users_list(
        db: AsyncSession,
        role: UserRole | None = None,
        offset: int = 0,
        limit: int = 100
    ) -> tuple[list[User], int]:
        """
        Получить список пользователей
        
        Args:
            db: Сессия БД
            role: Фильтр по роли (опционально)
            offset: Смещение
            limit: Лимит
        
        Returns:
            (список пользователей, общее количество)
        """
        # Базовый запрос
        query = select(User)
        count_query = select(func.count(User.id))
        
        # Фильтр по роли
        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        
        # Подсчет
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Получение с пагинацией
        query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
        result = await db.execute(query)
        users = result.scalars().all()
        
        return list(users), total
    
    @staticmethod
    async def count_users_by_role(
        db: AsyncSession
    ) -> dict[str, int]:
        """
        Подсчитать пользователей по ролям
        
        Returns:
            {"student": 100, "admin": 5, "moderator": 2}
        """
        counts = {}
        
        for role in UserRole:
            result = await db.execute(
                select(func.count(User.id)).where(User.role == role)
            )
            counts[role.value] = result.scalar() or 0
        
        return counts


# Создаем глобальный экземпляр
user_service = UserService()
