"""
Redis сервис для кеширования, сессий экзаменов и rate limiting
"""
import json
from typing import Any
from datetime import timedelta
import redis.asyncio as redis

from app.core.config import settings


class RedisService:
    """Сервис для работы с Redis"""
    
    def __init__(self):
        self.redis: redis.Redis | None = None
    
    async def connect(self):
        """Подключение к Redis"""
        self.redis = redis.from_url(
            str(settings.REDIS_URL),
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Отключение от Redis"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Any | None:
        """Получить значение по ключу"""
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: int | timedelta | None = None
    ) -> bool:
        """
        Установить значение
        
        Args:
            key: Ключ
            value: Значение (будет сериализовано в JSON)
            expire: Время жизни (секунды или timedelta)
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        if isinstance(expire, timedelta):
            expire = int(expire.total_seconds())
        
        return await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> int:
        """Удалить ключ"""
        return await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        return await self.redis.exists(key) > 0
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Увеличить значение"""
        return await self.redis.incrby(key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Установить TTL для ключа"""
        return await self.redis.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """Получить TTL ключа"""
        return await self.redis.ttl(key)
    
    # ===================================
    # Practice Mode
    # ===================================
    
    async def get_practice_progress(self, user_id: int, subject_code: str) -> dict | None:
        """Получить прогресс в свободном режиме"""
        key = f"practice:{user_id}:{subject_code}"
        return await self.get(key)
    
    async def save_practice_progress(
        self,
        user_id: int,
        subject_code: str,
        progress: dict
    ) -> bool:
        """
        Сохранить прогресс в свободном режиме
        
        Args:
            progress: {
                "answered_questions": [uuid1, uuid2, ...],
                "correct_count": 15,
                "total_count": 20,
                "last_offset": 20
            }
        """
        key = f"practice:{user_id}:{subject_code}"
        ttl_days = settings.PRACTICE_SESSION_TTL_DAYS
        return await self.set(key, progress, expire=timedelta(days=ttl_days))
    
    async def delete_practice_progress(self, user_id: int, subject_code: str) -> int:
        """Удалить прогресс в свободном режиме"""
        key = f"practice:{user_id}:{subject_code}"
        return await self.delete(key)
    
    # ===================================
    # Exam Session
    # ===================================
    
    async def get_exam_session(self, attempt_id: str) -> dict | None:
        """
        Получить сессию экзамена
        
        Returns:
            {
                "user_id": 1,
                "started_at": "2025-10-25T10:00:00Z",
                "questions": ["uuid1", "uuid2", ...],
                "answers": {"uuid1": ["A"], "uuid2": ["B"]},
                "time_remaining": 5400,
                "proctoring": {
                    "copy_paste": 0,
                    "tab_switches": 0,
                    "console_opens": 0
                }
            }
        """
        key = f"exam:attempt:{attempt_id}"
        return await self.get(key)
    
    async def save_exam_session(
        self,
        attempt_id: str,
        session_data: dict,
        expire_seconds: int | None = None
    ) -> bool:
        """Сохранить сессию экзамена"""
        key = f"exam:attempt:{attempt_id}"
        if expire_seconds is None:
            expire_seconds = settings.EXAM_SESSION_TTL_HOURS * 3600
        return await self.set(key, session_data, expire=expire_seconds)
    
    async def update_exam_answer(
        self,
        attempt_id: str,
        question_id: str,
        selected_keys: list[str]
    ) -> bool:
        """Обновить ответ в сессии экзамена"""
        session = await self.get_exam_session(attempt_id)
        if not session:
            return False
        
        if "answers" not in session:
            session["answers"] = {}
        
        session["answers"][question_id] = selected_keys
        return await self.save_exam_session(attempt_id, session)
    
    async def increment_proctoring_event(
        self,
        attempt_id: str,
        event_type: str
    ) -> bool:
        """Увеличить счетчик события прокторинга в сессии"""
        session = await self.get_exam_session(attempt_id)
        if not session:
            return False
        
        if "proctoring" not in session:
            session["proctoring"] = {
                "copy_paste": 0,
                "tab_switches": 0,
                "console_opens": 0
            }
        
        # Маппинг типов событий на счетчики
        event_mapping = {
            "copy": "copy_paste",
            "paste": "copy_paste",
            "cut": "copy_paste",
            "tab_switch": "tab_switches",
            "window_blur": "tab_switches",
            "console_open": "console_opens",
        }
        
        counter_key = event_mapping.get(event_type)
        if counter_key and counter_key in session["proctoring"]:
            session["proctoring"][counter_key] += 1
        
        return await self.save_exam_session(attempt_id, session)
    
    async def delete_exam_session(self, attempt_id: str) -> int:
        """Удалить сессию экзамена"""
        key = f"exam:attempt:{attempt_id}"
        return await self.delete(key)
    
    # ===================================
    # Rate Limiting
    # ===================================
    
    async def check_rate_limit(
        self,
        user_id: int,
        endpoint: str = "api",
        max_requests: int | None = None,
        window_seconds: int = 60
    ) -> tuple[bool, int]:
        """
        Проверить rate limit
        
        Args:
            user_id: ID пользователя
            endpoint: Название endpoint
            max_requests: Максимум запросов (None = из settings)
            window_seconds: Окно времени в секундах
        
        Returns:
            (allowed, remaining): разрешен ли запрос и сколько осталось
        """
        if max_requests is None:
            max_requests = settings.RATE_LIMIT_PER_MINUTE
        
        key = f"rate_limit:{user_id}:{endpoint}"
        
        # Получаем текущее количество запросов
        current = await self.redis.get(key)
        
        if current is None:
            # Первый запрос в окне
            await self.redis.set(key, 1, ex=window_seconds)
            return True, max_requests - 1
        
        current = int(current)
        
        if current >= max_requests:
            # Превышен лимит
            ttl = await self.ttl(key)
            return False, 0
        
        # Увеличиваем счетчик
        await self.redis.incr(key)
        return True, max_requests - current - 1
    
    # ===================================
    # Caching
    # ===================================
    
    async def cache_get(self, cache_key: str) -> Any | None:
        """Получить из кеша"""
        return await self.get(f"cache:{cache_key}")
    
    async def cache_set(
        self,
        cache_key: str,
        value: Any,
        expire_seconds: int = 3600
    ) -> bool:
        """Сохранить в кеш"""
        return await self.set(f"cache:{cache_key}", value, expire=expire_seconds)
    
    async def cache_delete(self, cache_key: str) -> int:
        """Удалить из кеша"""
        return await self.delete(f"cache:{cache_key}")


# Создаем глобальный экземпляр
redis_service = RedisService()
