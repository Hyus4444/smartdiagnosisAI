from app.core.database import engine
from fastapi import FastAPI

app = FastAPI(title="SmartDiagnosis AI API", version="1.0.0")

@app.get("/smartdiagnosis/db")
def health_check():
    try:
        with engine.connect() as connection:
            return {"status": "Database connection successful"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
    return {"status": "SmartDiagnosis AI API is running"}

    
