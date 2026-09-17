import joblib
import pandas as pd

from features import extract_features


MODEL_PATH = "model/phishing_model.pkl"


# Load the trained model package
model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
feature_columns = model_data["features"]


def predict_url(url):
    """Predict whether a URL is legitimate or phishing."""

    features = extract_features(url)

    # Ensure features are supplied in the same order used during training
    data = pd.DataFrame(
        [[features[column] for column in feature_columns]],
        columns=feature_columns,
    )

    prediction = model.predict(data)[0]
    probability = model.predict_proba(data)[0]

    phishing_probability = probability[
        list(model.classes_).index(1)
    ]

    return {
        "url": url,
        "prediction": int(prediction),
        "phishing_probability": float(phishing_probability),
        "features": features,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src\\predict.py <URL>")
        raise SystemExit(1)

    url = sys.argv[1]

    result = predict_url(url)

    print(f"URL: {result['url']}")
    print(f"Prediction: {result['prediction']}")

    print(
        f"Phishing probability: "
        f"{result['phishing_probability']:.2%}"
    )