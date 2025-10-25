"""
Модель специальности (Major) - ИСПРАВЛЕННАЯ
"""
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base, TimestampMixin


class MagistracyType(str, PyEnum):
    """Тип магистратуры"""
    PROFILE = "profile"
    SCIENTIFIC_PEDAGOGICAL = "scientific_pedagogical"


class Major(Base, TimestampMixin):
    """Специальность для поступления в магистратуру"""
    
    __tablename__ = "majors"
    
    code: Mapped[str] = mapped_column(String(10), primary_key=True, index=True)
    title_kk: Mapped[str] = mapped_column(String(500), nullable=False)
    title_ru: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # ВАЖНО: values_callable для правильной работы str enum!
    magistracy_type: Mapped[str] = mapped_column(
        SQLEnum(MagistracyType, values_callable=lambda x: [e.value for e in x]),
        default="profile",
        nullable=False
    )
    
    # JSONB вместо JSON
    categories: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    students: Mapped[list["User"]] = relationship("User", back_populates="major")
    subjects: Mapped[list["Subject"]] = relationship(
        "Subject",
        back_populates="major",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Major(code='{self.code}', title='{self.title_kk}')>"