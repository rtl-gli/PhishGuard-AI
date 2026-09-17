import joblib
import pandas as pd

from features import extract_features


MODEL_PATH = "model/phishing_model.pkl"


FEATURE_NAMES = {
    "url_length": "URL length",
    "hyphen_count": "Hyphens",
    "digit_count": "Digits",
    "subdomain_count": "Subdomains",
    "trusted_tld": "Trusted TLD",
    "protocol_exists": "Protocol",
    "special_char_count": "Special characters",
    "entropy": "URL entropy",
    "path_depth": "Path depth",
    "domain_length": "Domain length",
    "is_domain_ip": "IP address domain",
    "has_at_symbol": "@ symbol",
    "has_double_slash_redirect": "Double-slash redirect",
    "tld_length": "TLD length",
    "query_param_count": "Query parameters",
    "path_length": "Path length",
}


def explain_url(url):
    """Explain a URL prediction using standardised feature contributions."""

    model_data = joblib.load(MODEL_PATH)

    model = model_data["model"]
    feature_columns = model_data["features"]

    features = extract_features(url)

    data = pd.DataFrame(
        [[features[column] for column in feature_columns]],
        columns=feature_columns,
    )

    prediction = model.predict(data)[0]

    probabilities = model.predict_proba(data)[0]

    phishing_probability = probabilities[
        list(model.classes_).index(1)
    ]

    # Get the two stages of the pipeline.
    scaler = model.named_steps["scaler"]
    classifier = model.named_steps["classifier"]

    # Standardise the feature values.
    scaled_features = scaler.transform(data)[0]

    # Calculate each feature's contribution.
    contributions = []

    for feature, value, coefficient in zip(
        feature_columns,
        scaled_features,
        classifier.coef_[0],
    ):
        contribution = value * coefficient

        contributions.append(
            {
                "feature": feature,
                "value": features[feature],
                "contribution": contribution,
            }
        )

    # Sort from strongest phishing influence to strongest
    # legitimate influence.
    contributions.sort(
        key=lambda item: abs(item["contribution"]),
        reverse=True,
    )

    return {
        "url": url,
        "prediction": int(prediction),
        "phishing_probability": float(phishing_probability),
        "contributions": contributions,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src\\explain.py <URL>")
        raise SystemExit(1)

    url = sys.argv[1]

    result = explain_url(url)

    print(f"URL: {result['url']}")
    print(
        f"Phishing probability: "
        f"{result['phishing_probability']:.2%}"
    )

    if result["prediction"] == 1:
        print("Prediction: Potentially phishing")
    else:
        print("Prediction: Likely legitimate")

    print("\nKey model contributions:")

    for item in result["contributions"][:5]:

        if item["contribution"] > 0:
            direction = "phishing"
        else:
            direction = "legitimate"

        name = FEATURE_NAMES.get(
            item["feature"],
            item["feature"],
        )

        print(
            f"- {name}: "
            f"{item['contribution']:+.3f} "
            f"({direction})"
        )