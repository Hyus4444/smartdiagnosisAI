from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings("ignore")

RANDOM_STATE = 42
TARGET = "diabetes"
SMOKING_COL = "smoking_history"
DATA_PATH = Path("backend\\app\\ml\\data\\raw\\diabetes_prediction_dataset.csv")
OUTPUT_DIR = Path("results")
DROP_OTHER_GENDER = True


def build_models():
    return {
        "LogReg": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
        "GaussianNB": GaussianNB(),
        "SVM": SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            class_weight="balanced",
            probability=True,
            random_state=RANDOM_STATE,
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "ExtraTrees": ExtraTreesClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "HistGB": HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_iter=300,
            max_leaf_nodes=31,
            min_samples_leaf=20,
            l2_regularization=0.0,
            random_state=RANDOM_STATE,
        ),
    }



def make_preprocessor(df_features: pd.DataFrame):
    categorical_cols = [c for c in df_features.columns if df_features[c].dtype == "object"]
    numeric_cols = [c for c in df_features.columns if c not in categorical_cols]

    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    return ColumnTransformer([
        ("num", numeric_pipe, numeric_cols),
        ("cat", categorical_pipe, categorical_cols),
    ])



def make_histgb_preprocessor(df_features: pd.DataFrame):
    categorical_cols = [c for c in df_features.columns if df_features[c].dtype == "object"]
    numeric_cols = [c for c in df_features.columns if c not in categorical_cols]

    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    return ColumnTransformer([
        ("num", numeric_pipe, numeric_cols),
        ("cat", categorical_pipe, categorical_cols),
    ])



def evaluate_scenario(df: pd.DataFrame, scenario_name: str, outdir: Path):
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
        "pr_auc": "average_precision",
    }

    holdout_rows = []
    cv_rows = []

    for model_name, model in build_models().items():
        preprocessor = make_histgb_preprocessor(X) if model_name == "HistGB" else make_preprocessor(X)

        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])

        cv_result = cross_validate(
            pipe,
            X_train,
            y_train,
            cv=cv,
            scoring=scoring,
            n_jobs=1,
            return_train_score=False,
        )

        cv_row = {"scenario": scenario_name, "model": model_name}
        for metric in scoring:
            vals = cv_result[f"test_{metric}"]
            cv_row[f"cv_mean_{metric}"] = float(np.mean(vals))
            cv_row[f"cv_std_{metric}"] = float(np.std(vals))
        cv_rows.append(cv_row)

        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]

        holdout_rows.append(
            {
                "scenario": scenario_name,
                "model": model_name,
                "holdout_accuracy": accuracy_score(y_test, y_pred),
                "holdout_precision": precision_score(y_test, y_pred, zero_division=0),
                "holdout_recall": recall_score(y_test, y_pred, zero_division=0),
                "holdout_f1": f1_score(y_test, y_pred, zero_division=0),
                "holdout_roc_auc": roc_auc_score(y_test, y_prob),
                "holdout_pr_auc": average_precision_score(y_test, y_prob),
            }
        )

    holdout_df = pd.DataFrame(holdout_rows).sort_values(["holdout_roc_auc", "holdout_recall"], ascending=False)
    cv_df = pd.DataFrame(cv_rows).sort_values(["cv_mean_roc_auc", "cv_mean_recall"], ascending=False)

    merged = holdout_df.merge(cv_df, on=["scenario", "model"], how="left")
    merged["rank_score"] = (
        0.35 * merged["holdout_roc_auc"]
        + 0.25 * merged["holdout_recall"]
        + 0.20 * merged["holdout_pr_auc"]
        + 0.10 * merged["holdout_f1"]
        + 0.10 * merged["holdout_precision"]
    )
    merged = merged.sort_values("rank_score", ascending=False)

    holdout_df.to_csv(outdir / f"{scenario_name}_holdout_results.csv", index=False)
    cv_df.to_csv(outdir / f"{scenario_name}_cv_results.csv", index=False)
    merged.to_csv(outdir / f"{scenario_name}_summary_ranked.csv", index=False)
    return merged



def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo '{DATA_PATH}'. Pon el script en la misma carpeta del dataset o ajusta DATA_PATH."
        )

    df = pd.read_csv(DATA_PATH)

    if TARGET not in df.columns:
        raise ValueError(f"No se encontró la columna objetivo '{TARGET}'.")
    if SMOKING_COL not in df.columns:
        raise ValueError(f"No se encontró la columna '{SMOKING_COL}'.")

    if DROP_OTHER_GENDER and "gender" in df.columns:
        df = df[df["gender"] != "Other"].copy()

    with_smoking = df.copy()
    without_smoking = df.drop(columns=[SMOKING_COL]).copy()

    summary_with = evaluate_scenario(with_smoking, "with_smoking_history", OUTPUT_DIR)
    summary_without = evaluate_scenario(without_smoking, "without_smoking_history", OUTPUT_DIR)

    comparison = summary_with[[
        "model",
        "rank_score",
        "holdout_accuracy",
        "holdout_precision",
        "holdout_recall",
        "holdout_f1",
        "holdout_roc_auc",
        "holdout_pr_auc",
    ]].merge(
        summary_without[[
            "model",
            "rank_score",
            "holdout_accuracy",
            "holdout_precision",
            "holdout_recall",
            "holdout_f1",
            "holdout_roc_auc",
            "holdout_pr_auc",
        ]],
        on="model",
        suffixes=("_with", "_without"),
    )

    for metric in [
        "rank_score",
        "holdout_accuracy",
        "holdout_precision",
        "holdout_recall",
        "holdout_f1",
        "holdout_roc_auc",
        "holdout_pr_auc",
    ]:
        comparison[f"delta_{metric}_without_minus_with"] = (
            comparison[f"{metric}_without"] - comparison[f"{metric}_with"]
        )

    comparison = comparison.sort_values("rank_score_without", ascending=False)
    comparison.to_csv(OUTPUT_DIR / "with_vs_without_smoking_comparison.csv", index=False)

    metadata = {
        "random_state": RANDOM_STATE,
        "target": TARGET,
        "smoking_column": SMOKING_COL,
        "drop_other_gender": DROP_OTHER_GENDER,
        "data_path": str(DATA_PATH),
        "output_dir": str(OUTPUT_DIR),
        "models": list(build_models().keys()),
        "ranking_formula": {
            "holdout_roc_auc": 0.35,
            "holdout_recall": 0.25,
            "holdout_pr_auc": 0.20,
            "holdout_f1": 0.10,
            "holdout_precision": 0.10,
        },
    }
    (OUTPUT_DIR / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("Proceso finalizado.")
    print(f"Resultados guardados en: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
