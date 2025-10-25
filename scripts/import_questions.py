#!/usr/bin/env python3
"""
Скрипт импорта вопросов из JSON файлов

Импортирует вопросы из questions.json в базу данных

Usage:
    python scripts/import_questions.py [path_to_questions.json]
"""
import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import List, Dict

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.db.session import async_session_maker
from app.models.question import Question, QuestionDifficulty, QuestionType
from app.models.subject import Subject


async def import_questions_from_json(json_path: Path):
    """
    Импортировать вопросы из JSON файла
    
    Args:
        json_path: Путь к questions.json
    """
    print(f"\n📥 Импорт вопросов из {json_path}...")
    
    # Читаем JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл не найден: {json_path}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return
    
    # Проверяем формат
    if not isinstance(data, dict) or "questions" not in data:
        print("❌ Неверный формат JSON. Ожидается: {\"questions\": [...]}")
        return
    
    questions_data: List[Dict] = data["questions"]
    total_questions = len(questions_data)
    
    print(f"   📊 Найдено {total_questions} вопросов в JSON")
    
    async with async_session_maker() as db:
        try:
            # Проверяем существующие вопросы
            result = await db.execute(select(func.count(Question.id)))
            existing_count = result.scalar() or 0
            
            if existing_count > 0:
                print(f"   ℹ️  В БД уже существует {existing_count} вопросов")
                overwrite = input("   Очистить существующие и импортировать заново? (y/N): ").strip().lower()
                
                if overwrite == 'y':
                    # Удаляем все вопросы
                    await db.execute("DELETE FROM questions")
                    await db.commit()
                    print("   ✅ Существующие вопросы удалены")
                else:
                    print("   ⏭️  Добавление новых вопросов к существующим")
            
            # Импортируем вопросы
            created_count = 0
            skipped_count = 0
            error_count = 0
            
            for i, q_data in enumerate(questions_data, 1):
                try:
                    # Валидация обязательных полей
                    required_fields = ["subject_code", "question_text", "options"]
                    
                    for field in required_fields:
                        if field not in q_data:
                            print(f"   ⚠️  Вопрос {i}: отсутствует поле '{field}', пропуск")
                            skipped_count += 1
                            continue
                    
                    # Проверяем существование предмета
                    subject_code = q_data["subject_code"]
                    result = await db.execute(
                        select(Subject).where(Subject.code == subject_code)
                    )
                    subject = result.scalar_one_or_none()
                    
                    if not subject:
                        print(f"   ⚠️  Вопрос {i}: предмет '{subject_code}' не найден, пропуск")
                        skipped_count += 1
                        continue
                    
                    # Парсим difficulty
                    difficulty_str = q_data.get("difficulty", "medium")
                    try:
                        difficulty = QuestionDifficulty(difficulty_str)
                    except ValueError:
                        difficulty = QuestionDifficulty.MEDIUM
                    
                    # Парсим question_type
                    question_type_str = q_data.get("question_type", "single")
                    try:
                        question_type = QuestionType(question_type_str)
                    except ValueError:
                        question_type = QuestionType.SINGLE
                    
                    # Создаем вопрос
                    question = Question(
                        subject_code=subject_code,
                        question_text=q_data["question_text"],
                        options=q_data["options"],  # JSON массив
                        difficulty=difficulty,
                        question_type=question_type,
                        points=q_data.get("points", 1),
                        time_seconds=q_data.get("time_seconds", 60),
                        explanation=q_data.get("explanation"),
                        tags=q_data.get("tags", [])
                    )
                    
                    db.add(question)
                    created_count += 1
                    
                    # Коммитим каждые 100 вопросов
                    if created_count % 100 == 0:
                        await db.commit()
                        print(f"   ⏳ Импортировано {created_count}/{total_questions}...")
                
                except Exception as e:
                    print(f"   ❌ Ошибка при импорте вопроса {i}: {e}")
                    error_count += 1
                    continue
            
            # Финальный коммит
            await db.commit()
            
            print(f"\n   ✅ Импорт завершен:")
            print(f"      - Создано: {created_count}")
            print(f"      - Пропущено: {skipped_count}")
            print(f"      - Ошибок: {error_count}")
            
        except Exception as e:
            print(f"   ❌ Критическая ошибка: {e}")
            await db.rollback()
            raise


async def show_statistics():
    """Показать статистику по вопросам"""
    print("\n📊 Статистика вопросов:")
    
    async with async_session_maker() as db:
        try:
            # Общее количество
            result = await db.execute(select(func.count(Question.id)))
            total = result.scalar() or 0
            print(f"   Всего вопросов: {total}")
            
            # По предметам
            result = await db.execute(
                select(
                    Question.subject_code,
                    func.count(Question.id)
                ).group_by(Question.subject_code)
            )
            by_subject = result.all()
            
            if by_subject:
                print("\n   По предметам:")
                for subject_code, count in by_subject:
                    print(f"      {subject_code}: {count}")
            
            # По сложности
            result = await db.execute(
                select(
                    Question.difficulty,
                    func.count(Question.id)
                ).group_by(Question.difficulty)
            )
            by_difficulty = result.all()
            
            if by_difficulty:
                print("\n   По сложности:")
                for difficulty, count in by_difficulty:
                    print(f"      {difficulty.value}: {count}")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")


async def main():
    """Главная функция"""
    print("=" * 60)
    print("📚 Импорт вопросов в Connect AITU")
    print("=" * 60)
    
    # Определяем путь к JSON
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
    else:
        # По умолчанию ищем в корне проекта
        json_path = Path(__file__).parent.parent / "questions.json"
    
    if not json_path.exists():
        print(f"\n❌ Файл не найден: {json_path}")
        print("\nИспользование:")
        print("   python scripts/import_questions.py [path/to/questions.json]")
        print("\nФормат questions.json:")
        print("""
{
  "questions": [
    {
      "subject_code": "TGO",
      "question_text": "Какой год?",
      "options": [
        {"key": "A", "text": "2024", "is_correct": false},
        {"key": "B", "text": "2025", "is_correct": true}
      ],
      "difficulty": "easy",
      "question_type": "single",
      "points": 1,
      "time_seconds": 60,
      "explanation": "Объяснение...",
      "tags": ["история", "даты"]
    }
  ]
}
        """)
        sys.exit(1)
    
    try:
        await import_questions_from_json(json_path)
        await show_statistics()
        
        print("\n" + "=" * 60)
        print("✅ Импорт завершен!")
        print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Отменено пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
