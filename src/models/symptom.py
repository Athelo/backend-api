from models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column


class Symptom(TimestampMixin, Base):
    __tablename__ = "symptoms"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str]
