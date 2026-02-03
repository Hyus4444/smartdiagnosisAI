import uuid
from sqlalchemy import Column, String, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
class Patient(Base):
    __tablename__ = "patients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    full_name = Column(String(150), nullable=False)
    gender = Column(String(20), nullable=False)
    date_of_birth = Column(Date, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship("User", backref="patients")
