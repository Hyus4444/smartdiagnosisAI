## Este servicio maneja la lógica de negocio relacionada con los registros clínicos, como creación y listado por paciente.
import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.clinical_record import ClinicalRecord
from app.models.patient import Patient
from app.schemas.clinical_record import ClinicalRecordCreate

def create_clinical_record(
    db: Session,
    patient_id: uuid.UUID,
    data: ClinicalRecordCreate,
    creator_id: uuid.UUID
) -> ClinicalRecord:
    # Verificar que el paciente existe (sin endpoints aún, error de dominio)
    patient_exists = db.query(Patient.id).filter(Patient.id == patient_id).first()
    if not patient_exists:
        raise ValueError("Paciente no existe.")

    record = ClinicalRecord(
        created_by=creator_id,
        patient_id=patient_id,
        content=data.content.strip(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_clinical_records_by_patient(
    db: Session,
    patient_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[ClinicalRecord], int]:
    query = db.query(ClinicalRecord).filter(ClinicalRecord.patient_id == patient_id)

    total = query.with_entities(func.count(ClinicalRecord.id)).scalar() or 0

    items = (
        query
        .order_by(ClinicalRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total