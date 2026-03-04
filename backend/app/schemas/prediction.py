from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field


class PredictionRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    clinical_record_id: uuid.UUID
    created_by: uuid.UUID
    predicted_label: int = Field(ge=0, le=1)
    predicted_proba: float = Field(ge=0, le=1)
    model_name: str
    model_version: str
    threshold: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)