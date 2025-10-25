#!/usr/bin/env python3
"""
Скрипт генерации тестовых данных
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import async_session_maker
from app.models.user import User, UserRole
from app.models.major import Major, MagistracyType
from app.models.subject import Subject, SubjectType
from app.models.question import Question, QuestionDifficulty, QuestionType
from app.core.security import get_password_hash


async def generate_test_users(count: int = 10):
    """Создать тестовых пользователей"""
    
    print(f"\n👥 Создание {count} тестовых пользователей...")
    
    async with async_session_maker() as db:
        created = 0
        
        for i in range(1, count + 1):
            username = f"student{i}"
            
            # Проверяем существование
            from sqlalchemy import select
            result = await db.execute(
                select(User).where(User.username == username)
            )
            if result.scalar_one_or_none():
                continue
            
            user = User(
                username=username,
                password_hash=get_password_hash("password123"),
                full_name=f"Студент Тестовый {i}",
                role=UserRole.STUDENT,
                major_code=f"M{str(i % 153 + 1).zfill(3)}",
                is_active=True
            )
            db.add(user)
            created += 1
        
        await db.commit()
        print(f"✅ Создано пользователей: {created}")


async def generate_test_majors(count: int = 10):
    """Создать тестовые специальности"""
    
    print(f"\n🎓 Создание {count} тестовых специальностей...")
    
    async with async_session_maker() as db:
        created = 0
        
        for i in range(1, count + 1):
            code = f"MTEST{str(i).zfill(3)}"
            
            # Проверяем существование
            from sqlalchemy import select
            result = await db.execute(
                select(Major).where(Major.code == code)
            )
            if result.scalar_one_or_none():
                continue
            
            major = Major(
                code=code,
                title_kk=f"Тестовая специальность {i}",
                title_ru=f"Тестовая специальность {i}",
                magistracy_type=random.choice([
                    MagistracyType.PROFILE,
                    MagistracyType.SCIENTIFIC_PEDAGOGICAL
                ]),
                categories=["test"],
                is_active=True
            )
            db.add(major)
            created += 1
        
        await db.commit()
        print(f"✅ Создано специальностей: {created}")


async def generate_test_subjects(major_code: str = "M001", count: int = 4):
    """Создать тестовые предметы"""
    
    print(f"\n📚 Создание {count} тестовых предметов для {major_code}...")
    
    async with async_session_maker() as db:
        created = 0
        
        subjects = [
            ("TGO", "Тестирование ғылым тарихы", SubjectType.COMMON),
            ("ENG", "English Test", SubjectType.COMMON),
            (f"{major_code}_TEST1", "Тестовый предмет 1", SubjectType.PROFILE),
            (f"{major_code}_TEST2", "Тестовый предмет 2", SubjectType.PROFILE),
        ]
        
        for code, title, subject_type in subjects[:count]:
            # Проверяем существование
            from sqlalchemy import select
            result = await db.execute(
                select(Subject).where(Subject.code == code)
            )
            if result.scalar_one_or_none():
                continue
            
            subject = Subject(
                code=code,
                title_kk=title,
                title_ru=title,
                subject_type=subject_type,
                major_code=major_code if subject_type == SubjectType.PROFILE else None,
                is_active=True
            )
            db.add(subject)
            created += 1
        
        await db.commit()
        print(f"✅ Создано предметов: {created}")


async def generate_test_questions(subject_code: str = "TGO", count: int = 50):
    """Создать тестовые вопросы"""
    
    print(f"\n❓ Создание {count} тестовых вопросов для {subject_code}...")
    
    async with async_session_maker() as db:
        created = 0
        
        for i in range(1, count + 1):
            # Случайный тип вопроса
            question_type = random.choice([
                QuestionType.SINGLE,
                QuestionType.MULTIPLE
            ])
            
            # Генерируем варианты
            options = [
                {
                    "key": "A",
                    "text": f"Вариант А для вопроса {i}",
                    "is_correct": question_type == QuestionType.SINGLE
                },
                {
                    "key": "B",
                    "text": f"Вариант Б для вопроса {i}",
                    "is_correct": question_type == QuestionType.MULTIPLE
                },
                {
                    "key": "C",
                    "text": f"Вариант В для вопроса {i}",
                    "is_correct": question_type == QuestionType.MULTIPLE
                },
                {
                    "key": "D",
                    "text": f"Вариант Г для вопроса {i}",
                    "is_correct": False
                }
            ]
            
            question = Question(
                subject_code=subject_code,
                question_text=f"Тестовый вопрос №{i} для предмета {subject_code}?",
                options=options,
                difficulty=random.choice([
                    QuestionDifficulty.EASY,
                    QuestionDifficulty.MEDIUM,
                    QuestionDifficulty.HARD
                ]),
                question_type=question_type,
                points=1,
                time_seconds=60,
                explanation=f"Объяснение для вопроса {i}",
                tags=["test", f"question{i}"]
            )
            db.add(question)
            created += 1
        
        await db.commit()
        print(f"✅ Создано вопросов: {created}")


async def generate_all_test_data():
    """Создать все тестовые данные"""
    
    print("=" * 60)
    print("🧪 ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ")
    print("=" * 60)
    
    try:
        await generate_test_users(10)
        await generate_test_majors(5)
        await generate_test_subjects("M001", 4)
        await generate_test_questions("TGO", 50)
        await generate_test_questions("ENG", 50)
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТОВЫЕ ДАННЫЕ СОЗДАНЫ!")
        print("=" * 60)
        
        print("\n📋 Созданные данные:")
        print("   • 10 тестовых пользователей (student1-10, password: password123)")
        print("   • 5 тестовых специальностей (MTEST001-005)")
        print("   • 4 тестовых предмета")
        print("   • 100 тестовых вопросов")
    
    except Exception as e:
        print(f"\n❌ Ошибка при генерации тестовых данных: {e}")
        raise


if __name__ == "__main__":
    print("\n" + "🎓 Connect AITU - Генерация тестовых данных".center(60))
    asyncio.run(generate_all_test_data())
