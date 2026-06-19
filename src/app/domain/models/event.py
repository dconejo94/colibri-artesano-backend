import uuid

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Uuid, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=True)
    image_url = Column(String, nullable=True)
    created_by = Column(Uuid, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User", back_populates="created_events")
    attendees = relationship(
        "EventAttendee",
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class EventAttendee(Base):
    """Buyer RSVP to an event.

    Vendor participation is modeled separately via ``Event.created_by`` (event
    creation). This table tracks attendance interest from any authenticated user.
    """

    __tablename__ = "event_attendees"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_attendee"),)

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    event_id = Column(
        Uuid, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    event = relationship("Event", back_populates="attendees")
    user = relationship("User", back_populates="event_attendances")
