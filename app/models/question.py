"""
Модель вопроса (Question)
"""
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, JSON, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

from app.db.base import Base, TimestampMixin


class QuestionDifficulty(str, PyEnum):
    """Сложность вопроса"""
    A = "A"  # Легкий
    B = "B"  # Средний
    C = "C"  # Сложный


class QuestionType(str, PyEnum):
    """Тип вопроса"""
    SINGLE = "single"  # Один правильный ответ
    MULTIPLE = "multiple"  # Несколько правильных ответов


class Question(Base, TimestampMixin):
    """Вопрос"""
    
    __tablename__ = "questions"
    
    # UUID для безопасности (не последовательный ID)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Предмет
    subject_code: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("subjects.code", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Текст вопроса
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Варианты ответа (JSON)
    # Пример: [{"key": "A", "text": "Вариант А", "is_correct": true}, ...]
    # ВАЖНО: is_correct НЕ отправляется на фронт!
    options: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    
    # Сложность
    difficulty: Mapped[QuestionDifficulty] = mapped_column(
        SQLEnum(QuestionDifficulty, name="question_difficulty"),
        default=QuestionDifficulty.A,
        nullable=False,
        index=True
    )
    
    # Тип вопроса
    question_type: Mapped[QuestionType] = mapped_column(
        SQLEnum(QuestionType, name="question_type"),
        default=QuestionType.SINGLE,
        nullable=False
    )
    
    # Баллы за правильный ответ
    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Время на ответ (секунды)
    time_seconds: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    
    # Объяснение правильного ответа (опционально)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Теги для категоризации
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    
    # Метаданные (например, source_question_number из импорта)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    # Relationships
    subject: Mapped["Subject"] = relationship("Subject", back_populates="questions")
    answers: Mapped[list["ExamAnswer"]] = relationship(
        "ExamAnswer",
        back_populates="question",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Question(id={self.id}, subject='{self.subject_code}', difficulty='{self.difficulty}')>"
    
    def to_safe_dict(self) -> dict:
        """
        Безопасное представление вопроса БЕЗ правильных ответов
        Используется для отправки на фронт
        """
        return {
            "id": str(self.id),
            "question_text": self.question_text,
            "options": [
                {"key": opt["key"], "text": opt["text"]}
                for opt in self.options
            ],
            "difficulty": self.difficulty.value,
            "question_type": self.question_type.value,
            "time_seconds": self.time_seconds,
        }
    
    def get_correct_keys(self) -> list[str]:
        """Получить список правильных ответов"""
        return [opt["key"] for opt in self.options if opt.get("is_correct")]
