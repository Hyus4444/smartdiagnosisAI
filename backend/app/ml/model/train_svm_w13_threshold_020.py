
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

DATA_FILE = "C:/Users/Jairo/Documents/Repositorios/Proyecto de grado/SmartDiagnosisAI/backend/app/ml/data/raw/diabetes_prediction_dataset.csv"
OUTPUT_DIR = Path("artifacts/svm_w13_threshold_020")
TARGET = "diabetes"
DROP_COLS = ["smoking_history"]
DROP_GENDER_OTHER = True

MODEL_NAME = "svm_w13_sigmoid_threshold_020"
THRESHOLD = 0.20

def load_data():
    df = pd.read_csv(DATA_FILE)

    if DROP_GENDER_OTHER and "gender" in df.columns:
        df = df[df["gender"] != "Other"].copy()

    for col in DROP_COLS:
        if col in df.columns:
            df = df.drop(columns=col)

    if TARGET not in df.columns:
        raise ValueError(f"No se encontró la columna objetivo '{TARGET}'.")

    return df

def build_pipeline(X: pd.DataFrame) -> Pipeline:
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_cols = [c for c in X.columns if c not in categorical_cols]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )

    base_svc = SVC(
        kernel="rbf",
        C=1.0,
        gamma=0.05,
        class_weight={0: 1, 1: 3},
        probability=False,
        random_state=42,
    )

    calibrated_svc = CalibratedClassifierCV(
        estimator=base_svc,
        method="sigmoid",
        cv=3,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", calibrated_svc),
        ]
    )
    return pipeline

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    pipeline = build_pipeline(X)
    pipeline.fit(X, y)

    model_path = OUTPUT_DIR / f"{MODEL_NAME}.joblib"
    joblib.dump(pipeline, model_path)

    metadata = {
        "model_name": MODEL_NAME,
        "model_type": "SVM RBF + sigmoid calibration",
        "threshold": THRESHOLD,
        "target": TARGET,
        "dropped_columns": DROP_COLS,
        "drop_gender_other": DROP_GENDER_OTHER,
        "training_rows": int(len(df)),
        "features_used": X.columns.tolist(),
        "svm_params": {
            "kernel": "rbf",
            "C": 1.0,
            "gamma": 0.05,
            "class_weight": {"0": 1, "1": 3},
        },
        "calibration": "sigmoid",
    }

    with open(OUTPUT_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("Pipeline entrenado y guardado correctamente.")
    print(f"Modelo: {model_path.resolve()}")
    print(f"Metadata: {(OUTPUT_DIR / 'metadata.json').resolve()}")

if __name__ == "__main__":
    main()
