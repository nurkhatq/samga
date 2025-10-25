#!/usr/bin/env python3
"""
Скрипт для создания первого администратора
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def create_admin():
    """Создать администратора"""
    
    print("=" * 60)
    print("🔐 СОЗДАНИЕ ПЕРВОГО АДМИНИСТРАТОРА")
    print("=" * 60)
    
    # Запрашиваем данные
    username = input("\nВведите логин (admin): ").strip() or "admin"
    password = input("Введите пароль (admin123): ").strip() or "admin123"
    full_name = input("Введите ФИО (Admin User): ").strip() or "Admin User"
    
    print("\n" + "=" * 60)
    print(f"Логин: {username}")
    print(f"ФИО: {full_name}")
    print(f"Роль: admin")
    print("=" * 60)
    
    confirm = input("\nСоздать администратора? (yes/no): ").strip().lower()
    
    if confirm not in ["yes", "y", "да"]:
        print("❌ Отменено")
        return
    
    async with async_session_maker() as db:
        try:
            # Проверяем существование
            result = await db.execute(
                select(User).where(User.username == username)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"\n⚠️  Пользователь '{username}' уже существует!")
                
                # Предлагаем обновить пароль
                update = input("Обновить пароль? (yes/no): ").strip().lower()
                if update in ["yes", "y", "да"]:
                    existing.password_hash = get_password_hash(password)
                    existing.role = "admin"  # Используем строку напрямую
                    existing.full_name = full_name
                    existing.is_active = True
                    await db.commit()
                    print(f"✅ Пароль пользователя '{username}' обновлен!")
                else:
                    print("❌ Отменено")
                return
            
            # Создаем администратора - ВАЖНО: используем строку напрямую
            admin = User(
                username=username,
                password_hash=get_password_hash(password),
                full_name=full_name,
                role="admin",  # Используем строку напрямую, а не UserRole.ADMIN
                is_active=True
            )
            
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            
            print(f"\n✅ Администратор успешно создан!")
            print(f"   ID: {admin.id}")
            print(f"   Логин: {admin.username}")
            print(f"   ФИО: {admin.full_name}")
            print(f"   Роль: {admin.role}")
            print("\n🎉 Теперь вы можете войти в систему!")
        
        except Exception as e:
            print(f"\n❌ Ошибка при создании администратора: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise


if __name__ == "__main__":
    print("\n" + "🎓 Connect AITU - Создание администратора".center(60))
    asyncio.run(create_admin())