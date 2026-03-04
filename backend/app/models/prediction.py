import uuid
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    clinical_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinical_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Resultado
    predicted_label: Mapped[int] = mapped_column(nullable=False)  # 0/1
    predicted_proba: Mapped[float] = mapped_column(Float, nullable=False)

    # Trazabilidad del modelo
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    model_version: Mapped[str] = mapped_column(String(60), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    clinical_record = relationship("ClinicalRecord", back_populates="predictions")

    __table_args__ = (
        Index("ix_predictions_patient_created", "patient_id", "created_at"),
        Index("ix_predictions_record_created", "clinical_record_id", "created_at"),
    )