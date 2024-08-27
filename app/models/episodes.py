from typing import TYPE_CHECKING
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
    members_no: Mapped[int] = mapped_column(default=0)
    description: Mapped[str] = mapped_column(nullable=False)
    no_of_khatmis: Mapped[int] = mapped_column(default=0)
    progress: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    is_active: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="episodes")
