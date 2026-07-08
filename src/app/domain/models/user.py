import uuid

from sqlalchemy import Column, String, Boolean, DateTime, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    role = Column(String(20), nullable=False, default="buyer", server_default="buyer")
    name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    store = relationship("Store", back_populates="owner", uselist=False)
    orders = relationship("MainOrder", back_populates="buyer")
    followed_stores = relationship(
        "Store", secondary="follows", back_populates="followers"
    )
    created_events = relationship(
        "Event", back_populates="creator", foreign_keys="Event.created_by"
    )
    event_participation_requests = relationship(
        "EventParticipant",
        back_populates="requester",
        foreign_keys="EventParticipant.requested_by",
    )
    event_participation_reviews = relationship(
        "EventParticipant",
        back_populates="reviewer",
        foreign_keys="EventParticipant.reviewed_by",
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    fcm_tokens = relationship(
        "FCMToken", back_populates="user", cascade="all, delete-orphan"
    )
