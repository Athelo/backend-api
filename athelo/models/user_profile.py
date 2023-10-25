from typing import List

from models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserProfile(TimestampMixin, Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    display_name: Mapped[str]
    email: Mapped[str] = mapped_column(index=True, unique=True)
    active: Mapped[bool] = mapped_column(default=True)
    user_symptoms: Mapped[List["UserSymptom"]] = relationship(
        back_populates="user_profile"
    )
    saved_content: Mapped[List["SavedContent"]] = relationship(
        back_populates="user_profile"
    )
