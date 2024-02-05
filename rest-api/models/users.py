from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class Users(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
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
    patient_profile: Mapped["PatientProfile"] = relationship(
        "PatientProfile", back_populates="user", uselist=False, lazy="joined"
    )
    admin_profile: Mapped["AdminProfile"] = relationship(
        "AdminProfile", back_populates="user", uselist=False, lazy="joined"
    )
    caregiver_profile: Mapped["CaregiverProfile"] = relationship(
        "CaregiverProfile", back_populates="user", uselist=False, lazy="joined"
    )
    provider_profile: Mapped["ProviderProfile"] = relationship(
        back_populates="user", uselist=False, lazy="joined"
    )

    @property
    def is_patient(self) -> bool:
        return self.patient_profile is not None and self.patient_profile.active

    @property
    def is_provider(self) -> bool:
        return self.provider_profile is not None and self.provider_profile.active

    @property
    def is_admin(self) -> bool:
        return self.admin_profile is not None and self.admin_profile.active

    @property
    def is_caregiver(self) -> bool:
        return self.caregiver_profile is not None and self.caregiver_profile.active
