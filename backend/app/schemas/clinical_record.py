from datetime import datetime
from pydantic import BaseModel, Field


class ClinicalRecordCreate(BaseModel):
    content: str = Field(min_length=1)


class ClinicalRecordReadBrief(BaseModel):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ClinicalRecordRead(BaseModel):
    id: str
    patient_id: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
