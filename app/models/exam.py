"""
Модели экзаменов и ответов
"""
from enum import Enum as PyEnum
from datetime import datetime
import uuid
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.db.base import Base, TimestampMixin


class ExamMode(str, PyEnum):
    """Режим экзамена"""
    PRACTICE = "practice"  # Свободный режим
    EXAM = "exam"  # Пробный экзамен


class ExamStatus(str, PyEnum):
    """Статус попытки экзамена"""
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"  # Завершен
    EXPIRED = "expired"  # Истек по времени
    CANCELLED = "cancelled"  # Отменен


class ExamAttempt(Base, TimestampMixin):
    """Попытка прохождения экзамена/практики"""
    
    __tablename__ = "exam_attempts"
    
    # UUID для безопасности
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Пользователь
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Режим
    mode: Mapped[ExamMode] = mapped_column(
        SQLEnum(ExamMode, name="exam_mode"),
        nullable=False,
        index=True
    )
    
    # Для Practice Mode - один предмет
    subject_code: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("subjects.code", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Для Exam Mode - специальность
    major_code: Mapped[str | None] = mapped_column(
        String(10),
        ForeignKey("majors.code", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Время
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Статус
    status: Mapped[ExamStatus] = mapped_column(
        SQLEnum(ExamStatus, name="exam_status"),
        default=ExamStatus.IN_PROGRESS,
        nullable=False,
        index=True
    )
    
    # Результаты
    total_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    answered_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score_percentage: Mapped[float | None] = mapped_column(nullable=True)
    
    # Прокторинг (сводка)
    proctoring_copy_paste_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    proctoring_tab_switches_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    proctoring_console_opens_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    proctoring_suspicious: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="exam_attempts")
    answers: Mapped[list["ExamAnswer"]] = relationship(
        "ExamAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan"
    )
    proctoring_events: Mapped[list["ProctoringEvent"]] = relationship(
        "ProctoringEvent",
        back_populates="attempt",
        cascade="all, delete-orphan"
    )
    
    # Индексы
    __table_args__ = (
        Index("idx_user_mode_status", "user_id", "mode", "status"),
        Index("idx_user_created", "user_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<ExamAttempt(id={self.id}, user_id={self.user_id}, mode='{self.mode}', status='{self.status}')>"


class ExamAnswer(Base, TimestampMixin):
    """Ответ студента на вопрос"""
    
    __tablename__ = "exam_answers"
    
    # ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Попытка экзамена
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Вопрос
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Ответ студента (ключи: "A", "B" или ["A", "B"] для множественного выбора)
    selected_keys: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False
    )
    
    # Правильность
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    # Время ответа
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    time_taken_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Relationships
    attempt: Mapped["ExamAttempt"] = relationship("ExamAttempt", back_populates="answers")
    question: Mapped["Question"] = relationship("Question", back_populates="answers")
    
    # Индексы
    __table_args__ = (
        Index("idx_attempt_question", "attempt_id", "question_id", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<ExamAnswer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>"
