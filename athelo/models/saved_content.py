from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint
from models.base import Base
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import relationship


class SavedContent(Base):
    __tablename__ = "saved_content"
    __table_args__ = (UniqueConstraint("external_content_id", "user_profile_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    external_content_id: Mapped[UUID] = mapped_column(nullable=False)
    user_profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id"), nullable=False
    )
    user_profile: Mapped["UserProfile"] = relationship(back_populates="saved_content")
