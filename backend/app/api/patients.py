import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.patient import PatientCreate, PatientRead
from app.schemas.clinical_record import (
    ClinicalRecordCreate,
    ClinicalRecordRead,
    ClinicalRecordReadBrief,
)
from app.schemas.common import Page

from app.services.patient_service import (
    create_patient,
    get_patient_by_id,
    list_patients,
)
from app.services.clinical_record_service import (
    create_clinical_record,
    list_clinical_records_by_patient,
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient_endpoint(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    try:
        return create_patient(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("", response_model=Page[PatientRead])
def list_patients_endpoint(
    skip: int = 0,
    limit: int = 20,
    q: str | None = None,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    items, total = list_patients(db, skip=skip, limit=limit, q=q)
    return Page(items=items, total=total, skip=skip, limit=limit)
    


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient_endpoint(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
    return patient




@router.post("/{patient_id}/clinical-records", response_model=ClinicalRecordRead, status_code=status.HTTP_201_CREATED)
def create_clinical_record_endpoint(
    patient_id: uuid.UUID,
    payload: ClinicalRecordCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    try:
        return create_clinical_record(db, patient_id, payload)
    except ValueError as e:
        # en service usamos "Paciente no existe."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))



@router.get(
    "/{patient_id}/clinical-records",
    response_model=Page[ClinicalRecordRead],
)
def list_clinical_records_endpoint(
    patient_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    items, total = list_clinical_records_by_patient(db, patient_id, skip, limit)
    return Page(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )