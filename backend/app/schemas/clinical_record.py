from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field


class ClinicalRecordCreate(BaseModel):
    content: str = Field(min_length=1)


class ClinicalRecordReadBrief(BaseModel):
    id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ClinicalRecordRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
