
import json
from pathlib import Path

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

DATA_FILE = "C:/Users/Jairo/Documents/Repositorios/Proyecto de grado/SmartDiagnosisAI/backend/app/ml/data/raw/diabetes_prediction_dataset.csv"
OUTPUT_DIR = Path("results/svm_w13_final_threshold")
TARGET = "diabetes"
DROP_COLS = ["smoking_history"]
DROP_GENDER_OTHER = True
TEST_SIZE = 0.2
RANDOM_STATE = 42
THRESHOLDS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]

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

def build_model(X):
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
        random_state=RANDOM_STATE,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", CalibratedClassifierCV(estimator=base_svc, method="sigmoid", cv=3)),
        ]
    )

def evaluate_thresholds(y_true, probs, thresholds):
    rows = []
    for thr in thresholds:
        preds = (probs >= thr).astype(int)
        acc = accuracy_score(y_true, preds)
        prec = precision_score(y_true, preds, zero_division=0)
        rec = recall_score(y_true, preds, zero_division=0)
        f1 = f1_score(y_true, preds, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_true, preds).ravel()
        rows.append({
            "threshold": thr,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        })
    return pd.DataFrame(rows)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    model = build_model(X)
    model.fit(X_train, y_train)
    test_probs = model.predict_proba(X_test)[:, 1]

    threshold_df = evaluate_thresholds(y_test.to_numpy(), test_probs, THRESHOLDS)
    global_df = pd.DataFrame([{
        "roc_auc": roc_auc_score(y_test, test_probs),
        "pr_auc": average_precision_score(y_test, test_probs),
        "brier": brier_score_loss(y_test, test_probs),
        "n_test": int(len(y_test)),
        "positives_test": int(y_test.sum()),
        "negatives_test": int((1 - y_test).sum()),
    }])

    probs_df = X_test.copy()
    probs_df[TARGET] = y_test.values
    probs_df["pred_proba"] = test_probs

    threshold_df.to_csv(OUTPUT_DIR / "svm_w13_sigmoid_threshold_selection.csv", index=False)
    global_df.to_csv(OUTPUT_DIR / "svm_w13_sigmoid_global_metrics.csv", index=False)
    probs_df.to_csv(OUTPUT_DIR / "svm_w13_sigmoid_test_probs.csv", index=False)

    meta = {
        "data_file": DATA_FILE,
        "output_dir": str(OUTPUT_DIR),
        "model": {
            "name": "svm_w13_sigmoid",
            "kernel": "rbf",
            "C": 1.0,
            "gamma": 0.05,
            "class_weight": {"0": 1, "1": 3},
            "calibration": "sigmoid",
        },
        "thresholds_tested": THRESHOLDS,
        "dropped_columns": DROP_COLS,
        "drop_gender_other": DROP_GENDER_OTHER,
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
    }

    with open(OUTPUT_DIR / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("Proceso completado.")
    print(f"Resultados guardados en: {OUTPUT_DIR.resolve()}")

if __name__ == "__main__":
    main()
