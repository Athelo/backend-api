from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class ZoomMeeting(TimestampMixin, Base):
    __tablename__ = "zoom_meetings"
    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"))
    appointment: Mapped["Appointment"] = relationship(
        back_populates="zoom_meeting", lazy="joined", foreign_keys=appointment_id
    )
    zoom_host_url: Mapped[str] = mapped_column(nullable=True)
    zoom_join_url: Mapped[str] = mapped_column(nullable=True)
