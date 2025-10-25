"""
ОБНОВЛЕНИЕ: Добавить в exam_service.py после создания ExamAttempt

В методе start_exam() после await db.commit():
"""

# После: await db.commit()

# Запускаем Celery задачу на автозавершение
from app.tasks.exam_tasks import auto_finish_exam

auto_finish_exam.apply_async(
    args=[str(attempt.id)],
    countdown=time_limit_minutes * 60  # Задержка в секундах
)

# Опционально: напоминание за 10 минут до конца
if time_limit_minutes > 10:
    from app.tasks.exam_tasks import send_exam_reminder
    
    send_exam_reminder.apply_async(
        args=[str(attempt.id), 10],
        countdown=(time_limit_minutes - 10) * 60
    )

# Продолжение кода...
return ExamStartResponse(...)
