from typing import List

from models.base import Base, TimestampMixin, bigint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.dialects.postgresql import BIGINT


# note for a Core table, we use the sqlalchemy.Column construct,
# not sqlalchemy.orm.mapped_column
thread_participants_table = Table(
    "thread_participants]",
    Base.metadata,
    Column("user_profile_id", ForeignKey("profiles.id")),
    Column("thread_id", ForeignKey("community_threads.id")),
)


class CommunityThread(TimestampMixin, Base):
    __tablename__ = "public_threads"
    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str]
    description: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True)
    posts: Mapped[List["ThreadPosts"]] = relationship(
        back_populates="thread",
        lazy="joined",
    )
    participants: Mapped[List["UserProfile"]] = relationship(
        secondary=thread_participants_table
    )
    # TODO: make this map to admin profile instead of user
    owner: Mapped["UserProfile"]
