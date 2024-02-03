from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class AdminProfile(TimestampMixin, Base):
    __tablename__ = "admin_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["Users"] = relationship(
        back_populates="admin_profile", lazy="joined", single_parent=True
    )
    active: Mapped[bool] = mapped_column(default=True)
    owned_threads: Mapped[List["CommunityThread"]] = relationship(
        back_populates="owner"
    )
