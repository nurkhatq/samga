"""
Модель пользователя (User)
"""
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserRole(str, PyEnum):
    """Роли пользователей"""
    STUDENT = "student"
    ADMIN = "admin"
    MODERATOR = "moderator"


class User(Base, TimestampMixin):
    """Пользователь системы"""
    
    __tablename__ = "users"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Роль
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        default=UserRole.STUDENT,
        nullable=False,
        index=True
    )
    
    # Специальность (только для студентов)
    major_code: Mapped[str | None] = mapped_column(
        String(10),
        ForeignKey("majors.code", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    major: Mapped["Major"] = relationship("Major", back_populates="students")
    exam_attempts: Mapped[list["ExamAttempt"]] = relationship(
        "ExamAttempt",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
