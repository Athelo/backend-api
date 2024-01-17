import enum

from datetime import datetime
from typing import Optional

from models.base import Base, TimestampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.types import Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

class CancerStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    REMISSION = "REMISSION"

class PatientProfiles(TimestampMixin, Base):
    __tablename__ = "patient_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["Users"] = relationship(
        back_populates="user_feelings", lazy="joined"
    )
    active: Mapped[bool] = mapped_column(default=True)
    cancer_status: Mapped[CancerStatus]