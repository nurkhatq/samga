#!/usr/bin/env python3
"""
Создание администратора (автоматически)
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.user import User
from app.core.security import get_password_hash


async def create_admin():
    """Создать администратора"""
    
    # Читаем из переменных окружения или используем дефолтные
    username = os.getenv("FIRST_ADMIN_USERNAME", "admin")
    password = os.getenv("FIRST_ADMIN_PASSWORD", "admin123")
    full_name = os.getenv("FIRST_ADMIN_FULLNAME", "Администратор")
    
    print("=" * 60)
    print("🔐 СОЗДАНИЕ АДМИНИСТРАТОРА")
    print("=" * 60)
    print(f"Логин: {username}")
    print(f"ФИО: {full_name}")
    print(f"Роль: admin")
    print("=" * 60)
    
    async with async_session_maker() as db:
        try:
            # Проверяем существование
            result = await db.execute(
                select(User).where(User.username == username)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"\n⚠️  Пользователь '{username}' уже существует!")
                # Обновляем пароль
                existing.password_hash = get_password_hash(password)
                existing.role = "admin"
                existing.full_name = full_name
                existing.is_active = True
                await db.commit()
                print(f"✅ Администратор обновлен!")
                return
            
            # Создаем администратора
            admin = User(
                username=username,
                password_hash=get_password_hash(password),
                full_name=full_name,
                role="admin",  # Используем строку напрямую
                is_active=True
            )
            
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            
            print(f"\n✅ Администратор создан!")
            print(f"   ID: {admin.id}")
            print(f"   Логин: {admin.username}")
            print(f"   ФИО: {admin.full_name}")
            print("\n🎉 Готово!\n")
        
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_admin())