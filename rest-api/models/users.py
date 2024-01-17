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
    user_feelings: Mapped[List["UserFeeling"]] = relationship(
        back_populates="users", lazy="joined"
    )
    user_symptoms: Mapped[List["UserSymptom"]] = relationship(
        back_populates="users", lazy="joined"
    )
    saved_content: Mapped[List["SavedContent"]] = relationship(
        back_populates="users", lazy="joined"
    )
