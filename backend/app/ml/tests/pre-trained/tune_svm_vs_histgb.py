import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    brier_score_loss
)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import SVC
from sklearn.ensemble import HistGradientBoostingClassifier

RANDOM_STATE = 42
DATA_PATH = Path('C:/Users/Jairo/Documents/Repositorios/Proyecto de grado/SmartDiagnosisAI/backend/app/ml/data/raw/diabetes_prediction_dataset.csv')
OUTDIR = Path('results') / 'svm_vs_histgb_tuning'
OUTDIR.mkdir(parents=True, exist_ok=True)


def load_data():
    df = pd.read_csv(DATA_PATH)
    if 'smoking_history' in df.columns:
        df = df.drop(columns=['smoking_history'])
    if 'gender' in df.columns:
        df = df[df['gender'] != 'Other'].copy()
    return df


def build_preprocessor(num_cols, cat_cols):
    num_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    cat_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    return ColumnTransformer([
        ('num', num_pipe, num_cols),
        ('cat', cat_pipe, cat_cols)
    ], remainder='drop')


def metrics_from_probs(y_true, probs, threshold=0.5):
    preds = (probs >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, preds).ravel()
    return {
        'threshold': threshold,
        'accuracy': accuracy_score(y_true, preds),
        'precision': precision_score(y_true, preds, zero_division=0),
        'recall': recall_score(y_true, preds, zero_division=0),
        'f1': f1_score(y_true, preds, zero_division=0),
        'roc_auc': roc_auc_score(y_true, probs),
        'pr_auc': average_precision_score(y_true, probs),
        'brier': brier_score_loss(y_true, probs),
        'fp': int(fp), 'fn': int(fn), 'tp': int(tp), 'tn': int(tn)
    }


def threshold_sweep(y_true, probs, name):
    rows = []
    for thr in np.round(np.arange(0.05, 0.96, 0.05), 2):
        row = metrics_from_probs(y_true, probs, threshold=float(thr))
        row['model'] = name
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUTDIR / f'{name}_threshold_sweep.csv', index=False)
    return out


def target_recall_row(sweep_df, min_recall=0.90):
    cand = sweep_df[sweep_df['recall'] >= min_recall].copy()
    if cand.empty:
        # choose best recall then best f1
        return sweep_df.sort_values(['recall', 'f1', 'precision'], ascending=False).iloc[0].to_dict()
    cand = cand.sort_values(['f1', 'precision', 'threshold'], ascending=[False, False, True])
    return cand.iloc[0].to_dict()


def make_profiles(model, preprocessor, X_train, y_train, base_row, name):
    # Fit model on full training set through pipeline manually for profile generation
    Xtr = preprocessor.fit_transform(X_train)
    model.fit(Xtr, y_train)

    h_vals = np.round(np.arange(5.5, 7.1, 0.1), 1)
    g_vals = np.arange(180, 221, 10)

    h_rows, g_rows = [], []
    for v in h_vals:
        row = base_row.copy()
        row['HbA1c_level'] = float(v)
        X = pd.DataFrame([row])
        p = model.predict_proba(preprocessor.transform(X))[:, 1][0]
        h_rows.append({'HbA1c_level': float(v), 'predicted_risk': float(p)})
    for v in g_vals:
        row = base_row.copy()
        row['blood_glucose_level'] = int(v)
        X = pd.DataFrame([row])
        p = model.predict_proba(preprocessor.transform(X))[:, 1][0]
        g_rows.append({'blood_glucose_level': int(v), 'predicted_risk': float(p)})

    pd.DataFrame(h_rows).to_csv(OUTDIR / f'{name}_hba1c_profile.csv', index=False)
    pd.DataFrame(g_rows).to_csv(OUTDIR / f'{name}_glucose_profile.csv', index=False)


