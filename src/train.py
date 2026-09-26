import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from src.hard_cases import build_feature_frame, generate_complex_legitimate_urls
from src.project import (
    BASE_FEATURE_COLUMNS,
    CANDIDATE_MODEL_PATH,
    DATASET_REVISION,
    load_dataset_split,
)

train_df = load_dataset_split("train")
validation_df = load_dataset_split("val")
test_df = load_dataset_split("test")

model_features = BASE_FEATURE_COLUMNS
X_train = train_df[model_features]
y_train = train_df["label"]
hard_negative_urls = generate_complex_legitimate_urls(
    train_df.loc[train_df["label"] == 0, "url"],
)
hard_negatives = build_feature_frame(hard_negative_urls, label=0)
X_train_augmented = pd.concat(
    [X_train, hard_negatives[model_features]],
    ignore_index=True,
)
y_train_augmented = pd.concat(
    [y_train, hard_negatives["label"]],
    ignore_index=True,
)

X_validation = validation_df[model_features]
y_validation = validation_df["label"]
X_test = test_df[model_features]
y_test = test_df["label"]


model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train_augmented, y_train_augmented)
print(f"Training rows before augmentation: {len(X_train)}")
print(f"Generated legitimate hard negatives: {len(hard_negatives)}")

for split_name, features, labels in (
    ("Validation", X_validation, y_validation),
    ("Test", X_test, y_test),
):
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, list(model.classes_).index(1)]

    print(f"=== {split_name} results ===")
    print(f"Accuracy: {accuracy_score(labels, predictions):.2%}")
    print(f"ROC-AUC: {roc_auc_score(labels, probabilities):.4f}")
    print(classification_report(labels, predictions, digits=4))
    print("Confusion Matrix (actual rows, predicted columns):")
    print(confusion_matrix(labels, predictions, labels=[0, 1]))

joblib.dump(
    {
        "model": model,
        "features": model_features,
        "training_rows": len(X_train_augmented),
        "hard_negative_rows": len(hard_negatives),
        "dataset_revision": DATASET_REVISION,
        "hard_negative_domains": 200,
        "hard_negative_templates_per_domain": 5,
    },
    CANDIDATE_MODEL_PATH,
)

print(f"\nCandidate model saved to: {CANDIDATE_MODEL_PATH}")