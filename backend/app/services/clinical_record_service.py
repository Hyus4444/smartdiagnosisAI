import uuid
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.clinical_record import ClinicalRecord
from app.models.patient import Patient
from app.schemas.clinical_record import ClinicalRecordCreate


def _calc_age_years(birth_date: date, today: date | None = None) -> int:
    today = today or date.today()
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return max(years, 0)


def _calc_bmi(weight_kg: float, height_cm: float) -> float:
    h_m = height_cm / 100.0
    return weight_kg / (h_m * h_m)


def _calc_hypertension(systolic: float, diastolic: float) -> bool:
    # Criterio simple y defendible (AHA/ACC clásico):
    # hipertensión si sistólica >= 130 o diastólica >= 80
    return systolic >= 130 or diastolic >= 80


def create_clinical_record(
    db: Session,
    patient_id: uuid.UUID,
    data: ClinicalRecordCreate,
    creator_id: uuid.UUID,
) -> ClinicalRecord:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise ValueError("Paciente no existe.")

    # Validaciones básicas (opcionales pero recomendadas)
    if data.diastolic_bp >= data.systolic_bp:
        raise ValueError("La presión diastólica no puede ser mayor o igual a la sistólica.")

    age_years = _calc_age_years(patient.birth_date)
    bmi = _calc_bmi(float(data.weight_kg), float(data.height_cm))
    hypertension = _calc_hypertension(float(data.systolic_bp), float(data.diastolic_bp))

    record = ClinicalRecord(
        created_by=creator_id,
        patient_id=patient_id,

        blood_glucose_level=float(data.blood_glucose_level),
        hba1c_level=float(data.hba1c_level),
        weight_kg=float(data.weight_kg),
        height_cm=float(data.height_cm),
        systolic_bp=float(data.systolic_bp),
        diastolic_bp=float(data.diastolic_bp),
        heart_disease=bool(data.heart_disease),
        notes=data.notes.strip() if isinstance(data.notes, str) and data.notes.strip() else None,

        # Derivados para trazabilidad/replicación
        age_years=age_years,
        bmi=float(bmi),
        hypertension=bool(hypertension),
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_clinical_record_by_id(db: Session, patient_id: uuid.UUID, record_id: uuid.UUID) -> ClinicalRecord | None:
    return (
        db.query(ClinicalRecord)
        .filter(ClinicalRecord.id == record_id, ClinicalRecord.patient_id == patient_id)
        .first()
    )
    
    
def list_clinical_records_by_patient(
    db: Session,
    patient_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[ClinicalRecord], int]:
    query = db.query(ClinicalRecord).filter(ClinicalRecord.patient_id == patient_id)
    total = query.with_entities(func.count(ClinicalRecord.id)).scalar() or 0

    items = (
        query.order_by(ClinicalRecord.recorded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items, total