from datetime import datetime
from typing import Optional
from typing import List
from models.base import Base, TimestampMixin
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.types import Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ProviderProfile(TimestampMixin, Base):
    __tablename__ = "provider_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["Users"] = relationship(
        back_populates="provider_profile", lazy="joined", single_parent=True
    )
    active: Mapped[bool] = mapped_column(default=True)
    appointment_buffer_sec: Mapped[int] = mapped_column(Integer())
    appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="provider",
        lazy="joined",
    )
