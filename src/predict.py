import joblib
import pandas as pd
from pathlib import Path

from src.features import clean_url, extract_features


MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "phishing_model.pkl"
MEDIUM_RISK_THRESHOLD = 0.40
HIGH_RISK_THRESHOLD = 0.75


def get_indicators(features):
    indicators = []

    if features["url_length"] > 75:
        indicators.append("Unusually long URL")

    if features["hyphen_count"] >= 3:
        indicators.append("Multiple hyphens in URL")

    if features["digit_count"] >= 5:
        indicators.append("Large number of digits")

    if features["subdomain_count"] >= 3:
        indicators.append("Multiple subdomains")

    if features["is_domain_ip"] == 1:
        indicators.append("IP address used instead of a domain name")

    if features["has_at_symbol"] == 1:
        indicators.append("@ symbol present in URL")

    if features["has_double_slash_redirect"] == 1:
        indicators.append("Possible redirect pattern")

    if features["query_param_count"] >= 4:
        indicators.append("Large number of query parameters")

    if features["path_depth"] >= 4:
        indicators.append("Deep URL path")

    if features["entropy"] > 4.5:
        indicators.append("High URL character randomness")

    return indicators


def predict_url(url):
    """Predict whether a URL is likely legitimate or phishing."""

    cleaned_url = clean_url(url)

    model_data = joblib.load(MODEL_PATH)

    model = model_data["model"]
    feature_columns = model_data["features"]

    features = extract_features(cleaned_url)

    data = pd.DataFrame(
        [[features[column] for column in feature_columns]],
        columns=feature_columns,
    )

    prediction = model.predict(data)[0]

    probabilities = model.predict_proba(data)[0]

    phishing_probability = probabilities[
        list(model.classes_).index(1)
    ]

    if phishing_probability >= HIGH_RISK_THRESHOLD:
        risk_level = "HIGH"
    elif phishing_probability >= MEDIUM_RISK_THRESHOLD:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    indicators = get_indicators(features)

    return {
        "url": cleaned_url,
        "prediction": int(prediction),
        "phishing_probability": float(phishing_probability),
        "risk_level": risk_level,
        "indicators": indicators,
        "features": features,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src\\predict.py <URL>")
        raise SystemExit(1)

    url = sys.argv[1]

    result = predict_url(url)

    print("\nPhishGuard AI")
    print("----------------------------")
    print(f"URL: {result['url']}")
    print(f"Risk level: {result['risk_level']}")
    print(f"Model risk score: {result['phishing_probability']:.2%}")

    if result["prediction"] == 1:
        print("Classification: Potentially phishing")
    else:
        print("Classification: Likely legitimate")

    print("\nSecurity indicators:")

    if result["indicators"]:
        for indicator in result["indicators"]:
            print(f"- {indicator}")
    else:
        print("- No obvious suspicious URL characteristics detected")