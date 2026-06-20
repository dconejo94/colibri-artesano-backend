import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    DateTime,
    Uuid,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ParticipationStatus(PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Event(Base):
    __tablename__ = "events"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    event_date = Column(DateTime(timezone=True), nullable=False)
    cover_image_url = Column(String, nullable=True)
    created_by = Column(Uuid, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship(
        "User", back_populates="created_events", foreign_keys=[created_by]
    )
    participants = relationship(
        "EventParticipant",
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class EventParticipant(Base):
    __tablename__ = "event_participants"
    __table_args__ = (UniqueConstraint("event_id", "store_id", name="uq_event_store"),)

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    event_id = Column(Uuid, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    store_id = Column(Uuid, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    status = Column(
        Enum(ParticipationStatus), nullable=False, default=ParticipationStatus.pending
    )
    requested_by = Column(Uuid, ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(Uuid, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    event = relationship("Event", back_populates="participants")
    store = relationship("Store", back_populates="event_participants")
    requester = relationship(
        "User",
        foreign_keys=[requested_by],
        back_populates="event_participation_requests",
    )
    reviewer = relationship(
        "User", foreign_keys=[reviewed_by], back_populates="event_participation_reviews"
    )
