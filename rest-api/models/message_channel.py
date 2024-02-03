from typing import List

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin

# note for a Core table, we use the sqlalchemy.Column construct,
# not sqlalchemy.orm.mapped_column
channel_members_table = Table(
    "channel_members",
    Base.metadata,
    Column("user_profile_id", ForeignKey("users.id")),
    Column("message_channel_id", ForeignKey("message_channels.id")),
)


class MessageChannel(TimestampMixin, Base):
    __tablename__ = "message_channels"
    id: Mapped[int] = mapped_column(primary_key=True)
    active: Mapped[bool] = mapped_column(default=True)
    messages: Mapped[List["Message"]] = relationship(
        back_populates="channel",
        lazy="joined",
    )
    users: Mapped[List["Users"]] = relationship(secondary=channel_members_table)
    users_hash: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        index=True,
        unique=True,
    )
