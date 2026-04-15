
import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier


RANDOM_STATE = 42
DATA_FILE = Path("backend") / "app" / "ml" / "data" / "raw" / "diabetes_prediction_dataset.csv"
RESULTS_DIR = Path("results") / "finalists_no_smoking"
TARGET = "diabetes"


def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró {DATA_FILE.resolve()}."
        )
    df = pd.read_csv(DATA_FILE)

    # Limpieza acordada
    if "gender" in df.columns:
        df = df[df["gender"] != "Other"].copy()

    if "smoking_history" in df.columns:
        df = df.drop(columns=["smoking_history"])

    required = {"gender", "age", "hypertension", "heart_disease", "bmi", "HbA1c_level", "blood_glucose_level", TARGET}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing)}")

    return df


def build_preprocessor(X: pd.DataFrame):
    numeric_features = X.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [c for c in X.columns if c not in numeric_features]

    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer([
        ("num", num_pipe, numeric_features),
        ("cat", cat_pipe, categorical_features),
    ])
    return preprocessor


def get_models():
    return {
        "LogReg": LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            solver="lbfgs",
            random_state=RANDOM_STATE
        ),
        "SVM": SVC(
            kernel="rbf",
            C=3.0,
            gamma="scale",
            class_weight="balanced",
            probability=True,
            random_state=RANDOM_STATE
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            n_jobs=-1,
            random_state=RANDOM_STATE
        ),
        "HistGB": HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_iter=300,
            max_leaf_nodes=31,
            min_samples_leaf=30,
            l2_regularization=0.1,
            random_state=RANDOM_STATE
        ),
    }


def compute_metrics(y_true, proba, preds):
    tn, fp, fn, tp = confusion_matrix(y_true, preds).ravel()
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    npv = tn / (tn + fn) if (tn + fn) else 0.0
    return {
        "accuracy": accuracy_score(y_true, preds),
        "precision": precision_score(y_true, preds, zero_division=0),
        "recall": recall_score(y_true, preds, zero_division=0),
        "f1": f1_score(y_true, preds, zero_division=0),
        "roc_auc": roc_auc_score(y_true, proba),
        "pr_auc": average_precision_score(y_true, proba),
        "specificity": specificity,
        "npv": npv,
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    preprocessor = build_preprocessor(X_train)
    models = get_models()

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = {
        "roc_auc": "roc_auc",
        "average_precision": "average_precision",
        "recall": "recall",
        "precision": "precision",
        "f1": "f1",
        "accuracy": "accuracy",
    }

    holdout_rows = []
    cv_rows = []
    metadata = {
        "random_state": RANDOM_STATE,
        "target": TARGET,
        "dropped_columns": ["smoking_history"],
        "drop_other_gender": True,
        "data_file": str(DATA_FILE),
        "results_dir": str(RESULTS_DIR),
        "models": list(models.keys()),
        "features": X.columns.tolist(),
        "n_rows": int(len(df)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "positive_rate_full": float(y.mean()),
    }

    for model_name, model in models.items():
        print(f"\n=== Entrenando {model_name} ===")
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])

        cv_result = cross_validate(
            pipe, X_train, y_train, cv=cv, scoring=scoring, n_jobs=1, return_train_score=False
        )

        cv_row = {"model": model_name}
        for metric_name, values in cv_result.items():
            if metric_name.startswith("test_"):
                clean_name = metric_name.replace("test_", "cv_")
                cv_row[clean_name] = float(np.mean(values))
                cv_row[f"{clean_name}_std"] = float(np.std(values))
        cv_rows.append(cv_row)

        pipe.fit(X_train, y_train)
        proba = pipe.predict_proba(X_test)[:, 1]
        preds = (proba >= 0.5).astype(int)

        holdout_row = {"model": model_name}
        holdout_row.update(compute_metrics(y_test, proba, preds))
        holdout_rows.append(holdout_row)

        pred_df = pd.DataFrame({
            "y_true": y_test.values,
            "y_proba": proba,
            "y_pred_threshold_050": preds
        })
        pred_df.to_csv(RESULTS_DIR / f"{model_name}_test_predictions.csv", index=False)

    holdout_df = pd.DataFrame(holdout_rows).sort_values(
        by=["roc_auc", "recall", "pr_auc", "f1", "precision"],
        ascending=False
    )
    cv_df = pd.DataFrame(cv_rows).sort_values(
        by=["cv_roc_auc", "cv_recall", "cv_average_precision", "cv_f1", "cv_precision"],
        ascending=False
    )

    merged = holdout_df.merge(cv_df, on="model", how="left")
    merged["ranking_score"] = (
        merged["roc_auc"] * 0.35 +
        merged["recall"] * 0.25 +
        merged["pr_auc"] * 0.20 +
        merged["f1"] * 0.10 +
        merged["precision"] * 0.10
    )
    merged = merged.sort_values("ranking_score", ascending=False)

    holdout_df.to_csv(RESULTS_DIR / "finalists_holdout_results.csv", index=False)
    cv_df.to_csv(RESULTS_DIR / "finalists_cv_results.csv", index=False)
    merged.to_csv(RESULTS_DIR / "finalists_summary_ranked.csv", index=False)

    with open(RESULTS_DIR / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("\nListo. Archivos guardados en:")
    print(RESULTS_DIR.resolve())


if __name__ == "__main__":
    main()
