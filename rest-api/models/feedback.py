
from models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


class Feedback(TimestampMixin, Base):
    __tablename__ = "feedbacks"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["Users"] = relationship(lazy="joined", single_parent=True)
    content: Mapped[str] = mapped_column(nullable=False)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("feedback_topics.id"), nullable=False
    )
    topic: Mapped["FeedbackTopic"] = relationship(
        lazy="joined",
    )

    def to_json(self):
        return {
            "id": self.id,
            "content": self.content,
            "status": 2,
            "topic": self.topic.to_json(),
        }
