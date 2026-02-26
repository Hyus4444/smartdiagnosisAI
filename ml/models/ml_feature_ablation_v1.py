
"""
ML Feature Ablation (V1)
- Compares models WITH vs WITHOUT one-hot smoking_history
- Uses reproducible sklearn Pipelines (preprocess + model)
- Evaluates with holdout split + optional cross-validation

Dataset expected:
- diabetes_prediction_dataset.csv

Run:
    python ml_feature_ablation_v1.py
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from dataclasses import dataclass
from typing import Dict, List, Tuple

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    accuracy_score,
    precision_score,
    recall_score,
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB


DATA_PATH = "ml/data/raw/diabetes_prediction_dataset.csv" 

TARGET = "diabetes"

FEATURES_BASE = [
    "age",
    "gender",
    "bmi",
    "HbA1c_level",
    "blood_glucose_level",
    "hypertension",
    "heart_disease",
]

FEATURES_WITH_SMOKING = FEATURES_BASE + ["smoking_history"]

NUMERIC = ["age", "bmi", "HbA1c_level", "blood_glucose_level"]
BINARY = ["hypertension", "heart_disease"]
CATEGORICAL_BASE = ["gender"]
CATEGORICAL_WITH_SMOKING = ["gender", "smoking_history"]


@dataclass
class ExperimentConfig:
    name: str
    features: List[str]
    categorical: List[str]


def _build_preprocess(categorical_cols: List[str]) -> ColumnTransformer:
    """
    Preprocess:
    - scale numeric
    - one-hot categorical (keeps "No Info" as its own category)
    - passthrough binaries
    """
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
            ("bin", "passthrough", BINARY),
        ],
        remainder="drop",
    )


def _build_model_pipelines(preprocess: ColumnTransformer) -> Dict[str, Pipeline]:
    return {
        "LogReg": Pipeline(
            steps=[
                ("prep", preprocess),
                ("model", LogisticRegression(max_iter=3000)),
            ]
        ),
        "RandomForest": Pipeline(
            steps=[
                ("prep", preprocess),
                ("model", RandomForestClassifier(
                    n_estimators=400,
                    random_state=42,
                    n_jobs=-1,
                )),
            ]
        ),
        "SVM": Pipeline(
            steps=[
                ("prep", preprocess),
                ("model", SVC(probability=True)),
            ]
        ),
        "GaussianNB": Pipeline(
            steps=[
                ("prep", preprocess),
                ("model", GaussianNB()),
            ]
        ),
    }


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalize expected columns
    # gender and smoking_history are usually strings; ensure consistent casing
    if "gender" in df.columns:
        df["gender"] = df["gender"].astype(str).str.strip().str.lower()

    if "smoking_history" in df.columns:
        df["smoking_history"] = df["smoking_history"].astype(str).str.strip().str.lower()

    # Ensure binary ints
    for col in ["hypertension", "heart_disease", TARGET]:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # Ensure numerics
    for col in ["age", "bmi", "HbA1c_level", "blood_glucose_level"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows missing required numeric fields (minimal sanitation)
    required_numeric = [c for c in NUMERIC if c in df.columns]
    df = df.dropna(subset=required_numeric)

    return df


def eval_holdout(pipe: Pipeline, X_train, X_test, y_train, y_test) -> Dict[str, float]:
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, "predict_proba") else None

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
    }
    if y_proba is not None:
        metrics["roc_auc"] = float(roc_auc_score(y_test, y_proba))
    else:
        metrics["roc_auc"] = float("nan")

    return metrics


def eval_cv(pipe: Pipeline, X, y, folds: int = 5, seed: int = 42) -> Dict[str, float]:
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    scoring = {
        "accuracy": "accuracy",
        "f1": "f1",
        "precision": "precision",
        "recall": "recall",
        "roc_auc": "roc_auc",
    }
    out = cross_validate(pipe, X, y, cv=cv, scoring=scoring, n_jobs=-1)
    return {k: float(np.mean(v)) for k, v in out.items() if k.startswith("test_")}


def run_experiment(df: pd.DataFrame, cfg: ExperimentConfig, do_cv: bool = True) -> pd.DataFrame:
    X = df[cfg.features]
    y = df[TARGET].astype(int)

    # Holdout split (fixed)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocess = _build_preprocess(cfg.categorical)
    models = _build_model_pipelines(preprocess)

    rows = []

    for model_name, pipe in models.items():
        hold = eval_holdout(pipe, X_train, X_test, y_train, y_test)
        row = {
            "experiment": cfg.name,
            "model": model_name,
            "holdout_roc_auc": hold["roc_auc"],
            "holdout_f1": hold["f1"],
            "holdout_precision": hold["precision"],
            "holdout_recall": hold["recall"],
            "holdout_accuracy": hold["accuracy"],
        }

        if do_cv:
            cvm = eval_cv(pipe, X, y, folds=5, seed=42)
            row.update({
                "cv_roc_auc": cvm.get("test_roc_auc", float("nan")),
                "cv_f1": cvm.get("test_f1", float("nan")),
                "cv_precision": cvm.get("test_precision", float("nan")),
                "cv_recall": cvm.get("test_recall", float("nan")),
                "cv_accuracy": cvm.get("test_accuracy", float("nan")),
            })

        rows.append(row)

    return pd.DataFrame(rows)


def main():
    df = pd.read_csv(DATA_PATH)
    df = _clean_df(df)

    configs = [
        ExperimentConfig(
            name="A_without_smoking_history",
            features=FEATURES_BASE,
            categorical=CATEGORICAL_BASE,
        ),
        ExperimentConfig(
            name="B_with_smoking_history_onehot",
            features=FEATURES_WITH_SMOKING,
            categorical=CATEGORICAL_WITH_SMOKING,
        ),
    ]

    results = []
    for cfg in configs:
        res = run_experiment(df, cfg, do_cv=True)
        results.append(res)

    out = pd.concat(results, ignore_index=True)

    # Compute delta (B - A) per model for quick decision
    pivot = out.pivot(index="model", columns="experiment", values=["holdout_roc_auc", "holdout_f1", "cv_roc_auc", "cv_f1"])
    pivot.columns = [f"{a}__{b}" for a, b in pivot.columns]

    if "holdout_roc_auc__B_with_smoking_history_onehot" in pivot.columns:
        pivot["delta_holdout_roc_auc"] = (
            pivot["holdout_roc_auc__B_with_smoking_history_onehot"]
            - pivot["holdout_roc_auc__A_without_smoking_history"]
        )
        pivot["delta_holdout_f1"] = (
            pivot["holdout_f1__B_with_smoking_history_onehot"]
            - pivot["holdout_f1__A_without_smoking_history"]
        )
        pivot["delta_cv_roc_auc"] = (
            pivot["cv_roc_auc__B_with_smoking_history_onehot"]
            - pivot["cv_roc_auc__A_without_smoking_history"]
        )
        pivot["delta_cv_f1"] = (
            pivot["cv_f1__B_with_smoking_history_onehot"]
            - pivot["cv_f1__A_without_smoking_history"]
        )

    print("\n=== Raw Results (holdout + CV means) ===")
    print(out.sort_values(["model", "experiment"]).to_string(index=False))

    print("\n=== Pivot + Deltas (B - A) ===")
    print(pivot.to_string())

    # Save outputs
    out.to_csv("ablation_results_raw.csv", index=False)
    pivot.to_csv("ablation_results_pivot.csv")

    print("\nSaved:")
    print("- ablation_results_raw.csv")
    print("- ablation_results_pivot.csv")


if __name__ == "__main__":
    main()
