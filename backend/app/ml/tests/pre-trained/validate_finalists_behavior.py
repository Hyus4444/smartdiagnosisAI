
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, brier_score_loss
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier


RANDOM_STATE = 42
DATA_FILE = Path("backend") / "app" / "ml" / "data" / "raw" / "diabetes_prediction_dataset.csv"
RESULTS_DIR = Path("results") / "finalists_no_smoking" / "behavior_validation"
TARGET = "diabetes"


def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró {DATA_FILE.resolve()}. Pon el script en la misma carpeta del dataset."
        )
    df = pd.read_csv(DATA_FILE)
    if "gender" in df.columns:
        df = df[df["gender"] != "Other"].copy()
    if "smoking_history" in df.columns:
        df = df.drop(columns=["smoking_history"])
    return df


def build_preprocessor(X):
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

    return ColumnTransformer([
        ("num", num_pipe, numeric_features),
        ("cat", cat_pipe, categorical_features),
    ])


def get_models():
    return {
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


def evaluate(y_true, proba, threshold=0.5):
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    return {
        "threshold": threshold,
        "accuracy": accuracy_score(y_true, pred),
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred, zero_division=0),
        "f1": f1_score(y_true, pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, proba),
        "pr_auc": average_precision_score(y_true, proba),
        "brier_score": brier_score_loss(y_true, proba),
        "specificity": specificity,
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def threshold_sweep(y_true, proba):
    rows = []
    for t in np.arange(0.05, 0.95, 0.05):
        row = evaluate(y_true, proba, threshold=float(np.round(t, 2)))
        rows.append(row)
    return pd.DataFrame(rows)


def choose_threshold_for_target_recall(sweep_df, target_recall=0.90):
    eligible = sweep_df[sweep_df["recall"] >= target_recall].copy()
    if eligible.empty:
        best = sweep_df.sort_values(["recall", "f1"], ascending=False).iloc[0]
    else:
        best = eligible.sort_values(["precision", "f1", "specificity"], ascending=False).iloc[0]
    return best.to_dict()


def save_confusion_matrix_png(cm, labels, outpath, title):
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, interpolation="nearest")
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=labels,
        yticklabels=labels,
        ylabel="Real",
        xlabel="Predicho",
        title=title,
    )

    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j, i, format(cm[i, j], "d"),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black"
            )
    fig.tight_layout()
    fig.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close(fig)


def save_calibration_plot(y_true, proba, outpath, title):
    frac_pos, mean_pred = calibration_curve(y_true, proba, n_bins=10, strategy="quantile")
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot([0, 1], [0, 1], linestyle="--")
    ax.plot(mean_pred, frac_pos, marker="o")
    ax.set_xlabel("Probabilidad predicha")
    ax.set_ylabel("Frecuencia observada")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close(fig)


