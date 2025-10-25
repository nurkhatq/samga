#!/usr/bin/env python3
"""
Скрипт инициализации базовых данных
- Специальности (153 штуки)
- Предметы (ТГО, АНГЛ, профильные по каждой специальности)

Usage:
    python scripts/init_data.py
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.db.session import async_session_maker
from app.models.major import Major, MagistracyType
from app.models.subject import Subject, SubjectType


# Пример специальностей (в реальности должно быть 153)
MAJORS_DATA = [
    {
        "code": "M001",
        "title_kk": "Педагогика және психология",
        "title_ru": "Педагогика и психология",
        "magistracy_type": "profile",  # Используем строку напрямую
        "categories": ["Білім беру"]
    },
    {
        "code": "M002",
        "title_kk": "Бастауыш оқыту педагогикасы мен әдістемесі",
        "title_ru": "Педагогика и методика начального обучения",
        "magistracy_type": "profile",  # Используем строку напрямую
        "categories": ["Білім беру"]
    },
    {
        "code": "M003",
        "title_kk": "Математика",
        "title_ru": "Математика",
        "magistracy_type": "scientific_pedagogical",  # Используем строку напрямую
        "categories": ["Жаратылыстану"]
    },
    {
        "code": "M004",
        "title_kk": "Физика",
        "title_ru": "Физика",
        "magistracy_type": "scientific_pedagogical",  # Используем строку напрямую
        "categories": ["Жаратылыстану"]
    },
    {
        "code": "M005",
        "title_kk": "Ақпараттық жүйелер",
        "title_ru": "Информационные системы",
        "magistracy_type": "profile",  # Используем строку напрямую
        "categories": ["Техника"]
    },
    # TODO: Добавить остальные 148 специальностей из реального списка
]


# Профильные предметы для каждой специальности
PROFILE_SUBJECTS = {
    "M001": [
        {"code": "M001_PEDAGOGY", "title_kk": "Педагогика", "title_ru": "Педагогика"},
        {"code": "M001_PSYCHOLOGY", "title_kk": "Психология", "title_ru": "Психология"},
    ],
    "M002": [
        {"code": "M002_METHODS", "title_kk": "Әдістеме", "title_ru": "Методика"},
        {"code": "M002_DIDACTICS", "title_kk": "Дидактика", "title_ru": "Дидактика"},
    ],
    "M003": [
        {"code": "M003_ALGEBRA", "title_kk": "Алгебра", "title_ru": "Алгебра"},
        {"code": "M003_GEOMETRY", "title_kk": "Геометрия", "title_ru": "Геометрия"},
    ],
    "M004": [
        {"code": "M004_MECHANICS", "title_kk": "Механика", "title_ru": "Механика"},
        {"code": "M004_THERMODYNAMICS", "title_kk": "Термодинамика", "title_ru": "Термодинамика"},
    ],
    "M005": [
        {"code": "M005_DATABASES", "title_kk": "Дерекқорлар", "title_ru": "Базы данных"},
        {"code": "M005_NETWORKS", "title_kk": "Желілер", "title_ru": "Сети"},
    ],
}


async def init_majors():
    """Инициализация специальностей"""
    async with async_session_maker() as db:
        # Проверяем существующие специальности
        result = await db.execute(select(func.count(Major.code)))
        count = result.scalar()
        
        if count > 0:
            print(f"⚠️  В базе уже есть {count} специальностей. Пропускаем...")
            return
        
        print("📚 Инициализация специальностей...")
        
        for major_data in MAJORS_DATA:
            major = Major(**major_data)
            db.add(major)
        
        await db.commit()
        print(f"✅ Добавлено {len(MAJORS_DATA)} специальностей")


async def init_common_subjects():
    """Инициализация общих предметов (ТГО, Иностранный язык)"""
    async with async_session_maker() as db:
        # Проверяем существующие предметы
        result = await db.execute(
            select(func.count(Subject.code)).where(Subject.subject_type == "common")
        )
        count = result.scalar()
        
        if count > 0:
            print(f"⚠️  В базе уже есть {count} общих предметов. Пропускаем...")
            return
        
        print("📖 Инициализация общих предметов...")
        
        common_subjects = [
            {
                "code": "TGO",
                "title_kk": "Тарих, география, құқық",
                "title_ru": "История, география, право",
                "subject_type": "common",  # Используем строку напрямую
                "major_code": None
            },
            {
                "code": "ENG",
                "title_kk": "Ағылшын тілі",
                "title_ru": "Английский язык",
                "subject_type": "common",  # Используем строку напрямую
                "major_code": None
            },
        ]
        
        for subject_data in common_subjects:
            subject = Subject(**subject_data)
            db.add(subject)
        
        await db.commit()
        print(f"✅ Добавлено {len(common_subjects)} общих предметов")


async def init_profile_subjects():
    """Инициализация профильных предметов"""
    async with async_session_maker() as db:
        # Проверяем существующие профильные предметы
        result = await db.execute(
            select(func.count(Subject.code)).where(Subject.subject_type == "profile")
        )
        count = result.scalar()
        
        if count > 0:
            print(f"⚠️  В базе уже есть {count} профильных предметов. Пропускаем...")
            return
        
        print("📝 Инициализация профильных предметов...")
        
        total = 0
        for major_code, subjects in PROFILE_SUBJECTS.items():
            for subject_data in subjects:
                subject = Subject(
                    **subject_data,
                    subject_type="profile",  # Используем строку напрямую
                    major_code=major_code
                )
                db.add(subject)
                total += 1
        
        await db.commit()
        print(f"✅ Добавлено {total} профильных предметов")


async def main():
    """Основная функция"""
    print("\n" + "=" * 60)
    print("🎓 Connect AITU - Инициализация базовых данных")
    print("=" * 60 + "\n")
    
    try:
        await init_majors()
        await init_common_subjects()
        await init_profile_subjects()
        
        print("\n" + "=" * 60)
        print("✅ Инициализация завершена успешно!")
        print("=" * 60)
        print("\n📌 Следующие шаги:")
        print("1. Импортировать вопросы: python scripts/import_questions.py")
        print("2. Создать администратора: python scripts/create_admin.py")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Ошибка при инициализации: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())