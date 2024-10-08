import enum
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class CancerStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    REMISSION = "REMISSION"


class PatientProfile(TimestampMixin, Base):
    __tablename__ = "patient_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["Users"] = relationship(
        back_populates="patient_profile", lazy="joined", single_parent=True
    )
    active: Mapped[bool] = mapped_column(default=True)
    cancer_status: Mapped[CancerStatus]
    appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="patient",
        lazy="joined",
    )
