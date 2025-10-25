#!/usr/bin/env python3
"""
Скрипт импорта данных из JSON файлов
"""
import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, List

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.question import Question, QuestionDifficulty, QuestionType


async def load_questions_from_json(json_path: str = "questions.json"):
    """
    Загрузить вопросы из JSON файла
    
    Формат JSON:
    [
        {
            "id": "uuid",
            "subject_code": "TGO",
            "question_text": "...",
            "options": [
                {"key": "A", "text": "...", "is_correct": true},
                {"key": "B", "text": "...", "is_correct": false}
            ],
            "difficulty": "medium",
            "question_type": "single",
            "points": 1,
            "time_seconds": 60,
            "explanation": "...",
            "tags": ["tag1", "tag2"]
        }
    ]
    """
    
    print("=" * 60)
    print("📥 ИМПОРТ ВОПРОСОВ ИЗ JSON")
    print("=" * 60)
    
    # Проверяем существование файла
    json_file = Path(json_path)
    if not json_file.exists():
        print(f"\n❌ Файл не найден: {json_path}")
        print(f"\nПоложите файл questions.json в корень проекта")
        return
    
    try:
        # Загружаем JSON
        print(f"\n📂 Чтение файла: {json_path}")
        with open(json_file, "r", encoding="utf-8") as f:
            questions_data = json.load(f)
        
        print(f"✅ Найдено вопросов: {len(questions_data)}")
        
        # Статистика по предметам
        subjects_count: Dict[str, int] = {}
        for q in questions_data:
            subject = q.get("subject_code", "UNKNOWN")
            subjects_count[subject] = subjects_count.get(subject, 0) + 1
        
        print(f"\n📊 Вопросы по предметам:")
        for subject, count in sorted(subjects_count.items()):
            print(f"   {subject}: {count}")
        
        confirm = input("\n\nПродолжить импорт? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y", "да"]:
            print("❌ Отменено")
            return
        
        # Импортируем в БД
        async with async_session_maker() as db:
            imported_count = 0
            updated_count = 0
            skipped_count = 0
            
            print("\n📥 Импорт вопросов...")
            
            for idx, q_data in enumerate(questions_data, 1):
                try:
                    # Извлекаем данные
                    question_id = q_data.get("id")
                    subject_code = q_data.get("subject_code")
                    question_text = q_data.get("question_text")
                    options = q_data.get("options", [])
                    difficulty = q_data.get("difficulty", "medium")
                    question_type = q_data.get("question_type", "single")
                    points = q_data.get("points", 1)
                    time_seconds = q_data.get("time_seconds", 60)
                    explanation = q_data.get("explanation")
                    tags = q_data.get("tags", [])
                    
                    # Проверяем существование
                    if question_id:
                        result = await db.execute(
                            select(Question).where(Question.id == question_id)
                        )
                        existing = result.scalar_one_or_none()
                    else:
                        existing = None
                    
                    # Преобразуем типы
                    try:
                        difficulty_enum = QuestionDifficulty(difficulty)
                    except ValueError:
                        difficulty_enum = QuestionDifficulty.MEDIUM
                    
                    try:
                        type_enum = QuestionType(question_type)
                    except ValueError:
                        type_enum = QuestionType.SINGLE
                    
                    if existing:
                        # Обновляем существующий
                        existing.subject_code = subject_code
                        existing.question_text = question_text
                        existing.options = options
                        existing.difficulty = difficulty_enum
                        existing.question_type = type_enum
                        existing.points = points
                        existing.time_seconds = time_seconds
                        existing.explanation = explanation
                        existing.tags = tags
                        
                        updated_count += 1
                    else:
                        # Создаем новый
                        question = Question(
                            id=question_id,
                            subject_code=subject_code,
                            question_text=question_text,
                            options=options,
                            difficulty=difficulty_enum,
                            question_type=type_enum,
                            points=points,
                            time_seconds=time_seconds,
                            explanation=explanation,
                            tags=tags
                        )
                        db.add(question)
                        imported_count += 1
                    
                    # Коммитим каждые 100 вопросов
                    if idx % 100 == 0:
                        await db.commit()
                        print(f"   Обработано: {idx}/{len(questions_data)}")
                
                except Exception as e:
                    print(f"   ⚠️  Ошибка при импорте вопроса #{idx}: {e}")
                    skipped_count += 1
                    continue
            
            # Финальный коммит
            await db.commit()
            
            print("\n" + "=" * 60)
            print("✅ ИМПОРТ ЗАВЕРШЕН!")
            print("=" * 60)
            print(f"   Импортировано новых: {imported_count}")
            print(f"   Обновлено: {updated_count}")
            print(f"   Пропущено (ошибки): {skipped_count}")
            print(f"   Всего обработано: {len(questions_data)}")
    
    except json.JSONDecodeError as e:
        print(f"\n❌ Ошибка парсинга JSON: {e}")
    except Exception as e:
        print(f"\n❌ Ошибка при импорте: {e}")
        raise


async def export_questions_to_json(
    output_path: str = "questions_export.json",
    subject_code: str | None = None
):
    """
    Экспортировать вопросы в JSON файл
    
    Args:
        output_path: Путь для сохранения
        subject_code: Фильтр по предмету (None = все)
    """
    
    print("=" * 60)
    print("📤 ЭКСПОРТ ВОПРОСОВ В JSON")
    print("=" * 60)
    
    async with async_session_maker() as db:
        try:
            # Получаем вопросы
            query = select(Question)
            if subject_code:
                query = query.where(Question.subject_code == subject_code)
                print(f"\n📂 Фильтр: {subject_code}")
            
            result = await db.execute(query)
            questions = result.scalars().all()
            
            print(f"✅ Найдено вопросов: {len(questions)}")
            
            # Преобразуем в dict
            questions_data = []
            for q in questions:
                questions_data.append({
                    "id": str(q.id),
                    "subject_code": q.subject_code,
                    "question_text": q.question_text,
                    "options": q.options,
                    "difficulty": q.difficulty.value,
                    "question_type": q.question_type.value,
                    "points": q.points,
                    "time_seconds": q.time_seconds,
                    "explanation": q.explanation,
                    "tags": q.tags,
                })
            
            # Сохраняем в файл
            output_file = Path(output_path)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    questions_data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            
            print(f"✅ Экспортировано в: {output_path}")
        
        except Exception as e:
            print(f"\n❌ Ошибка при экспорте: {e}")
            raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Импорт/Экспорт вопросов")
    parser.add_argument(
        "action",
        choices=["import", "export"],
        help="Действие: import (импортировать), export (экспортировать)"
    )
    parser.add_argument(
        "--file",
        default="questions.json",
        help="Путь к JSON файлу"
    )
    parser.add_argument(
        "--subject",
        help="Фильтр по предмету (только для export)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "🎓 Connect AITU - Импорт/Экспорт данных".center(60))
    
    if args.action == "import":
        asyncio.run(load_questions_from_json(args.file))
    elif args.action == "export":
        asyncio.run(export_questions_to_json(args.file, args.subject))
