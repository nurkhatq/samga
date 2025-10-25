# Celery - Фоновые задачи

## 🚀 Быстрый старт

### 1. Запуск Celery Worker

```bash
# В отдельном терминале
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

### 2. Запуск Celery Beat (планировщик)

```bash
# В отдельном терминале
celery -A app.tasks.celery_app beat --loglevel=info
```

### 3. Мониторинг Celery Flower (опционально)

```bash
celery -A app.tasks.celery_app flower --port=5555
```

Откройте в браузере: http://localhost:5555

---

## 📋 Задачи

### **Exam Tasks** (app.tasks.exam_tasks)

#### 1. `auto_finish_exam`
**Описание:** Автоматически завершает экзамен по истечении времени

**Запуск:** Автоматически при старте экзамена (с задержкой = time_limit_minutes)

**Что делает:**
- Проверяет все ответы
- Подсчитывает баллы
- Сохраняет статистику прокторинга
- Помечает экзамен как EXPIRED
- Удаляет сессию из Redis

**Пример использования:**
```python
from app.tasks.exam_tasks import auto_finish_exam

# При старте экзамена в exam_service.py
auto_finish_exam.apply_async(
    args=[str(attempt.id)],
    countdown=time_limit_minutes * 60  # Задержка в секундах
)
```

#### 2. `send_exam_reminder`
**Описание:** Отправляет напоминание о времени экзамена

**Параметры:**
- `attempt_id` - UUID попытки
- `minutes_remaining` - Минут осталось

**TODO:** Интеграция с Firebase/SendGrid

---

### **Cleanup Tasks** (app.tasks.cleanup_tasks)

#### 1. `cleanup_expired_exams`
**Описание:** Очищает истекшие экзамены

**Расписание:** Каждые 5 минут (Celery Beat)

**Что делает:**
- Ищет экзамены в статусе IN_PROGRESS
- Проверяет время (limit + buffer)
- Помечает как EXPIRED
- Удаляет из Redis

#### 2. `cleanup_old_redis_sessions`
**Описание:** Очищает старые сессии из Redis

**Расписание:** Каждый час (Celery Beat)

**TODO:** Реализовать SCAN по ключам exam:attempt:*

#### 3. `cleanup_old_proctoring_events`
**Описание:** Удаляет события прокторинга старше 90 дней

**Расписание:** Ручной запуск или добавить в beat_schedule

**Запуск:**
```bash
celery -A app.tasks.celery_app call app.tasks.cleanup_tasks.cleanup_old_proctoring_events
```

#### 4. `archive_old_attempts`
**Описание:** Архивирует старые попытки экзаменов

**Параметры:**
- `days` - Архивировать старше этого количества дней (default: 180)

**TODO:** Реализовать экспорт в S3/архивную таблицу

---

## ⚙️ Конфигурация

### Celery Beat Schedule

В `app/tasks/celery_app.py`:

```python
beat_schedule = {
    "cleanup-expired-exams": {
        "task": "app.tasks.cleanup_tasks.cleanup_expired_exams",
        "schedule": 300.0,  # Каждые 5 минут
    },
    "cleanup-old-redis-sessions": {
        "task": "app.tasks.cleanup_tasks.cleanup_old_redis_sessions",
        "schedule": 3600.0,  # Каждый час
    },
}
```

### Task Routes

```python
task_routes = {
    "app.tasks.exam_tasks.*": {"queue": "exams"},
    "app.tasks.cleanup_tasks.*": {"queue": "cleanup"},
}
```

---

## 🐳 Docker

### docker-compose.yml

```yaml
celery-worker:
  build: .
  command: celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
  depends_on:
    - redis
    - postgres
  environment:
    - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/connect_aitu
    - REDIS_URL=redis://redis:6379/0

celery-beat:
  build: .
  command: celery -A app.tasks.celery_app beat --loglevel=info
  depends_on:
    - redis
    - postgres
  environment:
    - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/connect_aitu
    - REDIS_URL=redis://redis:6379/0

celery-flower:
  build: .
  command: celery -A app.tasks.celery_app flower --port=5555
  ports:
    - "5555:5555"
  depends_on:
    - redis
  environment:
    - REDIS_URL=redis://redis:6379/0
```

---

## 📊 Мониторинг

### Celery Flower

```bash
celery -A app.tasks.celery_app flower
```

URL: http://localhost:5555

**Возможности:**
- Мониторинг задач в реальном времени
- История выполнения
- Статистика по worker'ам
- Управление задачами

### Логи

```bash
# Worker логи
celery -A app.tasks.celery_app worker --loglevel=debug

# Beat логи
celery -A app.tasks.celery_app beat --loglevel=debug
```

---

## 🧪 Тестирование

### Ручной запуск задачи

```python
from app.tasks.exam_tasks import auto_finish_exam

# Немедленно
result = auto_finish_exam.delay("attempt-uuid-here")

# С задержкой 60 секунд
result = auto_finish_exam.apply_async(
    args=["attempt-uuid-here"],
    countdown=60
)

# Проверить статус
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)  # Результат выполнения
```

### Очистить очередь

```bash
celery -A app.tasks.celery_app purge
```

---

## 🔧 Troubleshooting

### Проблема: Task not found

**Решение:** Убедитесь что модули импортированы в celery_app.py:
```python
include=["app.tasks.exam_tasks", "app.tasks.cleanup_tasks"]
```

### Проблема: Connection refused (Redis)

**Решение:** Проверьте REDIS_URL в .env:
```bash
REDIS_URL=redis://localhost:6379/0
```

### Проблема: Database connection error

**Решение:** Используйте async_session_maker в задачах:
```python
async with async_session_maker() as db:
    # ваш код
```

---

## 📚 Полезные команды

```bash
# Показать активные задачи
celery -A app.tasks.celery_app inspect active

# Показать зарегистрированные задачи
celery -A app.tasks.celery_app inspect registered

# Статистика worker'ов
celery -A app.tasks.celery_app inspect stats

# Остановить worker
celery -A app.tasks.celery_app control shutdown
```
