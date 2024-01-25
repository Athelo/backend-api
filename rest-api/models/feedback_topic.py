from typing import List

from models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column


class FeedbackTopic(TimestampMixin, Base):
    __tablename__ = "feedback_topics"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    def to_json(self):
        # contains legacy fields application and category
        return {
            "id": self.id,
            "category": self.id,
            "name": self.name,
            "application": 1,
        }
