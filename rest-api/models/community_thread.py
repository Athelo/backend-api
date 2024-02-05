from typing import List

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


# created as a class so we can query it easier
class ThreadParticipants(Base):
    __tablename__ = "thread_participants"
    user_profile_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    thread_id: Mapped[int] = mapped_column(ForeignKey("community_threads.id"))
    __table_args__ = (UniqueConstraint("user_profile_id", "thread_id"),)
    __mapper_args__ = {"primary_key": [user_profile_id, thread_id]}


class CommunityThread(TimestampMixin, Base):
    __tablename__ = "community_threads"
    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str]
    description: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True)
    posts: Mapped[List["ThreadPost"]] = relationship(
        back_populates="thread",
        lazy="joined",
    )
    participants: Mapped[List["Users"]] = relationship(secondary="thread_participants")
    owner_id: Mapped[int] = mapped_column(ForeignKey("admin_profiles.id"), unique=False)
    owner: Mapped["AdminProfile"] = relationship(
        back_populates="owned_threads", lazy="joined"
    )
