import uuid 

from sqlalchemy import (
    Column,
    String, 
    ForeignKey,
    DateTime,
    Uuid,
)

from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class FCMToken(Base):
    __tablename__ = "fcm_tokens"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="fcm_tokens")