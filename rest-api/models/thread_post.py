
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class ThreadPost(TimestampMixin, Base):
    __tablename__ = "thread_posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(nullable=False)
    thread_id: Mapped[int] = mapped_column(
        ForeignKey("community_threads.id"), nullable=False
    )
    thread: Mapped["CommunityThread"] = relationship(
        back_populates="posts",
        lazy="joined",
    )
