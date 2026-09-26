import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from src.hard_cases import build_feature_frame, generate_complex_legitimate_urls
from src.domains import registrable_domain
from src.project import BASE_FEATURE_COLUMNS, FEATURE_COLUMNS, load_dataset_split


def _augmented_training_data(
    source: pd.DataFrame,
    feature_columns: list[str],
    add_hard_negatives: bool,
) -> tuple[pd.DataFrame, pd.Series, int]:
    features = source[feature_columns]
    labels = source["label"]
    if not add_hard_negatives:
        return features, labels, 0

    hard_urls = generate_complex_legitimate_urls(
        source.loc[source["label"] == 0, "url"],
    )
    hard_cases = build_feature_frame(hard_urls, label=0)
    return (
        pd.concat(
            [features, hard_cases[feature_columns]],
            ignore_index=True,
        ),
        pd.concat([labels, hard_cases["label"]], ignore_index=True),
        len(hard_cases),
    )


def _cross_validate(
    estimator,
    training_data: pd.DataFrame,
    feature_columns: list[str],
    add_hard_negatives: bool,
    folds: StratifiedGroupKFold,
) -> list[float]:
    scores = []
    groups = training_data["url"].map(registrable_domain)
    for train_indices, validation_indices in folds.split(
        training_data[feature_columns],
        training_data["label"],
        groups,
    ):
        fold_train = training_data.iloc[train_indices]
        fold_validation = training_data.iloc[validation_indices]
        X_train, y_train, _ = _augmented_training_data(
            fold_train,
            feature_columns,
            add_hard_negatives,
        )
        fold_model = clone(estimator)
        fold_model.fit(X_train, y_train)
        scores.append(
            accuracy_score(
                fold_validation["label"],
                fold_model.predict(fold_validation[feature_columns]),
            )
        )
    return scores


def main():
    train_df = load_dataset_split("train")
    validation_df = load_dataset_split("val")
    test_df = load_dataset_split("test")

    models = [
        (
            "Logistic Regression (26 features)",
            Pipeline([
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, random_state=42)),
            ]),
            FEATURE_COLUMNS,
            False,
        ),
        (
            "Decision Tree (26 features)",
            DecisionTreeClassifier(max_depth=8, random_state=42),
            FEATURE_COLUMNS,
            False,
        ),
        (
            "Random Forest (16 features)",
            RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                random_state=42,
                n_jobs=-1,
            ),
            BASE_FEATURE_COLUMNS,
            False,
        ),
        (
            "Random Forest (16 features + hard negatives)",
            RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                random_state=42,
                n_jobs=-1,
            ),
            BASE_FEATURE_COLUMNS,
            True,
        ),
        (
            "Random Forest (26 features)",
            RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                random_state=42,
                n_jobs=-1,
            ),
            FEATURE_COLUMNS,
            False,
        ),
        (
            "Random Forest (26 features + hard negatives)",
            RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                random_state=42,
                n_jobs=-1,
            ),
            FEATURE_COLUMNS,
            True,
        ),
    ]

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    print("=== Model and feature comparison ===\n")

    for name, estimator, feature_columns, add_hard_negatives in models:
        X_train, y_train, hard_negative_count = _augmented_training_data(
            train_df,
            feature_columns,
            add_hard_negatives,
        )
        estimator.fit(X_train, y_train)
        cv_scores = _cross_validate(
            estimator,
            train_df,
            feature_columns,
            add_hard_negatives,
            cv,
        )

        print(name)
        print("-" * len(name))
        print(f"Training hard negatives: {hard_negative_count}")
        print(
            f"5-fold CV accuracy: {np.mean(cv_scores):.4f} "
            f"+/- {np.std(cv_scores):.4f}"
        )

        for split_name, split_df in (
            ("Validation", validation_df),
            ("Test", test_df),
        ):
            labels = split_df["label"]
            features = split_df[feature_columns]
            predictions = estimator.predict(features)
            probabilities = estimator.predict_proba(features)[
                :, list(estimator.classes_).index(1)
            ]
            tn, fp, fn, tp = confusion_matrix(
                labels,
                predictions,
                labels=[0, 1],
            ).ravel()
            print(
                f"{split_name}: accuracy={accuracy_score(labels, predictions):.4f} "
                f"precision={precision_score(labels, predictions, zero_division=0):.4f} "
                f"recall={recall_score(labels, predictions, zero_division=0):.4f} "
                f"F1={f1_score(labels, predictions, zero_division=0):.4f} "
                f"ROC-AUC={roc_auc_score(labels, probabilities):.4f} "
                f"FP={fp} FN={fn}"
            )
        print()


if __name__ == "__main__":
    main()