def main():
    df = load_data()
    target_col = 'diabetes'
    y = df[target_col].astype(int)
    X = df.drop(columns=[target_col])
    cat_cols = [c for c in X.columns if X[c].dtype == 'object']
    num_cols = [c for c in X.columns if c not in cat_cols]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    preprocessor = build_preprocessor(num_cols, cat_cols)
    Xtr = preprocessor.fit_transform(X_train)
    Xte = preprocessor.transform(X_test)

    base_pos = float((y_train == 1).mean())
    pos_weight = (1 - base_pos) / base_pos

    svm_variants = {
        'SVM_balanced_C1': SVC(C=1.0, kernel='rbf', gamma='scale', class_weight='balanced', probability=True, random_state=RANDOM_STATE),
        'SVM_balanced_C2': SVC(C=2.0, kernel='rbf', gamma='scale', class_weight='balanced', probability=True, random_state=RANDOM_STATE),
        'SVM_custom_1_2': SVC(C=1.0, kernel='rbf', gamma='scale', class_weight={0:1,1:2}, probability=True, random_state=RANDOM_STATE),
        'SVM_custom_1_3': SVC(C=1.0, kernel='rbf', gamma='scale', class_weight={0:1,1:3}, probability=True, random_state=RANDOM_STATE),
        'SVM_custom_1_4': SVC(C=1.0, kernel='rbf', gamma='scale', class_weight={0:1,1:4}, probability=True, random_state=RANDOM_STATE),
    }

    histgb = HistGradientBoostingClassifier(
        learning_rate=0.05,
        max_depth=6,
        max_iter=300,
        min_samples_leaf=30,
        l2_regularization=0.1,
        random_state=RANDOM_STATE,
    )

    summary_rows = []

    # HistGB baseline + calibrated
    histgb.fit(Xtr, y_train)
    hist_probs = histgb.predict_proba(Xte)[:,1]
    summary_rows.append({'model':'HistGB_raw', **metrics_from_probs(y_test, hist_probs, 0.5)})
    hist_sweep = threshold_sweep(y_test, hist_probs, 'HistGB_raw')
    hist_target = target_recall_row(hist_sweep, 0.90)
    hist_target['model'] = 'HistGB_raw_target_recall'
    summary_rows.append(hist_target)

    hist_cal = CalibratedClassifierCV(histgb, method='sigmoid', cv=3)
    hist_cal.fit(Xtr, y_train)
    hist_cal_probs = hist_cal.predict_proba(Xte)[:,1]
    summary_rows.append({'model':'HistGB_sigmoid', **metrics_from_probs(y_test, hist_cal_probs, 0.5)})
    hist_cal_sweep = threshold_sweep(y_test, hist_cal_probs, 'HistGB_sigmoid')
    hist_cal_target = target_recall_row(hist_cal_sweep, 0.90)
    hist_cal_target['model'] = 'HistGB_sigmoid_target_recall'
    summary_rows.append(hist_cal_target)

    # SVM variants
    best_variant_name = None
    best_variant_score = -1
    best_variant_model = None
    best_variant_probs = None

    for name, model in svm_variants.items():
        model.fit(Xtr, y_train)
        probs = model.predict_proba(Xte)[:,1]
        row = {'model': name, **metrics_from_probs(y_test, probs, 0.5)}
        summary_rows.append(row)
        sweep = threshold_sweep(y_test, probs, name)
        target = target_recall_row(sweep, 0.90)
        target['model'] = f'{name}_target_recall'
        summary_rows.append(target)
        # ranking favoring stable useful screening behavior
        score = 0.35*row['roc_auc'] + 0.25*target['recall'] + 0.2*target['f1'] + 0.1*target['precision'] + 0.1*(1-row['brier'])
        if score > best_variant_score:
            best_variant_score = score
            best_variant_name = name
            best_variant_model = model
            best_variant_probs = probs

    # Calibrated versions of best SVM
    best_base = svm_variants[best_variant_name]
    for method in ['sigmoid', 'isotonic']:
        cal = CalibratedClassifierCV(best_base, method=method, cv=3)
        cal.fit(Xtr, y_train)
        probs = cal.predict_proba(Xte)[:,1]
        row = {'model': f'{best_variant_name}_{method}', **metrics_from_probs(y_test, probs, 0.5)}
        summary_rows.append(row)
        sweep = threshold_sweep(y_test, probs, f'{best_variant_name}_{method}')
        target = target_recall_row(sweep, 0.90)
        target['model'] = f'{best_variant_name}_{method}_target_recall'
        summary_rows.append(target)

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUTDIR / 'svm_vs_histgb_summary.csv', index=False)

    # Final compact comparison table
    display_models = [
        'HistGB_raw', 'HistGB_sigmoid',
        best_variant_name, f'{best_variant_name}_sigmoid', f'{best_variant_name}_isotonic',
        'HistGB_raw_target_recall', 'HistGB_sigmoid_target_recall',
        f'{best_variant_name}_target_recall', f'{best_variant_name}_sigmoid_target_recall', f'{best_variant_name}_isotonic_target_recall'
    ]
    final = summary[summary['model'].isin(display_models)].copy()
    final.to_csv(OUTDIR / 'final_compact_comparison.csv', index=False)

    # Profiles using median-like base patient
    base_row = {
        'gender': 'Female',
        'age': float(X_train['age'].median()),
        'hypertension': 0,
        'heart_disease': 0,
        'bmi': float(X_train['bmi'].median()),
        'HbA1c_level': 6.0,
        'blood_glucose_level': 140,
    }
    make_profiles(HistGradientBoostingClassifier(
        learning_rate=0.05, max_depth=6, max_iter=300,
        min_samples_leaf=30, l2_regularization=0.1, random_state=RANDOM_STATE
    ), build_preprocessor(num_cols, cat_cols), X_train, y_train, base_row, 'HistGB_raw')

    best_svm_for_profiles = CalibratedClassifierCV(
        svm_variants[best_variant_name], method='sigmoid', cv=3
    )
    make_profiles(best_svm_for_profiles, build_preprocessor(num_cols, cat_cols), X_train, y_train, base_row, f'{best_variant_name}_sigmoid')

    metadata = {
        'data_path': str(DATA_PATH),
        'output_dir': str(OUTDIR),
        'rows_used': int(len(df)),
        'positive_rate': float(y.mean()),
        'best_svm_variant': best_variant_name,
        'random_state': RANDOM_STATE,
        'notes': [
            'smoking_history removed',
            'gender==Other removed',
            'SVM tuned via class_weight and C',
            'final decision should balance discrimination, sensitivity and stability'
        ]
    }
    with open(OUTDIR / 'run_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print('Proceso completado.')
    print(f'Mejor variante SVM: {best_variant_name}')
    print(f'Resultados en: {OUTDIR.resolve()}')

if __name__ == '__main__':
    main()
