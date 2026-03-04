##Modelos de entidades clínicas, como registros médicos, diagnósticos, tratamientos, etc.
import uuid
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Text, func
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

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Momento real de la medición (si lo dejas)
    recorded_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # === Inputs (se ingresan en UI) ===
    blood_glucose_level: Mapped[float] = mapped_column(Float, nullable=False)
    hba1c_level: Mapped[float] = mapped_column(Float, nullable=False)

    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)

    systolic_bp: Mapped[float] = mapped_column(Float, nullable=False)
    diastolic_bp: Mapped[float] = mapped_column(Float, nullable=False)

    heart_disease: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # === Derivados (calculados en backend, para trazabilidad/replicación) ===
    age_years: Mapped[int] = mapped_column(nullable=False)  # derivado de birth_date al crear record
    bmi: Mapped[float] = mapped_column(Float, nullable=False)  # derivado de weight/height
    hypertension: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # derivado de presiones

    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    patient = relationship("Patient", back_populates="clinical_records")
    predictions = relationship("Prediction", back_populates="clinical_record", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_clinical_records_patient_created", "patient_id", "created_at"),
        Index("ix_clinical_records_patient_recorded", "patient_id", "recorded_at"),
        Index("ix_clinical_records_created_by", "created_by"),
    )