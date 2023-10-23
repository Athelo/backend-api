from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime
from models.base import Base


class Vote(Base):
    __tablename__ = "votes"

    vote_id: Mapped[int] = mapped_column(primary_key=True)
    time_cast: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    candidate: Mapped[str] = mapped_column(nullable=False)
