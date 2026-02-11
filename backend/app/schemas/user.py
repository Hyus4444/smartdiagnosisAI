#Este documento define los esquemas de datos relacionados con los usuarios, incluyendo la creación de un nuevo usuario y la lectura de usuarios existentes. 
#Estos esquemas se utilizan para validar y estructurar los datos que se envían y reciben en las operaciones relacionadas con los usuarios.
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

model_config = ConfigDict(from_attributes=True)
