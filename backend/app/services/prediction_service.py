import json
import uuid
from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.clinical_record import ClinicalRecord
from app.models.prediction import Prediction

# Rutas a artifacts
BASE_DIR = Path(__file__).resolve().parents[1]  # app/
MODEL_PATH = BASE_DIR / "ml" / "models" / "smartdiagnosis_histgb_sigmoid_pipeline.joblib"
META_PATH = BASE_DIR / "ml" / "models" / "smartdiagnosis_histgb_sigmoid_metadata.json"

# Cache en memoria (se carga 1 vez)
_PIPELINE = None
_META = None


def _load_artifacts():
    global _PIPELINE, _META
    if _PIPELINE is None:
        _PIPELINE = joblib.load(MODEL_PATH)
    if _META is None:
        _META = json.loads(META_PATH.read_text(encoding="utf-8"))
    return _PIPELINE, _META


def _to_model_features(patient: Patient, record: ClinicalRecord) -> pd.DataFrame:
    # El pipeline espera estas columnas (según metadata del entrenamiento)
    # age: desde record.age_years (derivado)
    # gender: from patient.gender (M/F -> male/female)
    gender_raw = (patient.gender or "").strip().upper()
    gender = "male" if gender_raw == "M" else "female"

    row = {
        "age": float(record.age_years),
        "gender": gender,
        "bmi": float(record.bmi),
        "HbA1c_level": float(record.hba1c_level),
        "blood_glucose_level": float(record.blood_glucose_level),
        "hypertension": int(record.hypertension),
        "heart_disease": int(record.heart_disease),
    }
    return pd.DataFrame([row])


def predict_and_save(
    db: Session,
    patient_id: uuid.UUID,
    record_id: uuid.UUID,
    creator_id: uuid.UUID,
) -> Prediction:
    pipeline, meta = _load_artifacts()

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise ValueError("Paciente no encontrado.")

    record = (
        db.query(ClinicalRecord)
        .filter(ClinicalRecord.id == record_id, ClinicalRecord.patient_id == patient_id)
        .first()
    )
    if not record:
        raise ValueError("Registro clínico no encontrado para este paciente.")

    X = _to_model_features(patient, record)

    proba = float(pipeline.predict_proba(X)[0, 1])
    threshold = float(meta.get("threshold_selected_on_val", 0.5))
    label = 1 if proba >= threshold else 0

    model_name = meta.get("model_type", "HistGB+Sigmoid")
    model_version = meta.get("model_version", "v1")  # si no lo guardaste, queda v1

    pred = Prediction(
        patient_id=patient_id,
        clinical_record_id=record_id,
        created_by=creator_id,
        predicted_label=label,
        predicted_proba=proba,
        model_name=str(model_name),
        model_version=str(model_version),
        threshold=threshold,
    )

    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred