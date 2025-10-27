#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание subjects и импорт вопросов
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.subject import Subject, SubjectType
from app.models.question import Question, QuestionDifficulty, QuestionType

# Маппинг course_id -> (major_code, subject_name)
COURSE_MAPPING = {
    "COURSE_45": ("M123", "Геодезия"),
    "COURSE_46": (None, "Тау-кен ісі (Горное дело)"),
    "COURSE_47": (None, "Сәулет және қала құрылысы (Архитектура)"),
}

async def create_subjects_and_import(tests_file: str, questions_file: str):
    """Создать subjects и импортировать вопросы"""
    
    print("=" * 60)
    print("ШАГ 1: Создание предметов")
    print("=" * 60)
    
    # Загружаем tests.json
    with open(tests_file, 'r', encoding='utf-8') as f:
        tests_data = json.load(f)
    
    # Создаем маппинг test_id -> course_id
    test_to_course = {}
    for test in tests_data['tests']:
        test_to_course[test['test_id']] = test['course_id']
    
    async with async_session_maker() as db:
        # Создаем subjects
        for course_id, (major_code, name) in COURSE_MAPPING.items():
            # Проверяем существование
            result = await db.execute(
                select(Subject).where(Subject.code == course_id)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"   EXISTS: {course_id}")
                continue
            
            # Создаем
            subject = Subject(
                code=course_id,
                title_kk=name,
                title_ru=name,
                subject_type=SubjectType.PROFILE,
                major_code=major_code,
                is_active=True
            )
            db.add(subject)
            print(f"   CREATED: {course_id} - {name}")
        
        await db.commit()
    
    print("\n" + "=" * 60)
    print("ШАГ 2: Импорт вопросов")
    print("=" * 60)
    
    # Загружаем questions.json
    with open(questions_file, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    questions_list = questions_data.get('questions', [])
    print(f"   Всего вопросов: {len(questions_list)}")
    
    created = 0
    skipped = 0
    errors = 0
    
    async with async_session_maker() as db:
        for idx, q_data in enumerate(questions_list, 1):
            try:
                # Получаем subject_code через test_id
                test_id = q_data.get('test_id')
                if not test_id:
                    skipped += 1
                    continue
                
                course_id = test_to_course.get(test_id)
                if not course_id:
                    skipped += 1
                    continue
                
                # Создаем вопрос
                question = Question(
                    subject_code=course_id,
                    question_text=q_data['question_text'],
                    difficulty=QuestionDifficulty(q_data['difficulty']),
                    question_type=QuestionType(q_data['type']),
                    points=q_data.get('points', 1),
                    time_seconds=q_data.get('time_seconds', 90),
                    options=q_data['options'],
                    explanation=q_data.get('explanation'),
                    tags=q_data.get('tags', [])
                )
                
                db.add(question)
                created += 1
                
                if created % 500 == 0:
                    await db.commit()
                    print(f"   Импортировано: {created}/{len(questions_list)}")
                
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"   ОШИБКА вопрос {idx}: {e}")
        
        await db.commit()
    
    print("\n" + "=" * 60)
    print("ИМПОРТ ЗАВЕРШЕН")
    print("=" * 60)
    print(f"   Создано: {created}")
    print(f"   Пропущено: {skipped}")
    print(f"   Ошибок: {errors}")
    
    # Статистика
    async with async_session_maker() as db:
        from sqlalchemy import func
        
        result = await db.execute(
            select(Question.subject_code, func.count(Question.id))
            .group_by(Question.subject_code)
        )
        
        print("\nСтатистика по предметам:")
        for subject_code, count in result:
            print(f"   {subject_code}: {count} вопросов")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_subjects_and_import.py tests.json questions.json")
        sys.exit(1)
    
    asyncio.run(create_subjects_and_import(sys.argv[1], sys.argv[2]))
