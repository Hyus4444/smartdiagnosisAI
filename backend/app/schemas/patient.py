from datetime import date, datetime
from typing import List
from pydantic import BaseModel, Field, field_validator
from app.schemas.clinical_record import ClinicalRecordReadBrief
class PatientCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=120)
    document_type: str = Field(min_length=1, max_length=10)
    document_number: str = Field(min_length=3, max_length=32)
    birth_date: date
    gender: str = Field(min_length=1, max_length=12)

    @field_validator("full_name", "document_type", "document_number", "gender", mode="before")
    @classmethod
    def strip_strings(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("birth_date")
    @classmethod
    def birth_date_not_future(cls, v: date):
        from datetime import date as d
        if v > d.today():
            raise ValueError("birth_date no puede ser futura")
        return v
class PatientRead(BaseModel):
    id: str
    full_name: str
    document_type: str
    document_number: str
    birth_date: date
    gender: str
    created_at: datetime

    class Config:
        from_attributes = True

class PatientReadWithRecords(PatientRead):
    clinical_records: List[ClinicalRecordReadBrief] = []

    class Config:
        from_attributes = True
