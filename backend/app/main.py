from fastapi import FastAPI
from app.core.database import Base, engine
from app.models import user, patient
from app.api import logIn, signIn, patients

app = FastAPI(title="SmartDiagnosis AI API", version="1.0.0") 

app.include_router(logIn.router)
app.include_router(signIn.router)
app.include_router(patients.router)
