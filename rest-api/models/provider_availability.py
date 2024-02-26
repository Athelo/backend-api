from datetime import datetime, timedelta

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from zoneinfo import ZoneInfo

from api.constants import DATETIME_FORMAT, DEFAULT_DELAY_IN_MINUTES
from models.base import Base, TimestampMixin
from flask import current_app as app

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

    def to_open_appointments_json(self, timezone: ZoneInfo, blocked_times: set) -> list[dict]:
        # Temporary - splits into 30 min chunks
        # Add buffer from current time
        thirty_minutes_from_now = datetime.utcnow() + timedelta(minutes=DEFAULT_DELAY_IN_MINUTES)
        next_appt_start = max(self.start_time, thirty_minutes_from_now)
        next_appt_start = round_to_next_thirty(next_appt_start)
        next_appt_end = next_appt_start + timedelta(minutes=DEFAULT_DELAY_IN_MINUTES)

        appointments = []
        while next_appt_end <= self.end_time:
            if next_appt_end.strftime(DATETIME_FORMAT) in blocked_times:
                next_appt_end = next_appt_end + timedelta(minutes= 2 * DEFAULT_DELAY_IN_MINUTES)
            elif next_appt_start.strftime(DATETIME_FORMAT) in blocked_times:
                next_appt_end = next_appt_end + timedelta(minutes=DEFAULT_DELAY_IN_MINUTES)
            else:
                appointments.append(next_appt_start.astimezone(timezone).strftime("%m/%d/%Y %I:%M %p"))
            next_appt_start = next_appt_end
            next_appt_end = next_appt_end + timedelta(minutes=DEFAULT_DELAY_IN_MINUTES)
        return appointments

def round_to_next_thirty(timestamp: datetime):
    if timestamp.minute == 0 or timestamp.minute == 30:
        return timestamp
    
    delta = 0
    if timestamp.minute > 0 and timestamp.minute < 30:
        delta = 30 - timestamp.minute
    if timestamp.minute > 30 and timestamp.minute < 60:
        delta = 60 - timestamp.minute
    timestamp += timedelta(minutes=delta)

    return timestamp
