import enum

from datetime import datetime

from models.base import Base, TimestampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AppointmentStatus(enum.Enum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"


class VideoType(enum.Enum):
    VONAGE = "VONAGE"
    ZOOM = "ZOOM"
    NOT_CONFIGURED = "NOT_CONFIGURED"


class Appointment(TimestampMixin, Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient_profiles.id"))
    patient: Mapped["PatientProfile"] = relationship(
        back_populates="appointments", lazy="joined", foreign_keys=patient_id
    )
    provider_id: Mapped[int] = mapped_column(ForeignKey("provider_profiles.id"))
    provider: Mapped["ProviderProfile"] = relationship(
        back_populates="appointments", lazy="joined", foreign_keys=provider_id
    )
    zoom_host_url: Mapped[str] = mapped_column(nullable=True)
    zoom_join_url: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[AppointmentStatus]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    patient_start_time: Mapped[datetime] = mapped_column(nullable=True)
    provider_start_time: Mapped[datetime] = mapped_column(nullable=True)
    zoom_meeting: Mapped["ZoomMeeting"] = relationship(
        back_populates="appointment",
        lazy="joined",
    )
    vonage_session: Mapped["VonageSession"] = relationship(
        back_populates="appointment", lazy="joined"
    )

    # leaving off return type to avoid circular imports
    def get_patient_user(self):
        return self.patient.user

    # leaving off return type to avoid circular imports
    def get_provider_user(self):
        return self.provider.user

    def to_legacy_json(self) -> dict:
        return {
            "provider": {
                "display_name": self.provider.user.display_name,
                "photo": "",
            },
            "patient": {"display_name": self.patient.user.display_name, "photo": ""},
            "start_time": self.start_time,
            "end_time": self.end_time,
            "zoom_join_url": self.zoom_host_url,
            "zoom_host_url": self.zoom_join_url,
        }

    @property
    def is_zoom_appointment(self):
        return self.zoom_meeting is not None

    @property
    def is_vonage_appointment(self):
        return self.vonage_session is not None

    @property
    def video_call_type(self) -> VideoType:
        if self.vonage_session is not None:
            return VideoType.VONAGE
        if self.zoom_meeting is not None:
            return VideoType.ZOOM
        return VideoType.NOT_CONFIGURED
