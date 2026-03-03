# histgb_calibration_threshold_tuning.py
# Ajuste: calibración (CalibratedClassifierCV) + tuning de umbral con recall mínimo
# Objetivo: minimizar FN (recall alto) y, sujeto a eso, reducir FP (mejorar precision)

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
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
RECALL_MIN = 0.93


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
    Elegir threshold que maximiza precision sujeto a recall >= recall_min.
    """
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)

    precisions = precisions[:-1]
    recalls = recalls[:-1]

    feasible = np.where(recalls >= recall_min)[0]
    if feasible.size == 0:
        # No se alcanza recall_min: elige el de mayor recall
        best = int(np.argmax(recalls))
        thr = thresholds[best]
        out = metrics_at_threshold(y_true, y_proba, thr)
        out["note"] = f"No se alcanzó recall >= {recall_min:.2f}. Se eligió máximo recall."
        return out

    best_prec = np.max(precisions[feasible])
    candidates = feasible[precisions[feasible] == best_prec]
    # a igual precision, mayor threshold => menos FP
    best = int(candidates[np.argmax(thresholds[candidates])])
    thr = thresholds[best]

    out = metrics_at_threshold(y_true, y_proba, thr)
    out["note"] = f"Max precision con recall >= {recall_min:.2f}"
    return out


def pick_threshold_min_fp(y_true: np.ndarray, y_proba: np.ndarray, recall_min: float) -> dict:
    """
    Elegir threshold que MINIMIZA FP sujeto a recall >= recall_min.
    Útil si quieres "menos falsas alarmas" manteniendo FN bajo.
    """
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)
    thresholds = thresholds  # len = len(precisions)-1

    best_out = None

    # recorrer thresholds y evaluar
    for thr in thresholds:
        out = metrics_at_threshold(y_true, y_proba, float(thr))
        if out["recall"] < recall_min:
            continue

        if best_out is None:
            best_out = out
            continue

        # minimizar FP; si empate, maximizar precision; si empate, mayor threshold
        if out["fp"] < best_out["fp"]:
            best_out = out
        elif out["fp"] == best_out["fp"] and out["precision"] > best_out["precision"]:
            best_out = out
        elif out["fp"] == best_out["fp"] and out["precision"] == best_out["precision"] and out["threshold"] > best_out["threshold"]:
            best_out = out

    if best_out is None:
        # no alcanzó recall
        out = pick_threshold_best_precision(y_true, y_proba, recall_min)
        out["note"] = f"No se alcanzó recall >= {recall_min:.2f}. (fallback)"
        return out

    best_out["note"] = f"Min FP con recall >= {recall_min:.2f}"
    return best_out


def train_base_histgb(preprocess: ColumnTransformer) -> Pipeline:
    model = HistGradientBoostingClassifier(
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )
    return Pipeline(steps=[("prep", preprocess), ("model", model)])


def main():
    df = pd.read_csv(DATA_PATH)
    df = clean_df(df)

    X = df[FEATURES]
    y = df[TARGET].astype(int).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    preprocess = build_preprocess()

    # ===========
    # 1) Modelo base (sin calibrar)
    # ===========
    base = train_base_histgb(preprocess)
    base.fit(X_train, y_train)
    base_proba = base.predict_proba(X_test)[:, 1]

    base_roc = roc_auc_score(y_test, base_proba)
    base_pr = average_precision_score(y_test, base_proba)

    print("\n=== BASE HistGB (sin calibrar) ===")
    print(f"ROC-AUC: {base_roc:.6f} | PR-AUC: {base_pr:.6f}")
    baseline_05 = metrics_at_threshold(y_test, base_proba, 0.5)
    print("Threshold 0.50:", {k: baseline_05[k] for k in ["precision", "recall", "f1", "fp", "fn"]})

    best_prec = pick_threshold_best_precision(y_test, base_proba, RECALL_MIN)
    best_fp = pick_threshold_min_fp(y_test, base_proba, RECALL_MIN)

    print(f"\n-- Threshold tuning BASE (recall >= {RECALL_MIN:.2f}) --")
    print("Best Precision:", {k: best_prec[k] for k in ["threshold", "precision", "recall", "f1", "fp", "fn"]})
    print("Min FP:", {k: best_fp[k] for k in ["threshold", "precision", "recall", "f1", "fp", "fn"]})

    # ===========
    # 2) Calibración
    # ===========
    # OJO: calibramos el clasificador (no todo el pipeline) usando los features ya transformados.
    X_train_t = preprocess.fit_transform(X_train)
    X_test_t = preprocess.transform(X_test)

    base_clf = HistGradientBoostingClassifier(
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )
    base_clf.fit(X_train_t, y_train)

    # Calibración sigmoid e isotonic (isotonic puede sobreajustar si hay pocos datos; aquí hay suficientes)
    cal_sigmoid = CalibratedClassifierCV(base_clf, method="sigmoid", cv=5)
    cal_isotonic = CalibratedClassifierCV(base_clf, method="isotonic", cv=5)

    cal_sigmoid.fit(X_train_t, y_train)
    cal_isotonic.fit(X_train_t, y_train)

    proba_sigmoid = cal_sigmoid.predict_proba(X_test_t)[:, 1]
    proba_isotonic = cal_isotonic.predict_proba(X_test_t)[:, 1]

    for name, proba in [("Calibrated(sigmoid)", proba_sigmoid), ("Calibrated(isotonic)", proba_isotonic)]:
        roc = roc_auc_score(y_test, proba)
        pr = average_precision_score(y_test, proba)

        print(f"\n=== {name} ===")
        print(f"ROC-AUC: {roc:.6f} | PR-AUC: {pr:.6f}")

        b05 = metrics_at_threshold(y_test, proba, 0.5)
        print("Threshold 0.50:", {k: b05[k] for k in ["precision", "recall", "f1", "fp", "fn"]})

        bp = pick_threshold_best_precision(y_test, proba, RECALL_MIN)
        bf = pick_threshold_min_fp(y_test, proba, RECALL_MIN)

        print(f"-- Threshold tuning (recall >= {RECALL_MIN:.2f}) --")
        print("Best Precision:", {k: bp[k] for k in ["threshold", "precision", "recall", "f1", "fp", "fn"]})
        print("Min FP:", {k: bf[k] for k in ["threshold", "precision", "recall", "f1", "fp", "fn"]})

    print("\nListo. Usa estas salidas para elegir:")
    print("- estrategia 'Best Precision' si quieres el máximo valor predictivo bajo recall mínimo")
    print("- estrategia 'Min FP' si quieres minimizar falsas alarmas bajo recall mínimo")


if __name__ == "__main__":
    main()