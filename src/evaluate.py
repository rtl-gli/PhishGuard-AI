from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split


DATA_PATH = Path("data/raw/phishtrap_full.csv")
MODEL_PATH = Path("model/phishing_model.pkl")

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


# Load dataset
df = pd.read_csv(DATA_PATH)

X = df[FEATURE_COLUMNS]
y = df["label"]


# Recreate the same test split used during training
_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


# Load trained model
model_data = joblib.load(MODEL_PATH)
model = model_data["model"]


# Generate predictions
y_pred = model.predict(X_test)


# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
matrix = confusion_matrix(y_test, y_pred)


print("PhishGuard AI - Model Evaluation")
print("────────────────────────────────")

print(f"\nModel: Decision Tree")
print(f"Max depth: {model.get_params()['max_depth']}")
print(f"Test samples: {len(X_test)}")
print(f"Accuracy: {accuracy:.2%}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(matrix)

# False negatives:
# Actual phishing URLs predicted as legitimate.
false_negatives = matrix[1][0]

print(
    f"\nPhishing false negatives: "
    f"{false_negatives}"
)

print(
    f"Phishing recall: "
    f"{matrix[1][1] / (matrix[1][1] + matrix[1][0]):.2%}"
)