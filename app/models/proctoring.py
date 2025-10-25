"""
Модель прокторинга (отслеживание подозрительных действий)
"""
from enum import Enum as PyEnum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SQLEnum, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class ProctoringEventType(str, PyEnum):
    """Тип события прокторинга"""
    COPY = "copy"  # Копирование
    PASTE = "paste"  # Вставка
    CUT = "cut"  # Вырезание
    TAB_SWITCH = "tab_switch"  # Переключение вкладки/окна
    WINDOW_BLUR = "window_blur"  # Потеря фокуса
    FULLSCREEN_EXIT = "fullscreen_exit"  # Выход из полноэкранного режима
    CONTEXT_MENU = "context_menu"  # Открытие контекстного меню
    CONSOLE_OPEN = "console_open"  # Открытие консоли разработчика
    RIGHT_CLICK = "right_click"  # Правый клик мыши


class ProctoringEvent(Base):
    """События прокторинга"""
    
    __tablename__ = "proctoring_events"
    
    # ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Попытка экзамена
    attempt_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Тип события
    event_type: Mapped[ProctoringEventType] = mapped_column(
        SQLEnum(ProctoringEventType, name="proctoring_event_type"),
        nullable=False,
        index=True
    )
    
    # Время события
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Дополнительные данные (JSON)
    # Например: {"text_length": 100, "source": "keyboard"}
    product_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    # Relationships
    attempt: Mapped["ExamAttempt"] = relationship("ExamAttempt", back_populates="proctoring_events")
    
    # Индексы
    __table_args__ = (
        Index("idx_attempt_timestamp", "attempt_id", "timestamp"),
        Index("idx_attempt_event_type", "attempt_id", "event_type"),
    )
    
    def __repr__(self) -> str:
        return f"<ProctoringEvent(id={self.id}, type='{self.event_type}', attempt_id={self.attempt_id})>"
