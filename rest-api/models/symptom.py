from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class Symptom(TimestampMixin, Base):
    __tablename__ = "symptoms"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str]
