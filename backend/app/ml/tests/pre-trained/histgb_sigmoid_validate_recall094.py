# histgb_sigmoid_validate_recall094.py
# Objetivo:
# - Entrenar HistGradientBoostingClassifier (HistGB) con class_weight="balanced"
# - Calibrar probabilidades con CalibratedClassifierCV(method="sigmoid")
# - Elegir umbral en VALIDACIÓN para lograr recall >= 0.94 minimizando FP (max precision)
# - Evaluar FINAL en TEST (sin fuga de información)
#
# Dataset: diabetes_prediction_dataset.csv
#
# Ejecutar:
#   python histgb_sigmoid_validate_recall094.py

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
)
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV


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
RECALL_MIN = 0.94


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # gender solo female/male
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
    Elige threshold que maximiza precision sujeto a recall >= recall_min.
    Si hay empate en precision, elige el threshold mayor (menos FP).
    """
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)

    # Alinear tamaños (thresholds es 1 menos)
    precisions = precisions[:-1]
    recalls = recalls[:-1]

    feasible = np.where(recalls >= recall_min)[0]
    if feasible.size == 0:
        # No se alcanzó el recall mínimo: elige el de mayor recall
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


def main():
    # ============
    # 1) Cargar/limpiar
    # ============
    df = pd.read_csv(DATA_PATH)
    df = clean_df(df)

    X = df[FEATURES]
    y = df[TARGET].astype(int).values

    # ============
    # 2) Split: Train / Val / Test
    #   - Test queda totalmente aislado
    #   - Val se usa para calibración y para elegir threshold
    # ============
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=0.25, random_state=RANDOM_STATE, stratify=y_trainval
    )
    # Resultado: Train 60%, Val 20%, Test 20%

    preprocess = build_preprocess()

    # ============
    # 3) Fit preprocess SOLO con train (evita leakage)
    # ============
    X_train_t = preprocess.fit_transform(X_train)
    X_val_t = preprocess.transform(X_val)
    X_test_t = preprocess.transform(X_test)

    # ============
    # 4) Entrenar HistGB en train (features transformados)
    # ============
    base_clf = HistGradientBoostingClassifier(
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )
    base_clf.fit(X_train_t, y_train)

    # ============
    # 5) Calibración sigmoid usando SOLO train (cv interno sobre train)
    #    (No toca val/test)
    # ============
    calibrated = CalibratedClassifierCV(base_clf, method="sigmoid", cv=5)
    calibrated.fit(X_train_t, y_train)

    # ============
    # 6) Elegir threshold en VAL para recall >= 0.94
    # ============
    val_proba = calibrated.predict_proba(X_val_t)[:, 1]

    # Métricas por ranking (sin threshold) en val
    val_roc = roc_auc_score(y_val, val_proba)
    val_pr = average_precision_score(y_val, val_proba)

    print("\n=== VALIDACIÓN (calibrado sigmoid) ===")
    print(f"ROC-AUC: {val_roc:.6f} | PR-AUC: {val_pr:.6f}")

    val_05 = metrics_at_threshold(y_val, val_proba, 0.5)
    print("Threshold 0.50 (val):", {k: val_05[k] for k in ["precision", "recall", "f1", "fp", "fn"]})

    chosen = pick_threshold_best_precision(y_val, val_proba, RECALL_MIN)
    print(f"\nUmbral elegido en VALIDACIÓN (recall >= {RECALL_MIN:.2f}):")
    print(chosen["note"])
    print({k: chosen[k] for k in ["threshold", "precision", "recall", "f1", "fp", "fn"]})

    # ============
    # 7) Evaluación FINAL en TEST usando el threshold elegido
    # ============
    test_proba = calibrated.predict_proba(X_test_t)[:, 1]
    test_roc = roc_auc_score(y_test, test_proba)
    test_pr = average_precision_score(y_test, test_proba)

    print("\n=== TEST FINAL (calibrado sigmoid) ===")
    print(f"ROC-AUC: {test_roc:.6f} | PR-AUC: {test_pr:.6f}")

    test_05 = metrics_at_threshold(y_test, test_proba, 0.5)
    print("Threshold 0.50 (test):", {k: test_05[k] for k in ["precision", "recall", "f1", "fp", "fn"]})

    thr = float(chosen["threshold"])
    test_tuned = metrics_at_threshold(y_test, test_proba, thr)

    print(f"\nThreshold TUNED desde VAL (thr={thr:.6f}) aplicado en TEST:")
    print({k: test_tuned[k] for k in ["threshold", "precision", "recall", "f1", "fp", "fn", "accuracy"]})
    print("Confusion matrix [ [TN, FP], [FN, TP] ]:", test_tuned["confusion_matrix"])

    # Guardar resultados para documento
    out = {
        "recall_min": RECALL_MIN,
        "threshold_selected_on_val": thr,
        "val_roc_auc": val_roc,
        "val_pr_auc": val_pr,
        "val_precision": chosen["precision"],
        "val_recall": chosen["recall"],
        "val_f1": chosen["f1"],
        "val_fp": chosen["fp"],
        "val_fn": chosen["fn"],
        "test_roc_auc": test_roc,
        "test_pr_auc": test_pr,
        "test_precision": test_tuned["precision"],
        "test_recall": test_tuned["recall"],
        "test_f1": test_tuned["f1"],
        "test_fp": test_tuned["fp"],
        "test_fn": test_tuned["fn"],
        "test_accuracy": test_tuned["accuracy"],
    }

    pd.DataFrame([out]).to_csv("histgb_sigmoid_recall094_validation_results.csv", index=False)
    print("\nSaved: histgb_sigmoid_recall094_validation_results.csv")


if __name__ == "__main__":
    main()