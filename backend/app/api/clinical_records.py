import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.clinical_record import ClinicalRecord
from app.schemas.clinical_record import ClinicalRecordRead
from app.services.clinical_record_service import list_clinical_records_by_patient

router = APIRouter(prefix="/clinical-records", tags=["Clinical Records"])


@router.get("/{patient_id}/clinical-records", response_model=dict)
def list_clinical_records_endpoint(
    patient_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    items, total = list_clinical_records_by_patient(db, patient_id, skip, limit)
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }

