from app.config.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import func
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.episodes import Episode

class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    episode_id: Mapped[int] = mapped_column(ForeignKey("episodes.id"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(default=func.now())
    is_active: Mapped[bool] = mapped_column(default=True)
    is_full: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship("User", back_populates="members")
    episode: Mapped["Episode"] = relationship("Episode", back_populates="members")
