from typing import List

from sqlalchemy import ForeignKey

from models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ThreadPost(TimestampMixin, Base):
    __tablename__ = "thread_posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    thread_id: Mapped[int] = mapped_column(
        ForeignKey("community_threads.id"), nullable=False
    )
    thread: Mapped["CommunityThread"] = relationship(
        back_populates="posts",
        lazy="joined",
    )
