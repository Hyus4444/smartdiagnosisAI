import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate



def create_patient(db: Session, data: PatientCreate) -> Patient:
    # Normalización mínima (consistente con schema)
    doc_type = data.document_type.strip()
    doc_number = data.document_number.strip()

    existing = get_patient_by_document(db, doc_type, doc_number)
    if existing:
        # La capa service no decide HTTP codes; solo lanza error de dominio.
        raise ValueError("Ya existe un paciente con ese tipo y número de documento.")

    patient = Patient(
        full_name=data.full_name.strip(),
        document_type=doc_type,
        document_number=doc_number,
        birth_date=data.birth_date,
        gender=data.gender.strip(),
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient_by_id(db: Session, patient_id: uuid.UUID) -> Patient | None:
    return db.query(Patient).filter(Patient.id == patient_id).first()


def get_patient_by_document(
    db: Session,
    document_type: str,
    document_number: str,
) -> Patient | None:
    # Normalización mínima para evitar duplicados por espacios/case
    doc_type = document_type.strip()
    doc_number = document_number.strip()

    return (
        db.query(Patient)
        .filter(
            Patient.document_type == doc_type,
            Patient.document_number == doc_number,
        )
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