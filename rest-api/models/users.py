from typing import List
from models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Users(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    test: Mapped[str] 
    first_name: Mapped[str]
    last_name: Mapped[str]
    display_name: Mapped[str]
    email: Mapped[str] = mapped_column(index=True, unique=True)
    active: Mapped[bool] = mapped_column(default=True)
    birthday: Mapped[str] = mapped_column(default="")
    phone: Mapped[str] = mapped_column(default="")
    patient_feelings: Mapped[List["PatientFeelings"]] = relationship(
        back_populates="users", lazy="joined"
    )
    patient_symptoms: Mapped[List["PatientSymptoms"]] = relationship(
        back_populates="users", lazy="joined"
    )
    saved_content: Mapped[List["SavedContent"]] = relationship(
        back_populates="users", lazy="joined"
    )
    patient_profiles: Mapped["PatientProfiles"] = relationship(
        "PatientProfiles", back_populates="user", uselist=False, lazy="joined"
    )
    admin_profiles: Mapped["AdminProfiles"] = relationship(
        "AdminProfiles", back_populates="user", uselist=False, lazy="joined"
    )
    caregiver_profiles: Mapped["CaregiverProfiles"] = relationship(
        "CaregiverProfiles", back_populates="user", uselist=False, lazy="joined"
    )
    provider_profiles: Mapped["ProviderProfiles"] = relationship(
        "ProviderProfiles", back_populates="user", uselist=False, lazy="joined"
    )