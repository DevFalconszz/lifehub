import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base, BaseModelMixin


class Project(Base, BaseModelMixin):
    __tablename__ = 'projects'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default='active', nullable=False,
    )
    priority: Mapped[str] = mapped_column(
        String(10), default='medium', nullable=False,
    )
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    start_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    target_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True,
    )

    tasks: Mapped[list['Task']] = relationship(
        'Task', back_populates='project', cascade='all, delete-orphan',
    )

    __table_args__ = (
        CheckConstraint("status IN ('active', 'paused', 'completed', 'archived')"),
        CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')"),
        CheckConstraint("progress >= 0 AND progress <= 100"),
    )


class Task(Base, BaseModelMixin):
    __tablename__ = 'tasks'

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default='todo', nullable=False,
    )
    priority: Mapped[str] = mapped_column(
        String(10), default='medium', nullable=False,
    )
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('projects.id', ondelete='SET NULL'),
        nullable=True, index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True,
    )

    project: Mapped[Project | None] = relationship(
        'Project', back_populates='tasks',
    )

    __table_args__ = (
        CheckConstraint("status IN ('todo', 'in_progress', 'done', 'cancelled')"),
        CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')"),
    )
