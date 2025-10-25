# 🎓 Connect AITU Backend

Backend API для платформы подготовки к экзаменам в магистратуру Казахстана.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Особенности

### **Два режима подготовки:**

**🎯 Свободный режим (Practice Mode):**
- Пагинация по 20 вопросов
- Мгновенная проверка ответов
- Объяснения правильных ответов
- Статистика в реальном времени
- Сохранение прогресса (7 дней)

**📝 Режим экзамена (Exam Mode):**
- Генерация по типу магистратуры:
  - **Профильная:** 50 вопросов, 90 минут
  - **Научно-педагогическая:** 130 вопросов, 180 минут
- Автозавершение по таймеру (Celery)
- Прокторинг подозрительных действий
- Проверка только при завершении

### **🔒 Безопасность:**
- JWT авторизация (access + refresh)
- Role-based access control
- Вопросы БЕЗ правильных ответов
- Проверка только на бекенде
- Rate limiting (60 req/min)
- Password hashing (bcrypt)

## 🛠 Технологии

- **FastAPI** - Веб-фреймворк
- **SQLAlchemy 2.0** - ORM (async)
- **PostgreSQL 16** - База данных
- **Redis 7** - Кеширование
- **Celery** - Фоновые задачи
- **Alembic** - Миграции
- **Pydantic 2.0** - Валидация

## 📦 Быстрый старт

### С Docker (рекомендуется)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/your-org/connect-aitu-backend.git
cd connect-aitu-backend

# 2. Настроить .env
cp .env.example .env
# Отредактируйте .env

# 3. Запустить все сервисы
docker-compose up -d

# 4. Применить миграции
docker-compose exec backend alembic upgrade head

# 5. Инициализировать данные
docker-compose exec backend python scripts/init_data.py
docker-compose exec backend python scripts/create_admin.py

# API доступен: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Без Docker

```bash
# 1. Установить зависимости
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Настроить .env
cp .env.example .env

# 3. Запустить PostgreSQL и Redis
# (используйте Docker или локальную установку)

# 4. Применить миграции
alembic upgrade head

# 5. Инициализировать
python scripts/init_data.py
python scripts/create_admin.py

# 6. Запустить
# Терминал 1:
python -m app.main

# Терминал 2:
celery -A app.tasks.celery_app worker --beat --loglevel=info
```

## 📚 API Документация

### Swagger UI
http://localhost:8000/docs

### Основные endpoints:

**Авторизация:**
```
POST /api/auth/login       - Вход
POST /api/auth/refresh     - Обновить токен
```

**Свободный режим:**
```
POST /api/practice/start
GET  /api/practice/{subject}/questions
POST /api/practice/{subject}/submit-answer
```

**Режим экзамена:**
```
POST /api/exam/start
GET  /api/exam/{attempt_id}/questions
POST /api/exam/{attempt_id}/answer
POST /api/exam/{attempt_id}/submit
```

**Админ панель:**
```
GET    /api/admin/users
POST   /api/admin/users
GET    /api/admin/attempts
```

## 🏗 Архитектура

```
app/
├── api/         # Endpoints (роутеры)
├── core/        # Конфигурация
├── models/      # SQLAlchemy модели
├── schemas/     # Pydantic схемы
├── services/    # Бизнес-логика
└── tasks/       # Celery задачи
```

### Ключевые компоненты:

**Models:** User, Major, Subject, Question, ExamAttempt, ExamAnswer, ProctoringEvent

**Services:** auth, question, practice, exam, proctoring, redis

**Celery Tasks:** auto_finish_exam, cleanup_expired_exams, cleanup_old_attempts

## 🚢 Production деплой

### 1. SSL сертификаты

```bash
# Let's Encrypt
sudo certbot certonly --standalone -d connect-aitu.me
sudo cp /etc/letsencrypt/live/connect-aitu.me/*.pem ./ssl/
```

### 2. Настройка .env

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
CORS_ORIGINS=https://connect-aitu.me
```

### 3. Запуск

```bash
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/init_data.py
```

### 4. Мониторинг

- **Flower (Celery):** http://your-server:5555
- **Логи:** `docker-compose logs -f backend`
- **Health:** https://connect-aitu.me/health

## 📝 Разработка

### Создание миграции

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Тестирование

```bash
pytest
pytest --cov=app tests/
```

### Pre-commit

```bash
pip install pre-commit
pre-commit install
```

## 📄 Лицензия

MIT License

## 👥 Команда

Разработано с ❤️ командой Connect AITU

---

**Версия:** 1.0.0  
**Дата:** 2025-10-25
