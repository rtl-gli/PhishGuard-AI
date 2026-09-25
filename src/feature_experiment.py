import pandas as pd

from sklearn.metrics import accuracy_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from src.project import FEATURE_COLUMNS, load_dataset


df = load_dataset()

X = df[FEATURE_COLUMNS]
y = df["label"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


def evaluate_model(name, features):

    model = DecisionTreeClassifier(
        max_depth=8,
        random_state=42,
    )

    model.fit(
        X_train[features],
        y_train,
    )

    predictions = model.predict(
        X_test[features]
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    recall = recall_score(
        y_test,
        predictions,
        pos_label=1,
    )

    f1 = f1_score(
        y_test,
        predictions,
        pos_label=1,
    )

    print(f"\n{name}")
    print("────────────────────────")
    print(f"Features: {len(features)}")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Phishing recall: {recall:.2%}")
    print(f"Phishing F1: {f1:.2%}")


evaluate_model(
    "All features",
    FEATURE_COLUMNS,
)


reduced_features = [
    feature
    for feature in FEATURE_COLUMNS
    if feature != "url_length"
]


evaluate_model(
    "Without URL length",
    reduced_features,
)
