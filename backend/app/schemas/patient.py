#Este documento define los esquemas de datos relacionados con los pacientes, incluyendo la creación de un nuevo paciente y la lectura de pacientes existentes. 
#Estos esquemas se utilizan para validar y estructurar los datos que se envían y reciben en las operaciones relacionadas con los pacientes.
from datetime import date, datetime
from typing import List
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator
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
    id: uuid.UUID
    full_name: str
    document_type: str
    document_number: str
    birth_date: date
    gender: str
    created_at: datetime
    created_by: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class PatientReadWithRecords(PatientRead):
    clinical_records: List[ClinicalRecordReadBrief] = []
    model_config = ConfigDict(from_attributes=True)

