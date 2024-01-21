from typing import List

from sqlalchemy import ForeignKey

from models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Message(TimestampMixin, Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("message_channels.id"), nullable=False
    )
    channel: Mapped["MessageChannel"] = relationship(
        back_populates="messages",
        lazy="joined",
    )
