"""
Модель специальности (Major)
"""
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class MagistracyType(str, PyEnum):
    """Тип магистратуры"""
    PROFILE = "profile"  # Профильная
    SCIENTIFIC_PEDAGOGICAL = "scientific_pedagogical"  # Научно-педагогическая


class Major(Base, TimestampMixin):
    """Специальность для поступления в магистратуру"""
    
    __tablename__ = "majors"
    
    # Код специальности (например, "M001", "M002")
    code: Mapped[str] = mapped_column(String(10), primary_key=True, index=True)
    
    # Название на казахском
    title_kk: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Название на русском (опционально)
    title_ru: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Тип магистратуры
    magistracy_type: Mapped[MagistracyType] = mapped_column(
        SQLEnum(MagistracyType, name="magistracy_type"),
        default=MagistracyType.PROFILE,
        nullable=False
    )
    
    # Профильные предметы (categories из sorted_pairs.json)
    # Пример: ["M001 - Педагогика", "M001 - Психология"]
    categories: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    students: Mapped[list["User"]] = relationship("User", back_populates="major")
    subjects: Mapped[list["Subject"]] = relationship(
        "Subject",
        back_populates="major",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Major(code='{self.code}', title='{self.title_kk}')>"
