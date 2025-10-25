#!/usr/bin/env python3
"""
Скрипт инициализации базы данных
Создает все таблицы и загружает начальные данные
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.session import async_engine
from app.db.base import Base
from app.models import *  # Импортируем все модели


async def init_db():
    """Инициализировать базу данных"""
    
    print("=" * 60)
    print("🗄️  ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    try:
        # Проверяем подключение
        print("\n📡 Проверка подключения к базе данных...")
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Подключение успешно")
        
        # Создаем все таблицы
        print("\n📦 Создание таблиц...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы")
        
        # Список созданных таблиц
        print("\n📋 Созданные таблицы:")
        tables = [
            "users",
            "majors",
            "subjects",
            "questions",
            "exam_attempts",
            "exam_answers",
            "proctoring_events"
        ]
        
        for table in tables:
            print(f"   ✓ {table}")
        
        print("\n" + "=" * 60)
        print("✅ База данных успешно инициализирована!")
        print("=" * 60)
        
        print("\n📝 Следующие шаги:")
        print("   1. Импортируйте данные: python scripts/import_data.py")
        print("   2. Создайте админа: python scripts/create_admin.py")
        print("   3. Запустите сервер: uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"\n❌ Ошибка при инициализации базы данных: {e}")
        raise


async def drop_all_tables():
    """Удалить все таблицы (ОСТОРОЖНО!)"""
    
    print("\n" + "⚠️  ВНИМАНИЕ! ⚠️".center(60, "="))
    print("Вы собираетесь удалить ВСЕ таблицы из базы данных!")
    print("Это действие НЕОБРАТИМО!")
    print("=" * 60)
    
    confirm = input("\nВведите 'DELETE ALL' для подтверждения: ").strip()
    
    if confirm != "DELETE ALL":
        print("❌ Отменено")
        return
    
    try:
        print("\n🗑️  Удаление всех таблиц...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("✅ Все таблицы удалены")
    
    except Exception as e:
        print(f"\n❌ Ошибка при удалении таблиц: {e}")
        raise


async def reset_db():
    """Сбросить базу данных (удалить и создать заново)"""
    await drop_all_tables()
    await init_db()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Управление базой данных")
    parser.add_argument(
        "action",
        choices=["init", "drop", "reset"],
        help="Действие: init (создать), drop (удалить), reset (пересоздать)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "🎓 Connect AITU - Управление БД".center(60))
    
    if args.action == "init":
        asyncio.run(init_db())
    elif args.action == "drop":
        asyncio.run(drop_all_tables())
    elif args.action == "reset":
        asyncio.run(reset_db())
