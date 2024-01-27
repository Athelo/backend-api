from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class ChannelType(Enum):
    DM = "DM"
    COMMUNITY = "COMMUNITY"


class WebSocketSession(TimestampMixin, Base):
    __tablename__ = "websocket_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    session_id: Mapped[str] = mapped_column(nullable=False)
    channel_type: Mapped(ChannelType) = mapped_column(nullable=False)
    channel_id: Mapped[int] = mapped_column(nullable=False)
