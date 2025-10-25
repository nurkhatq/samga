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
        "magistracy_type": MagistracyType.PROFILE,
        "categories": ["Білім беру"]
    },
    {
        "code": "M002",
        "title_kk": "Бастауыш оқыту педагогикасы мен әдістемесі",
        "title_ru": "Педагогика и методика начального обучения",
        "magistracy_type": MagistracyType.PROFILE,
        "categories": ["Білім беру"]
    },
    {
        "code": "M003",
        "title_kk": "Математика",
        "title_ru": "Математика",
        "magistracy_type": MagistracyType.SCIENTIFIC,
        "categories": ["Жаратылыстану"]
    },
    {
        "code": "M004",
        "title_kk": "Физика",
        "title_ru": "Физика",
        "magistracy_type": MagistracyType.SCIENTIFIC,
        "categories": ["Жаратылыстану"]
    },
    {
        "code": "M005",
        "title_kk": "Ақпараттық жүйелер",
        "title_ru": "Информационные системы",
        "magistracy_type": MagistracyType.PROFILE,
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
        {"code": "M003_ANALYSIS", "title_kk": "Анализ", "title_ru": "Анализ"},
    ],
    "M004": [
        {"code": "M004_MECHANICS", "title_kk": "Механика", "title_ru": "Механика"},
        {"code": "M004_QUANTUM", "title_kk": "Кванттық физика", "title_ru": "Квантовая физика"},
    ],
    "M005": [
        {"code": "M005_DATABASES", "title_kk": "Дерекқорлар", "title_ru": "Базы данных"},
        {"code": "M005_NETWORKS", "title_kk": "Желілер", "title_ru": "Сети"},
    ],
}


async def init_majors():
    """Инициализировать специальности"""
    print("\n📚 Инициализация специальностей...")
    
    async with async_session_maker() as db:
        try:
            # Проверяем существующие
            result = await db.execute(select(func.count(Major.code)))
            existing_count = result.scalar() or 0
            
            if existing_count > 0:
                print(f"   ℹ️  Уже существует {existing_count} специальностей")
                overwrite = input("   Перезаписать? (y/N): ").strip().lower()
                
                if overwrite != 'y':
                    print("   ⏭️  Пропуск инициализации специальностей")
                    return
            
            # Создаем специальности
            created_count = 0
            
            for major_data in MAJORS_DATA:
                # Проверяем существование
                result = await db.execute(
                    select(Major).where(Major.code == major_data["code"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"   ⏭️  Специальность {major_data['code']} уже существует")
                    continue
                
                major = Major(**major_data)
                db.add(major)
                created_count += 1
            
            await db.commit()
            
            print(f"   ✅ Создано {created_count} специальностей")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            await db.rollback()
            raise


async def init_subjects():
    """Инициализировать предметы"""
    print("\n📖 Инициализация предметов...")
    
    async with async_session_maker() as db:
        try:
            # Проверяем существующие
            result = await db.execute(select(func.count(Subject.code)))
            existing_count = result.scalar() or 0
            
            if existing_count > 0:
                print(f"   ℹ️  Уже существует {existing_count} предметов")
                overwrite = input("   Перезаписать? (y/N): ").strip().lower()
                
                if overwrite != 'y':
                    print("   ⏭️  Пропуск инициализации предметов")
                    return
            
            created_count = 0
            
            # 1. Общие предметы (ТГО, АНГЛ)
            common_subjects = [
                {
                    "code": "TGO",
                    "title_kk": "Тарих, география және қоғамтану",
                    "title_ru": "История, география и обществознание",
                    "subject_type": SubjectType.COMMON,
                },
                {
                    "code": "ENG",
                    "title_kk": "Шетел тілі (ағылшын)",
                    "title_ru": "Иностранный язык (английский)",
                    "subject_type": SubjectType.COMMON,
                },
            ]
            
            for subject_data in common_subjects:
                result = await db.execute(
                    select(Subject).where(Subject.code == subject_data["code"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    continue
                
                subject = Subject(**subject_data)
                db.add(subject)
                created_count += 1
            
            # 2. Профильные предметы для каждой специальности
            for major_code, subjects_list in PROFILE_SUBJECTS.items():
                for subject_data in subjects_list:
                    result = await db.execute(
                        select(Subject).where(Subject.code == subject_data["code"])
                    )
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        continue
                    
                    subject = Subject(
                        code=subject_data["code"],
                        title_kk=subject_data["title_kk"],
                        title_ru=subject_data["title_ru"],
                        subject_type=SubjectType.PROFILE,
                        major_code=major_code
                    )
                    db.add(subject)
                    created_count += 1
            
            await db.commit()
            
            print(f"   ✅ Создано {created_count} предметов")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            await db.rollback()
            raise


async def main():
    """Главная функция"""
    print("=" * 60)
    print("🚀 Инициализация базовых данных Connect AITU")
    print("=" * 60)
    
    try:
        await init_majors()
        await init_subjects()
        
        print("\n" + "=" * 60)
        print("✅ Инициализация завершена!")
        print("=" * 60)
        
        print("\n💡 Следующие шаги:")
        print("   1. Импортируйте вопросы: python scripts/import_questions.py")
        print("   2. Создайте админа: python scripts/create_admin.py")
        print("   3. Запустите сервер: python -m app.main\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Отменено пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
