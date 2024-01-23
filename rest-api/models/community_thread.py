from typing import List

from models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as postgres_UUID
from uuid import uuid4, UUID


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
    owner_id: Mapped[int] = mapped_column(ForeignKey("admin_profiles.id"), unique=True)
    owner: Mapped["AdminProfile"] = relationship(
        back_populates="owned_threads", lazy="joined"
    )
    chat_room_id: Mapped[UUID] = mapped_column(
        postgres_UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )