from datetime import datetime
from typing import Optional

from models.base import Base, TimestampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserSymptom(TimestampMixin, Base):
    __tablename__ = "user_symptoms"
    id: Mapped[int] = mapped_column(primary_key=True)
    occurrence_date: Mapped[datetime] = mapped_column(index=True)
    user_profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    user_profile: Mapped["UserProfile"] = relationship(back_populates="user_symptoms")
    note: Mapped[str] = mapped_column(nullable=True)
    symptom_id: Mapped[int] = mapped_column(ForeignKey("symptoms.id"))
    symptom: Mapped["Symptom"] = relationship(single_parent=True)
