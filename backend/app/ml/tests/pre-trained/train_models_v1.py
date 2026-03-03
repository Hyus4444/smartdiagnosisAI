# train_models_v1.py
# Entrenamiento y comparación de modelos (V1, SIN smoking_history)
# Modelos: Logistic Regression, Random Forest, SVM, Naive Bayes, HistGradientBoosting
# Dataset: diabetes_prediction_dataset.csv

from __future__ import annotations

import pandas as pd
import numpy as np

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
    confusion_matrix,
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

import joblib


# =========================
# 1) Configuración
# =========================
DATA_PATH = "backend/app/ml/data/raw/diabetes_prediction_dataset.csv" 
TARGET = "diabetes"

# Feature set V1 (sin smoking_history)
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


# =========================
# 2) Preprocesamiento
# =========================
preprocess = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), NUMERIC),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
        ("bin", "passthrough", BINARY),
    ],
    remainder="drop",
)


# =========================
# 3) Modelos
# =========================
MODELS: dict[str, object] = {
    "LogReg": LogisticRegression(max_iter=3000, class_weight="balanced"),
    "RandomForest": RandomForestClassifier(
        n_estimators=300,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced_subsample",
    ),
    "SVM": SVC(probability=True, class_weight="balanced"),
    "GaussianNB": GaussianNB(),
    "HistGB": HistGradientBoostingClassifier(
        random_state=RANDOM_STATE,
        class_weight="balanced",
    ),
}


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalizar texto
    if "gender" in df.columns:
        df["gender"] = df["gender"].astype(str).str.strip().str.lower()

    if "gender" in df.columns:
        df["gender"] = df["gender"].astype(str).str.strip().str.lower()
        df = df[df["gender"].isin(["female", "male"])]
    # Tipos
    for col in ["hypertension", "heart_disease", TARGET]:
        if col in df.columns:
            df[col] = df[col].astype(int)

    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop mínimos (solo si faltan numéricos)
    df = df.dropna(subset=NUMERIC)

    # Asegurar columnas necesarias
    missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en el dataset: {missing}")

    return df


def evaluate_holdout(pipe: Pipeline, X_train, X_test, y_train, y_test) -> dict:
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, "predict_proba") else None

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred)),
    }

    if y_proba is not None:
        metrics["roc_auc"] = float(roc_auc_score(y_test, y_proba))
    else:
        metrics["roc_auc"] = float("nan")

    metrics["confusion_matrix"] = confusion_matrix(y_test, y_pred).tolist()
    return metrics


def evaluate_cv(pipe: Pipeline, X, y, folds: int = 5) -> dict:
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=RANDOM_STATE)

    scoring = {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
    }

    # Windows-friendly: usa n_jobs=1 si tienes problemas con joblib
    out = cross_validate(pipe, X, y, cv=cv, scoring=scoring, n_jobs=1)

    return {
        "cv_accuracy": float(np.mean(out["test_accuracy"])),
        "cv_precision": float(np.mean(out["test_precision"])),
        "cv_recall": float(np.mean(out["test_recall"])),
        "cv_f1": float(np.mean(out["test_f1"])),
        "cv_roc_auc": float(np.mean(out["test_roc_auc"])),
    }


def main():
    df = pd.read_csv(DATA_PATH)
    df = clean_df(df)

    X = df[FEATURES]
    y = df[TARGET].astype(int)

    # Holdout split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    rows = []
    trained_pipes: dict[str, Pipeline] = {}

    for name, model in MODELS.items():
        pipe = Pipeline(steps=[("prep", preprocess), ("model", model)])

        hold = evaluate_holdout(pipe, X_train, X_test, y_train, y_test)
        cvm = evaluate_cv(pipe, X, y, folds=5)

        row = {
            "model": name,
            # Holdout
            "holdout_accuracy": hold["accuracy"],
            "holdout_precision": hold["precision"],
            "holdout_recall": hold["recall"],
            "holdout_f1": hold["f1"],
            "holdout_roc_auc": hold["roc_auc"],
            "holdout_confusion_matrix": hold["confusion_matrix"],
            # CV
            **cvm,
        }

        rows.append(row)
        trained_pipes[name] = pipe

        print(f"\n=== {name} ===")
        print("Holdout:", {k: row[k] for k in row if k.startswith("holdout_") and k != "holdout_confusion_matrix"})
        print("CV:", {k: row[k] for k in row if k.startswith("cv_")})
        print("Confusion matrix:", hold["confusion_matrix"])

    results = pd.DataFrame(rows)

    # Ordenar por métrica principal (ROC-AUC CV) y fallback a F1
    results_sorted = results.sort_values(
        by=["cv_roc_auc", "cv_f1", "holdout_roc_auc", "holdout_f1"],
        ascending=False,
    )

    print("\n=== Ranking (mejor arriba) ===")
    print(results_sorted[[
        "model",
        "cv_roc_auc", "cv_f1", "cv_recall", "cv_precision", "cv_accuracy",
        "holdout_roc_auc", "holdout_f1", "holdout_recall", "holdout_precision", "holdout_accuracy",
    ]].to_string(index=False))

    # Guardar CSV de resultados
    results.to_csv("model_comparison_v1_raw.csv", index=False)
    results_sorted.to_csv("model_comparison_v1_ranked.csv", index=False)

    # Guardar mejor pipeline (según ranking)
    best_model_name = results_sorted.iloc[0]["model"]
    best_pipe = trained_pipes[best_model_name]

    # Re-entrenar mejor pipeline con TODO el dataset para exportar
    best_pipe.fit(X, y)
    joblib.dump(best_pipe, f"best_model_pipeline_v1_{best_model_name}.joblib")

    print("\nSaved:")
    print("- model_comparison_v1_raw.csv")
    print("- model_comparison_v1_ranked.csv")
    print(f"- best_model_pipeline_v1_{best_model_name}.joblib")


if __name__ == "__main__":
    main()