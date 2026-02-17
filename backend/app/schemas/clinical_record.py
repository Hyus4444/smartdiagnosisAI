#Este documento define los esquemas de datos relacionados con los registros clínicos, incluyendo la creación de un nuevo registro y la lectura de registros existentes. 
#Estos esquemas se utilizan para validar y estructurar los datos que se envían y reciben en las operaciones relacionadas con los registros clínicos.
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
    created_by: uuid.UUID 
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
