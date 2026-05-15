import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, brier_score_loss
)
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV

RANDOM_STATE = 42
TARGET = 'diabetes'
DATA_FILE = 'C:/Users/Jairo/Documents/Repositorios/Proyecto de grado/SmartDiagnosisAI/backend/app/ml/data/raw/diabetes_prediction_dataset.csv'
OUTDIR = Path('results/svm_basic_experiments')
OUTDIR.mkdir(parents=True, exist_ok=True)


def load_data():
    df = pd.read_csv(DATA_FILE)
    if 'gender' in df.columns:
        df = df[df['gender'] != 'Other'].copy()
    if 'smoking_history' in df.columns:
        df = df.drop(columns=['smoking_history'])
    return df


def build_preprocessor(X):
    cat_cols = X.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    num_cols = [c for c in X.columns if c not in cat_cols]
    pre = ColumnTransformer([
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
        ]), num_cols),
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore')),
        ]), cat_cols),
    ])
    return pre


def make_model(preprocessor, c, gamma, class_weight, calibration):
    if calibration is None:
        return Pipeline([
            ('preprocessor', preprocessor),
            ('svm', SVC(
                kernel='rbf',
                C=c,
                gamma=gamma,
                class_weight=class_weight,
                probability=True,
                random_state=RANDOM_STATE,
            ))
        ])

    base = Pipeline([
        ('preprocessor', preprocessor),
        ('svm', SVC(
            kernel='rbf',
            C=c,
            gamma=gamma,
            class_weight=class_weight,
            probability=False,
            random_state=RANDOM_STATE,
        ))
    ])
    return CalibratedClassifierCV(base, method=calibration, cv=3)


def pick_threshold(y_true, probs, min_recall=0.90):
    thresholds = np.round(np.arange(0.05, 0.51, 0.05), 2)
    rows = []
    for thr in thresholds:
        pred = (probs >= thr).astype(int)
        rows.append({
            'threshold': thr,
            'precision': precision_score(y_true, pred, zero_division=0),
            'recall': recall_score(y_true, pred, zero_division=0),
            'f1': f1_score(y_true, pred, zero_division=0),
            'accuracy': accuracy_score(y_true, pred),
        })
    sweep = pd.DataFrame(rows)
    eligible = sweep[sweep['recall'] >= min_recall].copy()
    if not eligible.empty:
        best = eligible.sort_values(['f1', 'precision', 'accuracy'], ascending=False).iloc[0]
    else:
        best = sweep.sort_values(['recall', 'f1'], ascending=False).iloc[0]
    return float(best['threshold']), sweep


def evaluate(y_true, probs, threshold):
    pred = (probs >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    return {
        'threshold': threshold,
        'accuracy': accuracy_score(y_true, pred),
        'precision': precision_score(y_true, pred, zero_division=0),
        'recall': recall_score(y_true, pred, zero_division=0),
        'f1': f1_score(y_true, pred, zero_division=0),
        'roc_auc': roc_auc_score(y_true, probs),
        'pr_auc': average_precision_score(y_true, probs),
        'brier': brier_score_loss(y_true, probs),
        'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn),
    }


def main():
    df = load_data()
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    pre = build_preprocessor(X_train)

    configs = [
        {'name': 'svm_balanced_sigmoid', 'C': 1.0, 'gamma': 'scale', 'class_weight': 'balanced', 'calibration': 'sigmoid'},
        {'name': 'svm_w13_sigmoid', 'C': 1.0, 'gamma': 0.05, 'class_weight': {0:1, 1:3}, 'calibration': 'sigmoid'},
        {'name': 'svm_w12_sigmoid', 'C': 0.5, 'gamma': 0.05, 'class_weight': {0:1, 1:2}, 'calibration': 'sigmoid'},
        {'name': 'svm_balanced_raw', 'C': 1.0, 'gamma': 'scale', 'class_weight': 'balanced', 'calibration': None},
    ]

    summary_rows = []
    cv_rows = []

    for cfg in configs:
        model = make_model(pre, cfg['C'], cfg['gamma'], cfg['class_weight'], cfg['calibration'])
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
        cv_probs = cross_val_predict(model, X_train, y_train, cv=cv, method='predict_proba', n_jobs=1)[:,1]
        best_thr, sweep = pick_threshold(y_train, cv_probs, min_recall=0.90)
        sweep.to_csv(OUTDIR / f"{cfg['name']}_cv_threshold_sweep.csv", index=False)

        model.fit(X_train, y_train)
        test_probs = model.predict_proba(X_test)[:,1]

        row_default = evaluate(y_test, test_probs, 0.5)
        row_default.update({'config': cfg['name'], 'selection': 'default_0.50'})
        row_tuned = evaluate(y_test, test_probs, best_thr)
        row_tuned.update({'config': cfg['name'], 'selection': 'tuned_for_recall'})
        summary_rows.extend([row_default, row_tuned])

        cv_rows.append({
            'config': cfg['name'],
            'chosen_threshold': best_thr,
            'cv_roc_auc': roc_auc_score(y_train, cv_probs),
            'cv_pr_auc': average_precision_score(y_train, cv_probs),
            'cv_brier': brier_score_loss(y_train, cv_probs),
        })

        pd.DataFrame({'y_true': y_test.values, 'prob': test_probs}).to_csv(
            OUTDIR / f"{cfg['name']}_test_probs.csv", index=False
        )

    summary = pd.DataFrame(summary_rows)
    cvdf = pd.DataFrame(cv_rows)
    summary['rank_score'] = (
        0.30 * summary['recall'] +
        0.20 * summary['roc_auc'] +
        0.15 * summary['pr_auc'] +
        0.15 * summary['f1'] +
        0.10 * summary['precision'] +
        0.10 * (1 - summary['brier'])
    )
    summary = summary.sort_values(['selection', 'rank_score'], ascending=[True, False])
    summary.to_csv(OUTDIR / 'svm_experiments_summary.csv', index=False)
    cvdf.to_csv(OUTDIR / 'svm_experiments_cv_summary.csv', index=False)

    metadata = {
        'data_file': DATA_FILE,
        'target': TARGET,
        'dropped_columns': ['smoking_history'],
        'drop_gender_other': True,
        'configs': configs,
        'test_size': 0.2,
        'random_state': RANDOM_STATE,
    }
    (OUTDIR / 'run_metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(f'Results saved to: {OUTDIR.resolve()}')


if __name__ == '__main__':
    main()
