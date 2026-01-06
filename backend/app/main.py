from fastapi import FastAPI
from app.core.database import engine

app = FastAPI(title="SmartDiagnosis AI API")

@app.get("/")
def health_check():
    return {"status": "API running"}
