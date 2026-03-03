# compare_histgb_extratrees_v1.py
# Comparación adicional (sin modelos complejos): HistGB vs ExtraTrees
# - Reporta: Holdout (ROC-AUC, PR-AUC, F1, Precision, Recall, Accuracy, CM)
# - CV (medias): ROC-AUC, PR-AUC, F1, Precision, Recall, Accuracy
# - Guarda CSV: compare_histgb_extratrees_raw.csv y compare_histgb_extratrees_ranked.csv

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
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
)

from sklearn.ensemble import HistGradientBoostingClassifier, ExtraTreesClassifier


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


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalizar gender y filtrar solo female/male
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


# =========================
# Preprocess (para ambos)
# =========================
preprocess = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), NUMERIC),
        ("cat", OneHotEncoder(handle_unknown="ignore", drop="if_binary", sparse_output=False), CATEGORICAL),
        ("bin", "passthrough", BINARY),
    ],
    remainder="drop",
)


# =========================
# Modelos simples
# =========================
MODELS = {
    "HistGB_balanced": HistGradientBoostingClassifier(
        random_state=RANDOM_STATE,
        class_weight="balanced",
    ),
    "ExtraTrees_balanced": ExtraTreesClassifier(
        n_estimators=500,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced_subsample",
    ),
}


def holdout_metrics(pipe: Pipeline, X_train, X_test, y_train, y_test) -> dict:
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)

    # Probabilidades para ROC-AUC y PR-AUC
    if hasattr(pipe, "predict_proba"):
        y_proba = pipe.predict_proba(X_test)[:, 1]
    else:
        y_proba = None

    metrics = {
        "holdout_accuracy": float(accuracy_score(y_test, y_pred)),
        "holdout_precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "holdout_recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "holdout_f1": float(f1_score(y_test, y_pred)),
        "holdout_confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }

    metrics["holdout_roc_auc"] = float(roc_auc_score(y_test, y_proba)) if y_proba is not None else float("nan")
    metrics["holdout_pr_auc"] = float(average_precision_score(y_test, y_proba)) if y_proba is not None else float("nan")

    return metrics


def cv_metrics(pipe: Pipeline, X, y, folds: int = 5) -> dict:
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=RANDOM_STATE)

    scoring = {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
        "pr_auc": "average_precision",  # PR-AUC
    }

    # Windows-friendly: usa n_jobs=1 (evita joblib/loky pesado)
    out = cross_validate(pipe, X, y, cv=cv, scoring=scoring, n_jobs=1)

    return {
        "cv_accuracy": float(np.mean(out["test_accuracy"])),
        "cv_precision": float(np.mean(out["test_precision"])),
        "cv_recall": float(np.mean(out["test_recall"])),
        "cv_f1": float(np.mean(out["test_f1"])),
        "cv_roc_auc": float(np.mean(out["test_roc_auc"])),
        "cv_pr_auc": float(np.mean(out["test_pr_auc"])),
    }


def main():
    df = pd.read_csv(DATA_PATH)
    df = clean_df(df)

    X = df[FEATURES]
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    rows = []
    for name, model in MODELS.items():
        pipe = Pipeline(steps=[("prep", preprocess), ("model", model)])

        hold = holdout_metrics(pipe, X_train, X_test, y_train, y_test)
        cvm = cv_metrics(pipe, X, y, folds=5)

        row = {"model": name, **hold, **cvm}
        rows.append(row)

        print(f"\n=== {name} ===")
        print("Holdout:", {k: row[k] for k in row if k.startswith("holdout_") and k != "holdout_confusion_matrix"})
        print("CV:", {k: row[k] for k in row if k.startswith("cv_")})
        print("Confusion matrix:", row["holdout_confusion_matrix"])

    results = pd.DataFrame(rows)

    # Ranking orientado a tu objetivo (FN no negociable):
    # 1) mayor recall CV
    # 2) luego mayor PR-AUC CV (reduce FP manteniendo recall alto)
    # 3) luego F1 CV
    ranked = results.sort_values(
        by=["cv_recall", "cv_pr_auc", "cv_f1", "cv_roc_auc"],
        ascending=False,
    )

    results.to_csv("compare_histgb_extratrees_raw.csv", index=False)
    ranked.to_csv("compare_histgb_extratrees_ranked.csv", index=False)

    print("\nSaved:")
    print("- compare_histgb_extratrees_raw.csv")
    print("- compare_histgb_extratrees_ranked.csv")


if __name__ == "__main__":
    main()