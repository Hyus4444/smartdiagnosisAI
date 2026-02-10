import uuid
from sqlalchemy import String, Date, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    document_type: Mapped[str] = mapped_column(String(10), nullable=False)
    document_number: Mapped[str] = mapped_column(String(32), nullable=False)
    birth_date: Mapped["Date"] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(12), nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    clinical_records = relationship(
        "ClinicalRecord",
        back_populates="patient",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("uq_patients_doc", "document_type", "document_number", unique=True),
        Index("ix_patients_full_name", "full_name"),
    )
