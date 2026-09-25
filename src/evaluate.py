import joblib
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from src.project import MODEL_PATH, load_dataset


def main():
    # Load model
    model_data = joblib.load(MODEL_PATH)
    model = model_data["model"]
    feature_columns = model_data["features"]

    # Load dataset
    df = load_dataset()

    X = df[feature_columns]
    y = df["label"]

    print("=== Cross-validation ===")

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    cv_scores = cross_val_score(
        model,
        X,
        y,
        cv=cv,
        scoring="accuracy",
    )

    print(f"Fold accuracies: {[round(score, 4) for score in cv_scores]}")
    print(f"Mean accuracy: {cv_scores.mean():.4f}")
    print(f"Standard deviation: {cv_scores.std():.4f}")

    # Train/test evaluation
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    print("\n=== Test-set evaluation ===")

    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, probabilities):.4f}")

    print("\nClassification report:")
    print(classification_report(y_test, predictions))

    print("Confusion matrix:")
    print(confusion_matrix(y_test, predictions))


if __name__ == "__main__":
    main()