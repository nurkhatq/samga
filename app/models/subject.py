"""
Модель предмета (Subject)
Предметы: ТГО, Иностранный язык, Профильные
"""
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class SubjectType(str, PyEnum):
    """Тип предмета"""
    COMMON = "common"  # Общий (ТГО, Иностранный язык)
    PROFILE = "profile"  # Профильный


class Subject(Base, TimestampMixin):
    """Предмет"""
    
    __tablename__ = "subjects"
    
    # Код предмета (например, "TGO", "ENG", "M001_PEDAGOGY")
    code: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    
    # Название на казахском
    title_kk: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Название на русском (опционально)
    title_ru: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Тип предмета
    subject_type: Mapped[SubjectType] = mapped_column(
        SQLEnum(SubjectType, name="subject_type"),
        nullable=False,
        index=True
    )
    
    # Если профильный предмет - связь с специальностью
    major_code: Mapped[str | None] = mapped_column(
        String(10),
        ForeignKey("majors.code", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    major: Mapped["Major"] = relationship("Major", back_populates="subjects")
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="subject",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Subject(code='{self.code}', title='{self.title_kk}', type='{self.subject_type}')>"
