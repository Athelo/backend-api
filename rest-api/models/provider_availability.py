from datetime import datetime, timedelta

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from zoneinfo import ZoneInfo

from models.base import Base, TimestampMixin


class ProviderAvailability(TimestampMixin, Base):
    __tablename__ = "provider_availability"
    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("provider_profiles.id"))
    provider: Mapped["ProviderProfile"] = relationship(
        back_populates="availability", lazy="joined", foreign_keys=provider_id
    )
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]

    def to_json(self, timezone: ZoneInfo = ZoneInfo("UTC")):
        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "start_time": self.start_time.astimezone(timezone),
            "end_time": self.end_time.astimezone(timezone),
        }

    def to_open_appointments_json(self, timezone: ZoneInfo) -> list[dict]:
        # Temporary - splits into 30 min chunks
        next_appt_start = self.start_time.astimezone(timezone)
        next_appt_end = self.start_time.astimezone(timezone) + timedelta(minutes=30)

        appointments = []
        while next_appt_end < self.end_time.replace(tzinfo=ZoneInfo("UTC")):
            appointments.append(next_appt_start.strftime("%m/%d/%Y %I:%M %p"))
            next_appt_start = next_appt_end
            next_appt_end = next_appt_end + timedelta(minutes=30)
        return appointments
