from fastapi import FastAPI
from app.core.database import Base, engine
from app.models import user, patient
from app.api import logIn, signIn

app = FastAPI(title="SmartDiagnosis AI API", version="1.0.0") 

Base.metadata.create_all(bind=engine)

app.include_router(logIn.router)
app.include_router(signIn.router)


@app.get("/smartdiagnosis/db")
def health_check():
    try:
        with engine.connect() as connection:
            return {"status": "Database connection successful"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
    return {"status": "SmartDiagnosis AI API is running"}

    
