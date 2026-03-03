from __future__ import annotations

import json
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_recall_curve,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
)
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

import joblib


# =========================
# Config
# =========================
DATA_PATH = "backend/app/ml/data/raw/diabetes_prediction_dataset.csv"
TARGET = "diabetes"

FEATURES = [
    "age",
    "gender",
    "bmi",
    "HbA1c_level",
    "blood_glucose_level",
    "hypertension",
    "heart_disease",
]

NUMERIC = ["age", "bmi", "HbA1c_level", "blood_glucose_level"]
BINARY = ["hypertension", "heart_disease"]
CATEGORICAL = ["gender"]

RANDOM_STATE = 42

# Ajusta aquí tu requisito de recall mínimo:
RECALL_MIN = 0.94

# Export names
OUT_MODEL = "smartdiagnosis_histgb_sigmoid_pipeline.joblib"
OUT_META = "smartdiagnosis_histgb_sigmoid_metadata.json"


# =========================
# Helpers
# =========================
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Solo female/male
    df["gender"] = df["gender"].astype(str).str.strip().str.lower()
    df = df[df["gender"].isin(["female", "male"])]

    # Tipos
    for col in ["hypertension", "heart_disease", TARGET]:
        df[col] = df[col].astype(int)

    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=NUMERIC)

    missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en el dataset: {missing}")

    return df


def build_preprocess() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore", drop="if_binary", sparse_output=False), CATEGORICAL),
            ("bin", "passthrough", BINARY),
        ],
        remainder="drop",
    )


def metrics_at_threshold(y_true: np.ndarray, y_proba: np.ndarray, thr: float) -> dict:
    y_pred = (y_proba >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    return {
        "threshold": float(thr),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
    }


def pick_threshold_best_precision(y_true: np.ndarray, y_proba: np.ndarray, recall_min: float) -> dict:
    """
    Threshold que maximiza precision sujeto a recall >= recall_min.
    Empate: mayor threshold (menos FP).
    """
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)

    # thresholds tiene len = len(precisions)-1
    precisions = precisions[:-1]
    recalls = recalls[:-1]

    feasible = np.where(recalls >= recall_min)[0]
    if feasible.size == 0:
        # No se alcanzó recall mínimo: elegir máximo recall
        best = int(np.argmax(recalls))
        thr = float(thresholds[best])
        out = metrics_at_threshold(y_true, y_proba, thr)
        out["note"] = f"No se alcanzó recall >= {recall_min:.2f}. Se eligió máximo recall."
        return out

    best_prec = np.max(precisions[feasible])
    candidates = feasible[precisions[feasible] == best_prec]
    best = int(candidates[np.argmax(thresholds[candidates])])

    thr = float(thresholds[best])
    out = metrics_at_threshold(y_true, y_proba, thr)
    out["note"] = f"Max precision con recall >= {recall_min:.2f}"
    return out


# =========================
# Main
# =========================
def main():
    df = pd.read_csv(DATA_PATH)
    df = clean_df(df)

    X = df[FEATURES]
    y = df[TARGET].astype(int).values

    # 80/20: Test aislado
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    # Dentro del 80%, creamos un VAL (para elegir umbral sin tocar test)
    # Train=60%, Val=20%, Test=20%
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=0.25, random_state=RANDOM_STATE, stratify=y_trainval
    )

    preprocess = build_preprocess()

    # Pipeline base (prep + HistGB)
    base_pipe = Pipeline(
        steps=[
            ("prep", preprocess),
            ("model", HistGradientBoostingClassifier(
                random_state=RANDOM_STATE,
                class_weight="balanced",
            )),
        ]
    )

    # Calibración SIGMOID aplicada al pipeline completo (incluye preprocess)
    # cv=5 calibrará usando SOLO X_train / y_train
    calibrated_pipe = CalibratedClassifierCV(
        estimator=base_pipe,
        method="sigmoid",
        cv=5,
    )

    print("\nEntrenando + calibrando (sigmoid) en TRAIN...")
    calibrated_pipe.fit(X_train, y_train)

    # Elegir threshold en VAL (recall >= RECALL_MIN)
    val_proba = calibrated_pipe.predict_proba(X_val)[:, 1]

    val_roc = roc_auc_score(y_val, val_proba)
    val_pr = average_precision_score(y_val, val_proba)

    chosen = pick_threshold_best_precision(y_val, val_proba, RECALL_MIN)
    thr = float(chosen["threshold"])

    print("\n=== VALIDACIÓN ===")
    print(f"ROC-AUC: {val_roc:.6f} | PR-AUC: {val_pr:.6f}")
    print(chosen["note"])
    print({k: chosen[k] for k in ["threshold", "precision", "recall", "f1", "fp", "fn"]})

    # Evaluación FINAL en TEST (sin tocar entrenamiento/umbral)
    test_proba = calibrated_pipe.predict_proba(X_test)[:, 1]
    test_roc = roc_auc_score(y_test, test_proba)
    test_pr = average_precision_score(y_test, test_proba)
    test_metrics = metrics_at_threshold(y_test, test_proba, thr)

    print("\n=== TEST FINAL ===")
    print(f"ROC-AUC: {test_roc:.6f} | PR-AUC: {test_pr:.6f}")
    print({k: test_metrics[k] for k in ["threshold", "precision", "recall", "f1", "fp", "fn", "accuracy"]})
    print("Confusion matrix:", test_metrics["confusion_matrix"])

    # Exportar modelo completo (calibrated pipeline)
    joblib.dump(calibrated_pipe, OUT_MODEL)

    # Exportar metadata (threshold + features + reglas)
    meta = {
        "model_type": "HistGradientBoostingClassifier + CalibratedClassifierCV(sigmoid)",
        "features": FEATURES,
        "target": TARGET,
        "gender_allowed": ["female", "male"],
        "recall_min_constraint": RECALL_MIN,
        "threshold_selected_on_val": thr,
        "val_metrics": {
            "roc_auc": float(val_roc),
            "pr_auc": float(val_pr),
            "precision": float(chosen["precision"]),
            "recall": float(chosen["recall"]),
            "f1": float(chosen["f1"]),
            "fp": int(chosen["fp"]),
            "fn": int(chosen["fn"]),
        },
        "test_metrics": {
            "roc_auc": float(test_roc),
            "pr_auc": float(test_pr),
            "precision": float(test_metrics["precision"]),
            "recall": float(test_metrics["recall"]),
            "f1": float(test_metrics["f1"]),
            "accuracy": float(test_metrics["accuracy"]),
            "fp": int(test_metrics["fp"]),
            "fn": int(test_metrics["fn"]),
            "confusion_matrix": test_metrics["confusion_matrix"],
        },
        "random_state": RANDOM_STATE,
    }

    with open(OUT_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print("\nExportado:")
    print(f"- {OUT_MODEL}")
    print(f"- {OUT_META}")


if __name__ == "__main__":
    main()

