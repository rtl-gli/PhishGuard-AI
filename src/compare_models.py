import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


DATA_PATH = "data/raw/phishtrap_full.csv"

FEATURE_COLUMNS = [
    "url_length",
    "hyphen_count",
    "digit_count",
    "subdomain_count",
    "trusted_tld",
    "protocol_exists",
    "special_char_count",
    "entropy",
    "path_depth",
    "domain_length",
    "is_domain_ip",
    "has_at_symbol",
    "has_double_slash_redirect",
    "tld_length",
    "query_param_count",
    "path_length",
]


def main():
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURE_COLUMNS]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, random_state=42)),
        ]),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=8,
            random_state=42,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            random_state=42,
            n_jobs=-1,
        ),
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    print("=== Model Comparison ===\n")

    for name, model in models.items():
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)[:, 1]

        cv_scores = cross_val_score(
            model,
            X,
            y,
            cv=cv,
            scoring="accuracy",
        )

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)
        roc_auc = roc_auc_score(y_test, probabilities)

        false_negatives = ((y_test == 1) & (predictions == 0)).sum()

        print(f"{name}")
        print("-" * len(name))
        print(f"Test accuracy:       {accuracy:.4f}")
        print(f"Precision:            {precision:.4f}")
        print(f"Recall:               {recall:.4f}")
        print(f"F1 score:             {f1:.4f}")
        print(f"ROC-AUC:              {roc_auc:.4f}")
        print(f"False negatives:      {false_negatives}")
        print(f"CV accuracy:          {cv_scores.mean():.4f}")
        print(f"CV standard deviation:{cv_scores.std():.4f}")
        print()


if __name__ == "__main__":
    main()