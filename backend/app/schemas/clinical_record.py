#Este documento define los esquemas de datos relacionados con los registros clínicos, incluyendo la creación de un nuevo registro y la lectura de registros existentes. 
#Estos esquemas se utilizan para validar y estructurar los datos que se envían y reciben en las operaciones relacionadas con los registros clínicos.
from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field


class ClinicalRecordCreate(BaseModel):
    # Inputs que vienen de la UI
    blood_glucose_level: float = Field(gt=0)
    hba1c_level: float = Field(gt=0)

    weight_kg: float = Field(gt=0)
    height_cm: float = Field(gt=0)

    systolic_bp: float = Field(gt=0)
    diastolic_bp: float = Field(gt=0)

    heart_disease: bool
    notes: str | None = Field(default=None, max_length=2000)


class ClinicalRecordReadBrief(BaseModel):
    id: uuid.UUID
    recorded_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClinicalRecordRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    created_by: uuid.UUID

    recorded_at: datetime
    created_at: datetime

    # inputs
    blood_glucose_level: float
    hba1c_level: float
    weight_kg: float
    height_cm: float
    systolic_bp: float
    diastolic_bp: float
    heart_disease: bool
    notes: str | None

    # derivados
    age_years: int
    bmi: float
    hypertension: bool

    model_config = ConfigDict(from_attributes=True)