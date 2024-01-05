from datetime import datetime
from uuid import UUID

from models.base import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class SavedContent(Base):
    __tablename__ = "saved_content"
    __table_args__ = (UniqueConstraint("external_content_id", "user_profile_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    external_content_id: Mapped[UUID] = mapped_column(nullable=False)
    user_profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id"), nullable=False
    )
    user_profile: Mapped["UserProfile"] = relationship(
        back_populates="saved_content", lazy="joined"
    )