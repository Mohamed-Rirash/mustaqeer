from sqlalchemy.orm import mapped_column, Mapped , relationship
from sqlalchemy import func, ForeignKey
from typing import TYPE_CHECKING
from datetime import datetime
from app.config.database import Base

if TYPE_CHECKING:
    from app.models.episodes import Episode, Member

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True , index=True , autoincrement=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    profile_image: Mapped[str] = mapped_column(nullable=True)
    points: Mapped[int] = mapped_column(default=0)
    no_of_khatmis: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=False)
    verified_at: Mapped[datetime] = mapped_column(nullable=True,default=None)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    is_firstlogin: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    members: Mapped[list["Member"]] = relationship("Member", back_populates="user")

    user_tokens: Mapped[list["UserToken"]] = relationship("UserToken", back_populates="user")
    episodes: Mapped[list["Episode"]] = relationship("Episode", back_populates="user")

    def get_context_string(self, context: str):
        return f"{context}{self.password[-6:]}{self.updated_at.strftime('%m%d%Y%H%M%S')}".strip()


class UserToken(Base):
    __tablename__ = "user_tokens"

    id: Mapped[int] = mapped_column(primary_key=True , index=True , autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    access_token: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    expires_at: Mapped[datetime] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_tokens")
