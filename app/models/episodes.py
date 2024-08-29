from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func
from datetime import datetime
from app.config.database import Base

if TYPE_CHECKING:
    from app.models.users import User

class Episode(Base):
    __tablename__ = "episodes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    juz: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    no_of_khatmis: Mapped[int] = mapped_column(default=0)
    progress: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    is_full: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="episodes")
    members: Mapped[List["Member"]] = relationship("Member", back_populates="episode")

class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    episode_id: Mapped[int] = mapped_column(ForeignKey("episodes.id"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="members")
    episode: Mapped["Episode"] = relationship("Episode", back_populates="members")
