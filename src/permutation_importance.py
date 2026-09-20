from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split


DATA_PATH = Path("data/raw/phishtrap_full.csv")
MODEL_PATH = Path("model/phishing_model.pkl")
OUTPUT_PATH = Path("permutation_importance.png")


df = pd.read_csv(DATA_PATH)

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
feature_columns = model_data["features"]

X = df[feature_columns]
y = df["label"]


_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


results = permutation_importance(
    model,
    X_test,
    y_test,
    n_repeats=10,
    random_state=42,
    scoring="f1",
)


importance = pd.DataFrame(
    {
        "feature": feature_columns,
        "importance": results.importances_mean,
        "std": results.importances_std,
    }
)

importance = importance.sort_values(
    "importance",
    ascending=False,
)


print("PhishGuard AI - Permutation Importance")
print("──────────────────────────────────────")

print("\nFeature importance:")

for _, row in importance.iterrows():
    print(
        f"{row['feature']:<30}"
        f"{row['importance']:.4f}"
        f" ± {row['std']:.4f}"
    )


plot_data = importance.sort_values(
    "importance",
    ascending=True,
)


plt.figure(figsize=(10, 7))

plt.barh(
    plot_data["feature"],
    plot_data["importance"],
)

plt.xlabel("Mean decrease in F1 score")
plt.ylabel("Feature")
plt.title("PhishGuard AI - Permutation Feature Importance")

plt.tight_layout()

plt.savefig(
    OUTPUT_PATH,
    dpi=150,
)

print(f"\nChart saved to: {OUTPUT_PATH}")