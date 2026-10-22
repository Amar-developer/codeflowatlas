from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    repository_url: Mapped[str] = mapped_column(String(600), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(100), nullable=False)
    repository_name: Mapped[str] = mapped_column(String(100), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    analyzer_version: Mapped[str] = mapped_column(String(30), nullable=False)
    warnings: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class ProjectEndpoint(Base):
    __tablename__ = "project_endpoints"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    path: Mapped[str] = mapped_column(String(1000), nullable=False)
    handler: Mapped[str] = mapped_column(String(500), nullable=False)
    source_file: Mapped[str] = mapped_column(String(1500), nullable=False)
    source_line: Mapped[int] = mapped_column(Integer, nullable=False)