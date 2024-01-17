from datetime import datetime
from typing import Optional

from models.base import Base, TimestampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.types import Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

class ProviderProfiles(TimestampMixin, Base):
    __tablename__ = "provider_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["Users"] = relationship(
        back_populates="provider_profiles", lazy="joined"
    )
    active: Mapped[bool] = mapped_column(default=True)
    appointment_buffer_sec: Mapped[int] = mapped_column(Integer)