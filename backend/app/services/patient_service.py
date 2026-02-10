import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate


def get_patient_by_id(db: Session, patient_id: uuid.UUID) -> Patient | None:
    return db.query(Patient).filter(Patient.id == patient_id).first()


def get_patient_by_document(db: Session, document_type: str, document_number: str) -> Patient | None:
    doc_type = document_type.strip().upper()
    doc_number = document_number.strip()
    return (
        db.query(Patient)
        .filter(Patient.document_type == doc_type, Patient.document_number == doc_number)
        .first()
    )
    
def list_patients(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    q: str | None = None,
) -> tuple[list[Patient], int]:
    query = db.query(Patient)

    if q:
        term = f"%{q.strip()}%"
        # Búsqueda simple por nombre o documento
        query = query.filter(
            (Patient.full_name.ilike(term)) |
            (Patient.document_number.ilike(term))
        )

    total = query.with_entities(func.count(Patient.id)).scalar() or 0

    items = (
        query
        .order_by(Patient.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total

def create_patient(db: Session, data: PatientCreate) -> Patient:
    # Normalización para consistencia (y evitar cc/CC)
    doc_type = data.document_type.strip().upper()
    doc_number = data.document_number.strip()

    patient = Patient(
        full_name=data.full_name.strip(),
        document_type=doc_type,
        document_number=doc_number,
        birth_date=data.birth_date,
        gender=data.gender.strip(),
    )

    db.add(patient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Ya existe un paciente con ese tipo y número de documento.")

    db.refresh(patient)
    return patient