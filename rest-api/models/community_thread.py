from typing import List

from models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Table, ForeignKey


# note for a Core table, we use the sqlalchemy.Column construct,
# not sqlalchemy.orm.mapped_column
thread_participants_table = Table(
    "thread_participants",
    Base.metadata,
    Column("user_profile_id", ForeignKey("users.id")),
    Column("thread_id", ForeignKey("community_threads.id")),
)


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
    participants: Mapped[List["Users"]] = relationship(
        secondary=thread_participants_table
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("admin_profiles.id"), unique=True)
    owner: Mapped["AdminProfile"] = relationship(
        back_populates="owned_threads", lazy="joined"
    )
