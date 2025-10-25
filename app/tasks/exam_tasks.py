"""
Celery задачи для экзаменов
"""
import uuid
from datetime import datetime
from celery import Task
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.db.session import async_session_maker
from app.models.exam import ExamAttempt, ExamAnswer, ExamStatus
from app.models.question import Question
from app.services.redis_service import redis_service
from app.services.question_service import question_service


class DatabaseTask(Task):
    """Базовый класс для задач с БД"""
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = async_session_maker()
        return self._db


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.exam_tasks.auto_finish_exam",
    max_retries=3,
    default_retry_delay=60
)
def auto_finish_exam(self, attempt_id: str):
    """
    Автоматически завершить экзамен по истечении времени
    
    Args:
        attempt_id: UUID попытки экзамена
    
    Эта задача запускается с задержкой = time_limit_minutes
    при старте экзамена.
    """
    import asyncio
    
    async def _finish_exam():
        async with async_session_maker() as db:
            try:
                # Получаем попытку
                attempt_uuid = uuid.UUID(attempt_id)
                result = await db.execute(
                    select(ExamAttempt).where(
                        ExamAttempt.id == attempt_uuid,
                        ExamAttempt.status == ExamStatus.IN_PROGRESS
                    )
                )
                attempt = result.scalar_one_or_none()
                
                if not attempt:
                    print(f"⚠️ Attempt {attempt_id} not found or already completed")
                    return
                
                # Проверяем что время действительно истекло
                elapsed = (datetime.utcnow() - attempt.started_at).total_seconds()
                time_limit = attempt.time_limit_minutes * 60
                
                if elapsed < time_limit:
                    print(f"⚠️ Attempt {attempt_id} time not expired yet")
                    return
                
                # Получаем сессию из Redis
                session = await redis_service.get_exam_session(attempt_id)
                
                if not session:
                    print(f"⚠️ Session {attempt_id} not found in Redis")
                    # Помечаем как expired без проверки
                    attempt.status = ExamStatus.EXPIRED
                    attempt.completed_at = datetime.utcnow()
                    await db.commit()
                    return
                
                # Проверяем все ответы
                answers_dict = session.get("answers", {})
                correct_count = 0
                
                for question_id_str, selected_keys in answers_dict.items():
                    try:
                        question_uuid = uuid.UUID(question_id_str)
                        q_result = await db.execute(
                            select(Question).where(Question.id == question_uuid)
                        )
                        question = q_result.scalar_one_or_none()
                        
                        if not question:
                            continue
                        
                        is_correct, _ = question_service.check_answer(
                            question, selected_keys
                        )
                        
                        # Сохраняем ответ
                        answer = ExamAnswer(
                            attempt_id=attempt.id,
                            question_id=question_uuid,
                            selected_keys=selected_keys,
                            is_correct=is_correct,
                            answered_at=datetime.utcnow()
                        )
                        db.add(answer)
                        
                        if is_correct:
                            correct_count += 1
                    
                    except Exception as e:
                        print(f"❌ Error processing question {question_id_str}: {e}")
                        continue
                
                # Обновляем попытку
                attempt.completed_at = datetime.utcnow()
                attempt.status = ExamStatus.EXPIRED  # Помечаем как expired
                attempt.answered_questions = len(answers_dict)
                attempt.correct_answers = correct_count
                attempt.score_percentage = (
                    correct_count / attempt.total_questions * 100
                    if attempt.total_questions > 0 else 0
                )
                
                # Прокторинг
                proctoring = session.get("proctoring", {})
                attempt.proctoring_copy_paste_count = proctoring.get("copy_paste", 0)
                attempt.proctoring_tab_switches_count = proctoring.get("tab_switches", 0)
                attempt.proctoring_console_opens_count = proctoring.get("console_opens", 0)
                
                # Проверяем подозрительность
                from app.core.config import settings
                total_suspicious = (
                    attempt.proctoring_copy_paste_count +
                    attempt.proctoring_tab_switches_count +
                    attempt.proctoring_console_opens_count
                )
                attempt.proctoring_suspicious = (
                    total_suspicious >= settings.PROCTORING_SUSPICIOUS_THRESHOLD
                )
                
                await db.commit()
                
                # Удаляем сессию из Redis
                await redis_service.delete_exam_session(attempt_id)
                
                print(f"✅ Auto-finished exam {attempt_id}: {correct_count}/{attempt.total_questions}")
            
            except Exception as e:
                print(f"❌ Error auto-finishing exam {attempt_id}: {e}")
                await db.rollback()
                raise
    
    # Запускаем асинхронную функцию
    asyncio.run(_finish_exam())


@celery_app.task(
    name="app.tasks.exam_tasks.send_exam_reminder",
    max_retries=3
)
def send_exam_reminder(attempt_id: str, minutes_remaining: int):
    """
    Отправить напоминание о времени экзамена
    
    Args:
        attempt_id: UUID попытки
        minutes_remaining: Минут осталось
    
    TODO: Интеграция с системой уведомлений
    """
    print(f"⏰ Exam {attempt_id}: {minutes_remaining} minutes remaining")
    
    # TODO: Отправить push-уведомление или email
    # Можно использовать Firebase, SendGrid, и т.д.
    
    return {
        "attempt_id": attempt_id,
        "minutes_remaining": minutes_remaining,
        "sent_at": datetime.utcnow().isoformat()
    }
