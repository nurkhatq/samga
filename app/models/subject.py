"""
Модель предмета (Subject) - ИСПРАВЛЕННАЯ
"""
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class SubjectType(str, PyEnum):
    """Тип предмета"""
    COMMON = "common"
    PROFILE = "profile"


class Subject(Base, TimestampMixin):
    """Предмет"""
    
    __tablename__ = "subjects"
    
    code: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    title_kk: Mapped[str] = mapped_column(String(500), nullable=False)
    title_ru: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # ВАЖНО: values_callable для правильной работы str enum!
    subject_type: Mapped[str] = mapped_column(
        SQLEnum(SubjectType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )
    
    major_code: Mapped[str | None] = mapped_column(
        String(10),
        ForeignKey("majors.code", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    major: Mapped["Major"] = relationship("Major", back_populates="subjects")
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="subject",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Subject(code='{self.code}', title='{self.title_kk}', type='{self.subject_type}')>"