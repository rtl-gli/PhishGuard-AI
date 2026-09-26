from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold

from src.domains import registrable_domain
from src.hard_cases import build_feature_frame, generate_complex_legitimate_urls
from src.project import CANDIDATE_MODEL_PATH, load_dataset_split


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VALIDATION_DIR = PROJECT_ROOT / "data" / "validation"
THRESHOLDS = [
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
    0.85,
]


def _print_threshold_report(name, model, features, labels):
    probabilities = model.predict_proba(features)[
        :, list(model.classes_).index(1)
    ]
    print(f"\n=== {name} ===")
    print(f"ROC-AUC: {roc_auc_score(labels, probabilities):.4f}")
    print("Threshold sweep:")
    for threshold in THRESHOLDS:
        predictions = (probabilities >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(
            labels,
            predictions,
            labels=[0, 1],
        ).ravel()
        print(
            f"{threshold:.2f}: "
            f"precision={precision_score(labels, predictions, zero_division=0):.4f} "
            f"recall={recall_score(labels, predictions, zero_division=0):.4f} "
            f"FPR={fp / (fp + tn):.4f} FNR={fn / (fn + tp):.4f} "
            f"FP={fp} FN={fn}"
        )


def _cross_validate_augmented(model, train_df, feature_columns):
    folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []
    groups = train_df["url"].map(registrable_domain)
    for train_indices, validation_indices in folds.split(
        train_df[feature_columns],
        train_df["label"],
        groups,
    ):
        fold_train = train_df.iloc[train_indices]
        fold_validation = train_df.iloc[validation_indices]
        hard_urls = generate_complex_legitimate_urls(
            fold_train.loc[fold_train["label"] == 0, "url"],
        )
        hard_cases = build_feature_frame(hard_urls, label=0)
        fold_features = pd.concat(
            [
                fold_train[feature_columns],
                hard_cases[feature_columns],
            ],
            ignore_index=True,
        )
        fold_labels = pd.concat(
            [fold_train["label"], hard_cases["label"]],
            ignore_index=True,
        )
        fold_model = clone(model)
        fold_model.fit(fold_features, fold_labels)
        scores.append(
            fold_model.score(
                fold_validation[feature_columns],
                fold_validation["label"],
            )
        )
    return scores


def _load_hard_case_file(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Hard-case file not found: {path}. "
            "Create both validation CSVs with "
            "'python -m src.prepare_hard_cases'."
        )
    cases = pd.read_csv(path)
    missing_columns = {"url", "label"} - set(cases.columns)
    if missing_columns:
        raise ValueError(
            f"{path.name} is missing columns: {', '.join(sorted(missing_columns))}"
        )
    if cases["url"].isna().any() or cases["label"].isna().any():
        raise ValueError(f"{path.name} contains missing URLs or labels.")
    if not set(cases["label"].unique()).issubset({0, 1}):
        raise ValueError(f"{path.name} labels must be 0 or 1.")
    return cases


def main():
    model_data = joblib.load(CANDIDATE_MODEL_PATH)
    model = model_data["model"]
    feature_columns = model_data["features"]

    train_df = load_dataset_split("train")
    validation_df = load_dataset_split("val")
    test_df = load_dataset_split("test")

    print("=== Five-fold CV with fold-local hard-negative generation ===")
    cv_scores = _cross_validate_augmented(
        model,
        train_df,
        feature_columns,
    )
    print(f"Fold accuracies: {[round(score, 4) for score in cv_scores]}")
    print(f"Mean accuracy: {np.mean(cv_scores):.4f}")
    print(f"Standard deviation: {np.std(cv_scores):.4f}")

    for split_name, split_df in (
        ("Validation split", validation_df),
        ("Held-out test split", test_df),
    ):
        _print_threshold_report(
            split_name,
            model,
            split_df[feature_columns],
            split_df["label"],
        )

    legitimate_cases = _load_hard_case_file(
        VALIDATION_DIR / "legitimate_hard_cases.csv"
    )
    phishing_cases = _load_hard_case_file(
        VALIDATION_DIR / "phishing_hard_cases.csv"
    )
    hard_cases = pd.concat(
        [legitimate_cases, phishing_cases],
        ignore_index=True,
    )
    hard_case_features = build_feature_frame(
        hard_cases["url"].astype(str).tolist(),
        label=0,
    )[feature_columns]
    _print_threshold_report(
        "Constructed hard-case validation set",
        model,
        hard_case_features,
        hard_cases["label"].astype(int),
    )


if __name__ == "__main__":
    main()
