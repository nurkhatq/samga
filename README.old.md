# 🎓 Connect AITU - Backend API

Платформа для подготовки к экзаменам в магистратуру Казахстана.

## 🚀 Особенности

- **FastAPI** - современный async Python framework
- **PostgreSQL** - надежное хранение данных
- **Redis** - кеширование, сессии, прокторинг
- **Celery** - фоновые задачи (автозавершение экзаменов)
- **JWT** - безопасная авторизация
- **Docker Compose** - легкий деплой

## 🔒 Безопасность

- ✅ Правильные ответы НИКОГДА не отправляются на фронт
- ✅ Проверка ответов только на бекенде
- ✅ Rate limiting (защита от DDoS)
- ✅ Прокторинг (отслеживание подозрительных действий)
- ✅ JWT с refresh tokens
- ✅ Bcrypt для паролей

## 📦 Установка

### Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo>
cd connect-aitu-backend

# 2. Создать .env файл
cp .env.example .env
# Отредактировать .env

# 3. Запустить все сервисы
docker-compose up -d

# 4. Применить миграции
docker-compose exec backend alembic upgrade head

# 5. Создать админа
docker-compose exec backend python -m app.scripts.create_admin

# 6. Импортировать данные (если есть)
docker-compose exec backend python -m app.scripts.import_data
```

API доступен на `http://localhost:8000`
Документация: `http://localhost:8000/docs`

### Локальная разработка

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запустить только базы данных
docker-compose up -d postgres redis rabbitmq

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# В отдельном терминале запустить Celery
celery -A app.celery_app worker --loglevel=info
```

## 📁 Структура проекта

```
connect-aitu-backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # Авторизация
│   │   ├── students.py   # Студенты
│   │   ├── practice.py   # Свободный режим
│   │   ├── exam.py       # Экзамены
│   │   └── admin.py      # Админ панель
│   ├── core/             # Ядро приложения
│   │   ├── config.py     # Конфигурация
│   │   ├── security.py   # JWT, bcrypt
│   │   └── deps.py       # Зависимости FastAPI
│   ├── models/           # SQLAlchemy модели
│   │   ├── user.py
│   │   ├── major.py
│   │   ├── subject.py
│   │   ├── question.py
│   │   ├── exam.py
│   │   └── proctoring.py
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   │   ├── auth.py
│   │   ├── practice.py
│   │   ├── exam.py
│   │   └── proctoring.py
│   ├── db/               # База данных
│   │   ├── base.py
│   │   └── session.py
│   ├── tasks/            # Celery задачи
│   ├── scripts/          # Вспомогательные скрипты
│   └── main.py           # Главный файл
├── alembic/              # Миграции БД
├── tests/                # Тесты
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 🔑 API Endpoints

### Авторизация
- `POST /api/auth/login` - Вход
- `POST /api/auth/refresh` - Обновить токен
- `POST /api/auth/logout` - Выход

### Студент
- `GET /api/majors` - Список специальностей
- `GET /api/subjects` - Список предметов
- `GET /api/stats/my` - Моя статистика

### Свободный режим (Practice)
- `POST /api/practice/start` - Начать практику
- `GET /api/practice/{subject_code}/questions` - Получить вопросы (пагинация)
- `POST /api/practice/submit-answer` - Ответить (с мгновенной проверкой)
- `POST /api/practice/finish` - Завершить практику

### Экзамен (Exam)
- `POST /api/exam/start` - Начать экзамен
- `GET /api/exam/{attempt_id}` - Текущее состояние
- `POST /api/exam/{attempt_id}/answer` - Ответить (БЕЗ проверки)
- `POST /api/exam/{attempt_id}/submit` - Завершить экзамен
- `POST /api/exam/{attempt_id}/proctoring` - Событие прокторинга

### Админ
- `POST /api/admin/users` - Создать пользователя
- `GET /api/admin/users` - Список пользователей
- `GET /api/admin/attempts` - Все попытки экзаменов
- `POST /api/admin/questions/import` - Импорт вопросов

## 🗄️ База данных

### Основные таблицы
- **users** - Пользователи
- **majors** - Специальности (M001-M153+)
- **subjects** - Предметы (ТГО, АНГЛ, профильные)
- **questions** - Вопросы с вариантами
- **exam_attempts** - Попытки экзаменов
- **exam_answers** - Ответы студентов
- **proctoring_events** - События прокторинга

## 📊 Redis структура

```python
# Активная попытка экзамена
exam:attempt:{attempt_id} = {...}
TTL: время экзамена + 1 час

# Прогресс в Practice Mode
practice:{user_id}:{subject_code} = {...}
TTL: 7 дней

# Rate limiting
rate_limit:{user_id}:api = количество
TTL: 1 минута
```

## 🔧 Переменные окружения

См. `.env.example`

## 🚀 Деплой на production

```bash
# На сервере
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build

# Применить миграции
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## 📝 Лицензия

Proprietary - все права защищены.
