from pathlib import Path

import pandas as pd

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


DATA_PATH = Path("data/raw/phishtrap_full.csv")

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


df = pd.read_csv(DATA_PATH)

X = df[FEATURE_COLUMNS]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


depths = [3, 5, 8, 12, None]


print("=" * 75)
print("DECISION TREE DEPTH COMPARISON")
print("=" * 75)

print(
    f"{'Depth':<10}"
    f"{'Train Acc.':<15}"
    f"{'Test Acc.':<15}"
    f"{'Precision':<15}"
    f"{'Recall':<15}"
    f"{'F1':<10}"
    f"{'False Neg.':<12}"
)

print("-" * 75)


for depth in depths:

    model = DecisionTreeClassifier(
        max_depth=depth,
        random_state=42,
    )

    model.fit(X_train, y_train)

    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)

    train_accuracy = accuracy_score(
        y_train,
        train_predictions,
    )

    test_accuracy = accuracy_score(
        y_test,
        test_predictions,
    )

    precision = precision_score(
        y_test,
        test_predictions,
        pos_label=1,
    )

    recall = recall_score(
        y_test,
        test_predictions,
        pos_label=1,
    )

    f1 = f1_score(
        y_test,
        test_predictions,
        pos_label=1,
    )

    false_negatives = (
        (y_test == 1) & (test_predictions == 0)
    ).sum()

    depth_name = (
        "None"
        if depth is None
        else str(depth)
    )

    print(
        f"{depth_name:<10}"
        f"{train_accuracy:<15.2%}"
        f"{test_accuracy:<15.2%}"
        f"{precision:<15.2%}"
        f"{recall:<15.2%}"
        f"{f1:<10.2%}"
        f"{false_negatives:<12}"
    )