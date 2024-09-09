from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func
from datetime import datetime
from app.config.database import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.episodes import Episode

class Progress(Base):
    __tablename__ = "       progress"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Reading details
    juz: Mapped[int] = mapped_column(nullable=False)
    chapter: Mapped[int] = mapped_column(nullable=False)
    verse: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=True)  # If you want to store the text content

    page: Mapped[int] = mapped_column(nullable=False)
    submission_time: Mapped[datetime] = mapped_column(default=func.now())

    # Progress details
    juz_required: Mapped[int] = mapped_column(default=lambda context: context.get_current_parameters()['juz'])  # Amount of Juz required for this submission
    juz_readed: Mapped[int] = mapped_column(nullable=False, default=0)  # Amount of Juz read during this submission
    remained: Mapped[int] = mapped_column(nullable=True, default=0)  # Remaining verses or pages in the current Juz/chapter

    state: Mapped[str] = mapped_column(nullable=False, default='active')  # State of the reading (e.g., 'active', 'remediant', "droped")
    xp: Mapped[int] = mapped_column(nullable=False, default=0)  # XP of the user
    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    episode_id: Mapped[int] = mapped_column(ForeignKey("episodes.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reading_progresses")
    episode: Mapped["Episode"] = relationship("Episode", back_populates="reading_progresses")
