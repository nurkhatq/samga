# Celery команды для Connect AITU

## Запуск Celery Worker

```bash
# Простой запуск
celery -A app.tasks.celery_app worker --loglevel=info

# С указанием очередей
celery -A app.tasks.celery_app worker -Q exams,cleanup --loglevel=info

# С автоперезагрузкой (для разработки)
celery -A app.tasks.celery_app worker --loglevel=info --autoreload

# С указанием количества воркеров
celery -A app.tasks.celery_app worker --concurrency=4 --loglevel=info
```

## Запуск Celery Beat (планировщик)

```bash
# Запуск планировщика для периодических задач
celery -A app.tasks.celery_app beat --loglevel=info
```

## Запуск Worker + Beat вместе

```bash
# Для разработки (один процесс)
celery -A app.tasks.celery_app worker --beat --loglevel=info
```

## Monitoring

```bash
# Flower - веб-интерфейс для мониторинга
celery -A app.tasks.celery_app flower --port=5555

# Затем открыть: http://localhost:5555
```

## Проверка задач

```bash
# Список зарегистрированных задач
celery -A app.tasks.celery_app inspect registered

# Активные задачи
celery -A app.tasks.celery_app inspect active

# Статистика
celery -A app.tasks.celery_app inspect stats
```

## Production

Для production рекомендуется использовать supervisor или systemd:

### systemd service (celery-worker.service)

```ini
[Unit]
Description=Celery Worker для Connect AITU
After=network.target redis.service postgresql.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/connect-aitu-backend
Environment="PATH=/var/www/connect-aitu-backend/venv/bin"
ExecStart=/var/www/connect-aitu-backend/venv/bin/celery -A app.tasks.celery_app worker \
    --loglevel=info \
    --logfile=/var/log/celery/worker.log \
    --pidfile=/var/run/celery/worker.pid

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### systemd service (celery-beat.service)

```ini
[Unit]
Description=Celery Beat для Connect AITU
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/connect-aitu-backend
Environment="PATH=/var/www/connect-aitu-backend/venv/bin"
ExecStart=/var/www/connect-aitu-backend/venv/bin/celery -A app.tasks.celery_app beat \
    --loglevel=info \
    --logfile=/var/log/celery/beat.log \
    --pidfile=/var/run/celery/beat.pid

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Управление сервисами

```bash
# Включить автозапуск
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat

# Запустить
sudo systemctl start celery-worker
sudo systemctl start celery-beat

# Проверить статус
sudo systemctl status celery-worker
sudo systemctl status celery-beat

# Перезапустить
sudo systemctl restart celery-worker
sudo systemctl restart celery-beat

# Логи
sudo journalctl -u celery-worker -f
sudo journalctl -u celery-beat -f
```

## Docker

Для Docker используйте отдельные контейнеры:

```yaml
services:
  celery-worker:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres
    environment:
      - DATABASE_URL=...
      - REDIS_URL=...
  
  celery-beat:
    build: .
    command: celery -A app.tasks.celery_app beat --loglevel=info
    depends_on:
      - redis
    environment:
      - REDIS_URL=...
```

## Полезные команды

```bash
# Очистить все задачи из очереди
celery -A app.tasks.celery_app purge

# Остановить все воркеры
celery -A app.tasks.celery_app control shutdown

# Перезапустить воркеры (без потери задач)
celery -A app.tasks.celery_app control pool_restart
```
