from datetime import datetime
from typing import Optional

from models.base import Base, TimestampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserSymptom(TimestampMixin, Base):
    __tablename__ = "user_symptoms"
    id: Mapped[int] = mapped_column(primary_key=True)
    occurrence_date: Mapped[datetime] = mapped_column(index=True)
    users_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    users: Mapped["Users"] = relationship(
        back_populates="user_symptoms", lazy="joined"
    )
    note: Mapped[str] = mapped_column(nullable=True)
    symptom_id: Mapped[int] = mapped_column(ForeignKey("symptoms.id"))
    symptom: Mapped["Symptom"] = relationship(single_parent=True)
