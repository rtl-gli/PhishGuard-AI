from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd


MODEL_PATH = Path("model/phishing_model.pkl")
OUTPUT_PATH = Path("feature_importance.png")


model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
feature_columns = model_data["features"]


importance = pd.DataFrame(
    {
        "feature": feature_columns,
        "importance": model.feature_importances_,
    }
)


importance = importance.sort_values(
    "importance",
    ascending=True,
)


print("PhishGuard AI - Feature Importance")
print("──────────────────────────────────")

print("\nFeature importance:")

for _, row in importance.sort_values(
    "importance",
    ascending=False,
).iterrows():

    print(
        f"{row['feature']:<30}"
        f"{row['importance']:.4f}"
    )


plt.figure(figsize=(10, 7))

plt.barh(
    importance["feature"],
    importance["importance"],
)

plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("PhishGuard AI - Decision Tree Feature Importance")

plt.tight_layout()

plt.savefig(
    OUTPUT_PATH,
    dpi=150,
)

print(f"\nChart saved to: {OUTPUT_PATH}")