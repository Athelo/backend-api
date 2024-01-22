from datetime import datetime
from typing import Optional

from models.base import Base, TimestampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class AppointmentStatus(enum.Enum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"


class Appointments(TimestampMixin, Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    zoom_url: Mapped[str]
    zoom_token: Mapped[str]
    status: Mapped[AppointmentStatus]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    patient_start_time: Mapped[datetime]
    provider_start_time: Mapped[datetime]