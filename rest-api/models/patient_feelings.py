from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class PatientFeelings(TimestampMixin, Base):
    __tablename__ = "patient_feelings"
    id: Mapped[int] = mapped_column(primary_key=True)
    occurrence_date: Mapped[datetime] = mapped_column(index=True)
    user_profile_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    users: Mapped["Users"] = relationship(
        back_populates="patient_feelings", lazy="joined"
    )
    note: Mapped[str] = mapped_column(nullable=True)
    general_feeling: Mapped[int] = mapped_column(nullable=True)
