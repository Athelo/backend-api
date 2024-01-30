from models.base import Base, TimestampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class VonageSession(TimestampMixin, Base):
    __tablename__ = "vonage_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"))
    appointment: Mapped["Appointment"] = relationship(
        back_populates="vonage_session", lazy="joined", foreign_keys=appointment_id
    )
    session_id: Mapped[str] = mapped_column(nullable=False)
