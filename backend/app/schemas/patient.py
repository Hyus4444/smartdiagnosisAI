from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime


class PatientCreate(BaseModel):
    full_name: str
    gender: str
    age: int 


class PatientResponse(BaseModel):
    id: UUID
    full_name: str
    gender: str
    age: int
    created_at: datetime

    class Config:
        from_attributes = True
