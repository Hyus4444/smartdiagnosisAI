##Modelos de entidades clínicas, como registros médicos, diagnósticos, tratamientos, etc.
import uuid
from sqlalchemy import Text, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ClinicalRecord(Base):
    __tablename__ = "clinical_records"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # “documento” mínimo; después lo descompones en campos clínicos si lo necesitas
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    patient = relationship("Patient", back_populates="clinical_records")

    __table_args__ = (
        Index("ix_clinical_records_patient_created", "patient_id", "created_at"),
    )
