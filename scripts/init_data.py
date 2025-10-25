#!/usr/bin/env python3
"""
Инициализация базовых данных из sorted_pairs.json
"""
import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.db.session import async_session_maker
from app.models.major import Major
from app.models.subject import Subject


async def init_majors():
    """Загрузка специальностей из sorted_pairs.json"""
    async with async_session_maker() as db:
        result = await db.execute(select(func.count(Major.code)))
        if result.scalar() > 0:
            print(f"⚠️  Специальности уже загружены")
            return
        
        # Загружаем sorted_pairs.json
        json_path = Path(__file__).parent.parent / "data" / "sorted_pairs.json"
        if not json_path.exists():
            print(f"❌ Файл {json_path} не найден!")
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📚 Загрузка {len(data)} специальностей...")
        
        for code, info in data.items():
            # Определяем тип магистратуры по коду
            # M001-M021, M050-M079, M111-M153 - профильная
            # M080-M110 - научно-педагогическая
            code_num = int(code[1:])
            if 80 <= code_num <= 110:
                mag_type = "scientific_pedagogical"
            else:
                mag_type = "profile"
            
            major = Major(
                code=code,
                title_kk=info["title"],
                title_ru=info.get("title_ru"),
                magistracy_type=mag_type,
                categories=info["categories"],
                is_active=True
            )
            db.add(major)
        
        await db.commit()
        print(f"✅ Загружено {len(data)} специальностей")


async def init_common_subjects():
    """Создание общих предметов"""
    async with async_session_maker() as db:
        result = await db.execute(
            select(func.count(Subject.code)).where(Subject.subject_type == "common")
        )
        if result.scalar() > 0:
            print(f"⚠️  Общие предметы уже созданы")
            return
        
        print("📖 Создание общих предметов...")
        
        subjects = [
            {
                "code": "TGO",
                "title_kk": "Тарих, география, құқық",
                "title_ru": "История, география, право",
                "subject_type": "common",
                "major_code": None
            },
            {
                "code": "ENG",
                "title_kk": "Ағылшын тілі",
                "title_ru": "Английский язык",
                "subject_type": "common",
                "major_code": None
            },
        ]
        
        for s in subjects:
            subject = Subject(**s)
            db.add(subject)
        
        await db.commit()
        print(f"✅ Создано {len(subjects)} общих предметов")


async def init_profile_subjects():
    """Создание профильных предметов из categories"""
    async with async_session_maker() as db:
        result = await db.execute(
            select(func.count(Subject.code)).where(Subject.subject_type == "profile")
        )
        if result.scalar() > 0:
            print(f"⚠️  Профильные предметы уже созданы")
            return
        
        print("📝 Создание профильных предметов...")
        
        # Получаем все специальности
        result = await db.execute(select(Major))
        majors = result.scalars().all()
        
        total = 0
        for major in majors:
            for i, category in enumerate(major.categories, 1):
                code = f"{major.code}_SUBJ{i}"
                
                subject = Subject(
                    code=code,
                    title_kk=category,
                    title_ru=category,
                    subject_type="profile",
                    major_code=major.code,
                    is_active=True
                )
                db.add(subject)
                total += 1
        
        await db.commit()
        print(f"✅ Создано {total} профильных предметов")


async def main():
    print("\n" + "=" * 60)
    print("🎓 Инициализация базовых данных")
    print("=" * 60 + "\n")
    
    try:
        await init_majors()
        await init_common_subjects()
        await init_profile_subjects()
        
        print("\n" + "=" * 60)
        print("✅ Инициализация завершена!")
        print("=" * 60)
        print("\n📌 Следующий шаг: python scripts/create_admin.py\n")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())