def profile_variable(model, X_ref, variable_name, values):
    rows = []
    base_row = X_ref.iloc[[0]].copy()

    for value in values:
        row = base_row.copy()
        row[variable_name] = value
        proba = float(model.predict_proba(row)[:, 1][0])
        rows.append({"variable": variable_name, "value": value, "predicted_risk": proba})
    return pd.DataFrame(rows)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=RANDOM_STATE
    )
    X_valid, X_test, y_valid, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=RANDOM_STATE
    )

    preprocessor = build_preprocessor(X_train)
    models = get_models()

    default_rows = []
    target_rows = []

    # perfil base para estabilidad
    medians = X_train.select_dtypes(include=["number", "bool"]).median()
    mode_gender = X_train["gender"].mode().iloc[0] if "gender" in X_train.columns else None
    ref = pd.DataFrame([{
        "gender": mode_gender,
        "age": float(medians.get("age", 50)),
        "hypertension": int(round(medians.get("hypertension", 0))),
        "heart_disease": int(round(medians.get("heart_disease", 0))),
        "bmi": float(medians.get("bmi", 28)),
        "HbA1c_level": 6.0,
        "blood_glucose_level": float(medians.get("blood_glucose_level", 140)),
    }])

    for model_name, model in models.items():
        print(f"\n=== Validando comportamiento {model_name} ===")
        raw_pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])
        raw_pipe.fit(X_train, y_train)

        # raw
        raw_proba_test = raw_pipe.predict_proba(X_test)[:, 1]
        raw_default = {"model": model_name, "variant": "raw"}
        raw_default.update(evaluate(y_test, raw_proba_test, threshold=0.5))
        default_rows.append(raw_default)

        raw_sweep = threshold_sweep(y_valid, raw_pipe.predict_proba(X_valid)[:, 1])
        raw_sweep.to_csv(RESULTS_DIR / f"{model_name}_raw_threshold_sweep.csv", index=False)
        best_raw = choose_threshold_for_target_recall(raw_sweep, target_recall=0.90)
        raw_target = {"model": model_name, "variant": "raw"}
        raw_target.update(evaluate(y_test, raw_proba_test, threshold=float(best_raw["threshold"])))
        target_rows.append(raw_target)

        raw_cm = confusion_matrix(y_test, (raw_proba_test >= 0.5).astype(int))
        save_confusion_matrix_png(raw_cm, ["No diabetes", "Diabetes"],
                                  RESULTS_DIR / f"{model_name}_raw_confusion_matrix_t050.png",
                                  f"{model_name} - Matriz de confusión (t=0.50)")
        save_calibration_plot(y_test, raw_proba_test,
                              RESULTS_DIR / f"{model_name}_raw_calibration_curve.png",
                              f"{model_name} - Curva de calibración")

        # sigmoid calibration
        calib_pipe = CalibratedClassifierCV(raw_pipe, method="sigmoid", cv=3)
        calib_pipe.fit(X_train, y_train)
        calib_proba_test = calib_pipe.predict_proba(X_test)[:, 1]

        calib_default = {"model": model_name, "variant": "sigmoid"}
        calib_default.update(evaluate(y_test, calib_proba_test, threshold=0.5))
        default_rows.append(calib_default)

        calib_sweep = threshold_sweep(y_valid, calib_pipe.predict_proba(X_valid)[:, 1])
        calib_sweep.to_csv(RESULTS_DIR / f"{model_name}_sigmoid_threshold_sweep.csv", index=False)
        best_calib = choose_threshold_for_target_recall(calib_sweep, target_recall=0.90)
        calib_target = {"model": model_name, "variant": "sigmoid"}
        calib_target.update(evaluate(y_test, calib_proba_test, threshold=float(best_calib["threshold"])))
        target_rows.append(calib_target)

        calib_cm = confusion_matrix(y_test, (calib_proba_test >= 0.5).astype(int))
        save_confusion_matrix_png(calib_cm, ["No diabetes", "Diabetes"],
                                  RESULTS_DIR / f"{model_name}_sigmoid_confusion_matrix_t050.png",
                                  f"{model_name} calibrado - Matriz de confusión (t=0.50)")
        save_calibration_plot(y_test, calib_proba_test,
                              RESULTS_DIR / f"{model_name}_sigmoid_calibration_curve.png",
                              f"{model_name} calibrado - Curva de calibración")

        # profiles
        hba1c_values = np.round(np.arange(5.5, 7.1, 0.1), 1)
        glucose_values = list(range(120, 221, 10))
        raw_hba1c = profile_variable(raw_pipe, ref, "HbA1c_level", hba1c_values)
        raw_hba1c["model"] = model_name
        raw_hba1c["variant"] = "raw"
        raw_hba1c.to_csv(RESULTS_DIR / f"{model_name}_raw_hba1c_profile.csv", index=False)

        raw_glu = profile_variable(raw_pipe, ref, "blood_glucose_level", glucose_values)
        raw_glu["model"] = model_name
        raw_glu["variant"] = "raw"
        raw_glu.to_csv(RESULTS_DIR / f"{model_name}_raw_glucose_profile.csv", index=False)

        calib_hba1c = profile_variable(calib_pipe, ref, "HbA1c_level", hba1c_values)
        calib_hba1c["model"] = model_name
        calib_hba1c["variant"] = "sigmoid"
        calib_hba1c.to_csv(RESULTS_DIR / f"{model_name}_sigmoid_hba1c_profile.csv", index=False)

        calib_glu = profile_variable(calib_pipe, ref, "blood_glucose_level", glucose_values)
        calib_glu["model"] = model_name
        calib_glu["variant"] = "sigmoid"
        calib_glu.to_csv(RESULTS_DIR / f"{model_name}_sigmoid_glucose_profile.csv", index=False)

    default_df = pd.DataFrame(default_rows).sort_values(
        by=["roc_auc", "recall", "pr_auc", "f1", "precision"], ascending=False
    )
    target_df = pd.DataFrame(target_rows).sort_values(
        by=["recall", "precision", "f1", "specificity"], ascending=False
    )

    default_df.to_csv(RESULTS_DIR / "behavior_default_threshold_results.csv", index=False)
    target_df.to_csv(RESULTS_DIR / "behavior_target_recall_results.csv", index=False)

    print("\nListo. Validaciones guardadas en:")
    print(RESULTS_DIR.resolve())


if __name__ == "__main__":
    main()
