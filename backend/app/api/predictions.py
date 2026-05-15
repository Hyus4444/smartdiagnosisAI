import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.prediction import PredictionRead
from app.services.patient_service import get_patient_by_id
from app.services.prediction_service import predict_and_save

router = APIRouter(prefix="", tags=["Predictions"])


@router.post(
    "/patients/{patient_id}/clinical-records/{record_id}/predict",
    response_model=PredictionRead,
    status_code=status.HTTP_201_CREATED,
)
def predict_endpoint(
    patient_id: uuid.UUID,
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # ownership del paciente
    patient = get_patient_by_id(db, patient_id, creator_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")

    try:
        return predict_and_save(db, patient_id, record_id, creator_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))